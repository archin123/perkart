from decimal import Decimal
from products.models import Product, Offer


class Cart:
    """
    Session-based shopping cart for PerkCart.
    """
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart
        self.coupon_code = self.session.get('coupon_code', None)

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.corporate_price),
                'original_price': str(product.original_price),
                'name': product.name,
                'image_url': product.image_url,
                'sku': product.sku,
            }
        
        if override_quantity:
            self.cart[product_id]['quantity'] = max(1, int(quantity))
        else:
            self.cart[product_id]['quantity'] += max(1, int(quantity))

        # Check stock bounds
        if product.stock_quantity > 0:
            if self.cart[product_id]['quantity'] > product.stock_quantity:
                self.cart[product_id]['quantity'] = product.stock_quantity

        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def update_quantity(self, product, quantity):
        product_id = str(product.id)
        if product_id in self.cart:
            qty = int(quantity)
            if qty <= 0:
                self.remove(product)
            else:
                if product.stock_quantity > 0 and qty > product.stock_quantity:
                    qty = product.stock_quantity
                self.cart[product_id]['quantity'] = qty
                self.save()

    def apply_coupon(self, code):
        code = code.strip().upper()
        try:
            offer = Offer.objects.get(code=code, is_active=True)
            self.session['coupon_code'] = offer.code
            self.coupon_code = offer.code
            self.session.modified = True
            return True, f"Coupon '{offer.code}' applied successfully! Enjoy {offer.discount_percent}% extra corporate discount."
        except Offer.DoesNotExist:
            return False, "Invalid or expired corporate coupon code."

    def remove_coupon(self):
        if 'coupon_code' in self.session:
            del self.session['coupon_code']
            self.coupon_code = None
            self.session.modified = True

    def get_applied_offer(self):
        if self.coupon_code:
            try:
                return Offer.objects.get(code=self.coupon_code, is_active=True)
            except Offer.DoesNotExist:
                return None
        return None

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        product_dict = {str(p.id): p for p in products}

        for item_id, item_data in list(self.cart.items()):
            product = product_dict.get(item_id)
            if not product:
                continue
            item = item_data.copy()
            item['product'] = product
            item['price'] = Decimal(item['price'])
            item['original_price'] = Decimal(item.get('original_price', item['price']))
            item['total_price'] = item['price'] * item['quantity']
            item['item_savings'] = (item['original_price'] - item['price']) * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_subtotal_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def get_total_savings(self):
        # Savings from corporate discount compared to original retail
        savings = Decimal('0.00')
        for item in self:
            savings += item['item_savings']
        savings += self.get_discount_amount()
        return savings

    def get_discount_amount(self):
        subtotal = self.get_subtotal_price()
        offer = self.get_applied_offer()
        if offer and subtotal >= offer.min_order_amount:
            discount = (subtotal * Decimal(offer.discount_percent)) / Decimal('100')
            if offer.max_discount_amount:
                discount = min(discount, offer.max_discount_amount)
            return round(discount, 2)
        return Decimal('0.00')

    def get_total_price(self):
        subtotal = self.get_subtotal_price()
        discount = self.get_discount_amount()
        return max(Decimal('0.00'), subtotal - discount)

    def clear(self):
        del self.session['cart']
        if 'coupon_code' in self.session:
            del self.session['coupon_code']
        self.session.modified = True

    def save(self):
        self.session.modified = True
