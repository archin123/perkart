from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import ProductCategory, Product, Offer, Wishlist


class ProductsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='buyer',
            email='buyer@corp.internal',
            password='Password@123'
        )
        self.category = ProductCategory.objects.create(
            name='Computing',
            slug='computing',
            icon='bi-laptop'
        )
        self.product = Product.objects.create(
            category=self.category,
            name='PerkBook Test Pro',
            slug='perkbook-test-pro',
            sku='TEST-001',
            description='Test laptop description',
            specs={'RAM': '16GB', 'Storage': '512GB'},
            original_price=Decimal('100000.00'),
            corporate_price=Decimal('70000.00'),
            stock_quantity=10,
            image_url='https://example.com/test.jpg',
            is_active=True
        )
        self.offer = Offer.objects.create(
            code='SAVE10',
            title='10% Off Test',
            description='Test offer description',
            discount_percent=10,
            is_active=True
        )

    def test_product_list_and_detail(self):
        resp = self.client.get(reverse('products:product_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'PerkBook Test Pro')

        resp_detail = self.client.get(reverse('products:product_detail', kwargs={'slug': 'perkbook-test-pro'}))
        self.assertEqual(resp_detail.status_code, 200)
        self.assertContains(resp_detail, '70000')

    def test_category_filter(self):
        resp = self.client.get(reverse('products:product_list') + '?category=computing')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'PerkBook Test Pro')

    def test_price_savings_calculation(self):
        self.assertEqual(self.product.discount_percent, 30)
        self.assertEqual(self.product.savings, Decimal('30000.00'))

    def test_wishlist_toggle(self):
        self.client.login(username='buyer', password='Password@123')
        # Add to wishlist
        resp = self.client.post(
            reverse('products:wishlist_toggle', kwargs={'product_id': self.product.id}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Wishlist.objects.filter(user=self.user, product=self.product).exists())

        # Remove from wishlist
        resp2 = self.client.post(
            reverse('products:wishlist_toggle', kwargs={'product_id': self.product.id}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp2.status_code, 200)
        self.assertFalse(Wishlist.objects.filter(user=self.user, product=self.product).exists())
