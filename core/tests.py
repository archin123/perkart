from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from products.models import ProductCategory, Product
from .models import Feedback


class CoreTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = ProductCategory.objects.create(name='Displays', slug='displays')
        self.product = Product.objects.create(
            category=self.category,
            name='UltraDisplay 4K',
            slug='ultradisplay-4k',
            sku='MON-TEST-01',
            description='Test 4K monitor',
            original_price=Decimal('40000.00'),
            corporate_price=Decimal('28000.00'),
            image_url='https://example.com/mon.jpg',
            is_featured=True,
            is_active=True
        )

    def test_homepage_view(self):
        resp = self.client.get(reverse('core:home'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'PerkCart')
        self.assertContains(resp, 'UltraDisplay 4K')

    def test_global_search_view(self):
        resp = self.client.get(reverse('core:global_search') + '?q=UltraDisplay')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'UltraDisplay 4K')

    def test_feedback_submission(self):
        resp = self.client.post(reverse('core:feedback'), {
            'name': 'Rahul Verma',
            'email': 'rahul@partner.internal',
            'company_name': 'Partner Tech',
            'category': 'EXPERIENCE',
            'rating': '5',
            'subject': 'Smooth shopping experience',
            'message': 'Fast checkout and clear corporate savings breakdown.'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Feedback.objects.filter(email='rahul@partner.internal').exists())

    def test_health_check_endpoint(self):
        resp = self.client.get(reverse('core:health_check'))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['database'], 'connected')
        self.assertIn('timestamp', data)

    def test_system_status_view(self):
        resp = self.client.get(reverse('core:system_status'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'System Operational Status')
