from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Product, ProductCategory, Offer, Wishlist


def product_list_view(request):
    """
    Corporate catalog with filtering by category, search query,
    sorting, budget range, and pagination.
    """
    category_slug = request.GET.get('category', '')
    query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', 'featured')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    products = Product.objects.filter(is_active=True).select_related('category')
    selected_category = None

    if category_slug:
        selected_category = get_object_or_404(ProductCategory, slug=category_slug, is_active=True)
        products = products.filter(category=selected_category)

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(tagline__icontains=query) |
            Q(description__icontains=query) |
            Q(sku__icontains=query) |
            Q(category__name__icontains=query)
        )

    if min_price:
        try:
            products = products.filter(corporate_price__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            products = products.filter(corporate_price__lte=float(max_price))
        except ValueError:
            pass

    # Sorting options
    if sort_by == 'price_low':
        products = products.order_by('corporate_price')
    elif sort_by == 'price_high':
        products = products.order_by('-corporate_price')
    elif sort_by == 'rating':
        products = products.order_by('-rating')
    elif sort_by == 'discount':
        # Handled in Python or approximate by difference
        products = products.order_by('-original_price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    else:  # 'featured'
        products = products.order_by('-is_featured', '-created_at')

    # Wishlisted product IDs for current user
    user_wishlist_ids = set()
    if request.user.is_authenticated:
        user_wishlist_ids = set(
            Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    categories = ProductCategory.objects.filter(is_active=True).order_by('order')

    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'products/product_list.html', {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'selected_category': selected_category,
        'categories': categories,
        'query': query,
        'sort_by': sort_by,
        'min_price': min_price or '',
        'max_price': max_price or '',
        'total_count': paginator.count,
        'user_wishlist_ids': user_wishlist_ids,
    })


def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]

    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(user=request.user, product=product).exists()

    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'is_wishlisted': is_wishlisted,
    })


def offers_view(request):
    offers = Offer.objects.filter(is_active=True).order_by('-discount_percent')
    return render(request, 'products/offers.html', {'offers': offers})


@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product', 'product__category')
    return render(request, 'products/wishlist.html', {'wishlist_items': wishlist_items})


@login_required
def wishlist_toggle_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if not created:
        item.delete()
        action = 'removed'
        is_wishlisted = False
        message = f"Removed '{product.name}' from your wishlist."
    else:
        action = 'added'
        is_wishlisted = True
        message = f"Added '{product.name}' to your wishlist."

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        total_count = Wishlist.objects.filter(user=request.user).count()
        return JsonResponse({
            'status': 'success',
            'action': action,
            'is_wishlisted': is_wishlisted,
            'message': message,
            'total_count': total_count
        })

    messages.info(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))
