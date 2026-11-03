from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from products.models import ProductCategory, Product, Offer
from .models import Order, OrderItem
from .cart import Cart


class CartAndOrderTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@corp.internal',
            password='Password@123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@corp.internal',
            password='Password@123'
        )
        self.category = ProductCategory.objects.create(name='Laptops', slug='laptops')
        self.product = Product.objects.create(
            category=self.category,
            name='Test Laptop',
            slug='test-laptop',
            sku='LAP-001',
            description='Test laptop',
            original_price=Decimal('100000.00'),
            corporate_price=Decimal('80000.00'),
            stock_quantity=5,
            image_url='https://example.com/lap.jpg',
            is_active=True
        )
        self.offer = Offer.objects.create(
            code='CORP10',
            title='10% Off',
            description='10% discount',
            discount_percent=10,
            is_active=True
        )

    def test_cart_add_and_quantity_validation(self):
        # Add 2 items
        resp = self.client.post(reverse('cart:cart_add', kwargs={'product_id': self.product.id}), {
            'quantity': 2
        })
        self.assertEqual(resp.status_code, 302)
        cart = self.client.session.get('cart')
        self.assertEqual(cart[str(self.product.id)]['quantity'], 2)

        # Quantity exceeding stock (stock is 5, request 10 -> caps at 5)
        self.client.post(reverse('cart:cart_update', kwargs={'product_id': self.product.id}), {
            'quantity': 10
        })
        cart = self.client.session.get('cart')
        self.assertEqual(cart[str(self.product.id)]['quantity'], 5)

    def test_coupon_discount_calculation(self):
        self.client.post(reverse('cart:cart_add', kwargs={'product_id': self.product.id}), {'quantity': 1})
        self.client.post(reverse('cart:cart_apply_coupon'), {'coupon_code': 'CORP10'})
        self.assertEqual(self.client.session.get('coupon_code'), 'CORP10')

    def test_checkout_and_order_creation(self):
        self.client.login(username='user1', password='Password@123')
        # Add product to cart
        self.client.post(reverse('cart:cart_add', kwargs={'product_id': self.product.id}), {'quantity': 1})

        # Submit checkout
        resp = self.client.post(reverse('cart:checkout'), {
            'full_name': 'User One',
            'corporate_email': 'user1@corp.internal',
            'phone': '+91 98765 00001',
            'shipping_address': 'DLF Phase 2 Cyber City',
            'city': 'Gurugram',
            'postal_code': '122002',
            'payment_method': 'SIMULATED_CORP_PAYROLL'
        })
        self.assertEqual(resp.status_code, 302)

        # Order created in database
        order = Order.objects.filter(user=self.user1).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.total_amount, Decimal('80000.00'))
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().product_name, 'Test Laptop')

        # Inventory decreased from 5 to 4
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 4)

    def test_strict_order_ownership_isolation(self):
        # Create order for user1
        order = Order.objects.create(
            user=self.user1,
            subtotal=Decimal('80000.00'),
            total_amount=Decimal('80000.00'),
            full_name='User One',
            corporate_email='user1@corp.internal',
            phone='9876543210',
            shipping_address='Street 1',
            city='City',
            postal_code='123456'
        )

        # Log in as user2 and attempt to access user1's order
        self.client.login(username='user2', password='Password@123')
        resp = self.client.get(reverse('cart:order_detail', kwargs={'order_number': order.order_number}))
        # Must be redirected / denied
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('cart:order_list'))

        # Log in as user1 and verify access is allowed
        self.client.login(username='user1', password='Password@123')
        resp_allowed = self.client.get(reverse('cart:order_detail', kwargs={'order_number': order.order_number}))
        self.assertEqual(resp_allowed.status_code, 200)
        self.assertContains(resp_allowed, order.order_number)
