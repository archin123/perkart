from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from products.models import Product, Offer
from .cart import Cart
from .models import Order, OrderItem
from troubleshooting.models import ErrorCode, AppErrorLog


def cart_detail_view(request):
    cart = Cart(request)
    applied_offer = cart.get_applied_offer()

    return render(request, 'cart/cart_detail.html', {
        'cart': cart,
        'applied_offer': applied_offer,
    })


def cart_add_view(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    if quantity <= 0:
        messages.error(request, "Invalid quantity specified (Code: CART-002). Quantity must be at least 1.")
        return redirect('products:product_detail', slug=product.slug)

    if product.stock_quantity < 1:
        messages.error(
            request,
            f"'{product.name}' is currently out of stock (Code: CART-001). Please check back soon or add it to your wishlist."
        )
        return redirect('products:product_detail', slug=product.slug)

    cart.add(product=product, quantity=quantity)
    messages.success(request, f"Added {quantity}x '{product.name}' to your corporate cart.")

    if request.POST.get('buy_now') == '1':
        return redirect('cart:checkout')

    return redirect('cart:cart_detail')


def cart_update_view(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    if quantity < 0:
        messages.error(request, "Invalid quantity (Code: CART-002). Quantity cannot be negative.")
        return redirect('cart:cart_detail')

    if quantity > product.stock_quantity:
        messages.warning(
            request,
            f"Requested {quantity} units exceeds available stock ({product.stock_quantity}) for '{product.name}'. Quantity adjusted to maximum available."
        )
        quantity = product.stock_quantity

    cart.update_quantity(product=product, quantity=quantity)
    messages.info(request, f"Updated '{product.name}' quantity.")
    return redirect('cart:cart_detail')


def cart_remove_view(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f"Removed '{product.name}' from your cart.")
    return redirect('cart:cart_detail')


def cart_apply_coupon_view(request):
    if request.method == 'POST':
        cart = Cart(request)
        code = request.POST.get('coupon_code', '').strip().upper()
        if not code:
            messages.error(request, "Please enter a corporate coupon code.")
            return redirect('cart:cart_detail')

        success, msg = cart.apply_coupon(code)
        if success:
            messages.success(request, msg)
        else:
            messages.error(
                request,
                f"{msg} (Error Code: DISC-001). Refer to Troubleshooting for active coupon assistance."
            )
    return redirect('cart:cart_detail')


def cart_remove_coupon_view(request):
    cart = Cart(request)
    cart.remove_coupon()
    messages.info(request, "Corporate coupon removed.")
    return redirect('cart:cart_detail')


@login_required
def checkout_view(request):
    cart = Cart(request)

    if len(cart) == 0:
        messages.warning(request, "Your shopping cart is currently empty.")
        return redirect('products:product_list')

    profile = getattr(request.user, 'profile', None)

    # Note: Pending users can experience the demonstration checkout or be alerted to their status
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        corporate_email = request.POST.get('corporate_email', '').strip()
        phone = request.POST.get('phone', '').strip()
        shipping_address = request.POST.get('shipping_address', '').strip()
        city = request.POST.get('city', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        payment_method = request.POST.get('payment_method', 'SIMULATED_CORP_PAYROLL')

        # Server-side validation
        if not (full_name and corporate_email and phone and shipping_address and city and postal_code):
            messages.error(
                request,
                "All shipping and employee contact fields are required (Code: PAY-001)."
            )
            return render(request, 'cart/checkout.html', {
                'cart': cart,
                'profile': profile,
                'form_data': request.POST,
            })

        # Recalculate all amounts on server for security
        subtotal = cart.get_subtotal_price()
        discount_amount = cart.get_discount_amount()
        shipping_cost = Decimal('0.00')  # Free corporate shipping privilege
        total_amount = max(Decimal('0.00'), subtotal - discount_amount + shipping_cost)
        applied_offer = cart.get_applied_offer()

        # Create Order
        order = Order.objects.create(
            user=request.user,
            status='PROCESSING',
            subtotal=subtotal,
            discount_amount=discount_amount,
            coupon_code=applied_offer.code if applied_offer else '',
            shipping_cost=shipping_cost,
            total_amount=total_amount,
            full_name=full_name,
            corporate_email=corporate_email,
            phone=phone,
            shipping_address=shipping_address,
            city=city,
            postal_code=postal_code,
            company_name=profile.company_name if profile else '',
            employee_id=profile.employee_id if profile else '',
            payment_method=payment_method,
            payment_status='PAID',
        )

        # Create Order Items and decrease stock
        for item in cart:
            product = item['product']
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                price=item['price'],
                quantity=item['quantity'],
            )
            # Adjust inventory
            if product.stock_quantity >= item['quantity']:
                product.stock_quantity -= item['quantity']
                product.save()

        # Clear session cart
        cart.clear()

        messages.success(
            request,
            f"🎉 Congratulations {full_name}! Order #{order.order_number} confirmed with simulated corporate billing."
        )
        return redirect('cart:order_detail', order_number=order.order_number)

    # Initial GET form data prefilled from profile
    initial_data = {
        'full_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
        'corporate_email': (profile.corporate_email if profile and profile.corporate_email else request.user.email),
        'phone': profile.phone if profile else '',
        'shipping_address': profile.shipping_address if profile else '',
        'city': profile.city if profile else '',
        'postal_code': profile.postal_code if profile else '',
    }

    return render(request, 'cart/checkout.html', {
        'cart': cart,
        'profile': profile,
        'form_data': initial_data,
    })


@login_required
def order_list_view(request):
    """
    Shows authenticated user's order history with pagination.
    Strictly isolated to request.user.
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'cart/order_list.html', {'orders': orders})


@login_required
def order_detail_view(request, order_number):
    """
    Displays order details. Strictly verifies user ownership.
    If unauthorized user attempts access, logs error code ORDER-001 and raises 404.
    """
    try:
        order = Order.objects.get(order_number=order_number)
    except Order.DoesNotExist:
        messages.error(request, f"Order #{order_number} not found (Code: ORDER-001).")
        return redirect('cart:order_list')

    # Security check: User must own this order unless staff
    if order.user != request.user and not request.user.is_staff:
        # Record security incident
        AppErrorLog.objects.create(
            error_code='ORDER-001',
            user=request.user,
            path=request.path,
            method=request.method,
            ip_address=request.META.get('REMOTE_ADDR'),
            message=f"Unauthorized order access attempt: user '{request.user.username}' tried to access order #{order_number} belonging to '{order.user.username}'.",
            context_data="Order ownership isolation enforced."
        )
        messages.error(
            request,
            "Access Denied: You do not have authorization to view this order record (Code: ORDER-001)."
        )
        return redirect('cart:order_list')

    return render(request, 'cart/order_detail.html', {'order': order})
