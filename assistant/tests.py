import json
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from products.models import ProductCategory, Product, Offer
from faq.models import FAQCategory, FAQ
from troubleshooting.models import ErrorCode
from .engine import retrieve_context, extract_price_constraint, process_assistant_query
from .models import AIConversation, AIMessage


class AssistantTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='emp_ai',
            email='emp@ai.internal',
            password='Password@123'
        )
        self.category = ProductCategory.objects.create(name='Laptops', slug='laptops')
        self.product = Product.objects.create(
            category=self.category,
            name='PerkBook Horizon AI',
            slug='perkbook-horizon-ai',
            sku='PB-HORIZON-01',
            tagline='Lightweight enterprise laptop',
            description='Flagship mobile productivity with OLED display',
            specs={'Processor': 'Intel Core Ultra 7', 'RAM': '16GB'},
            original_price=Decimal('120000.00'),
            corporate_price=Decimal('85000.00'),
            stock_quantity=15,
            image_url='https://example.com/laptop.jpg',
            is_active=True
        )
        self.offer = Offer.objects.create(
            code='AIWELCOME',
            title='AI Welcome',
            description='Exclusive AI launch discount',
            discount_percent=15,
            is_active=True
        )
        self.faq_cat = FAQCategory.objects.create(name='Security', slug='security')
        self.faq = FAQ.objects.create(
            category=self.faq_cat,
            question='How is corporate privacy guaranteed?',
            answer='Data is strictly partitioned with zero public model training.',
            is_active=True
        )
        self.err = ErrorCode.objects.create(
            code='API-001',
            title='Temporary Interruption',
            category='API',
            severity='CRITICAL',
            description='AI service timeout',
            troubleshooting_steps='Check internet connection and refresh.',
            preventive_recommendations='System fails over safely to search-based fallback.'
        )

    def test_price_constraint_extraction(self):
        self.assertEqual(extract_price_constraint("find laptops under 90000"), 90000.0)
        self.assertEqual(extract_price_constraint("show ultrabooks under 1 lakh"), 100000.0)
        self.assertEqual(extract_price_constraint("budget below 50k"), 50000.0)

    def test_rag_retrieval_pipeline(self):
        retrieved, sources = retrieve_context("PerkBook Horizon", user=self.user)
        self.assertEqual(len(retrieved['products']), 1)
        self.assertEqual(retrieved['products'][0]['name'], 'PerkBook Horizon AI')
        self.assertTrue(any(s['type'] == 'Product' for s in sources))

    def test_search_based_fallback_engine(self):
        # Process query with no API key -> should use Search-Based Fallback Engine
        result = process_assistant_query("find laptops under 90000", user=self.user)
        self.assertIn("Search-Based Fallback Engine", result['engine'])
        self.assertIn("PerkBook Horizon AI", result['content'])
        self.assertTrue(len(result['sources']) > 0)

    def test_assistant_api_endpoint(self):
        self.client.login(username='emp_ai', password='Password@123')
        payload = {'query': 'What is error API-001?'}
        resp = self.client.post(
            reverse('assistant:api_chat'),
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('API-001', data['content'])

        # Verify conversation and messages stored in DB
        conv = AIConversation.objects.filter(user=self.user).first()
        self.assertIsNotNone(conv)
        self.assertEqual(conv.messages.count(), 2)  # User + Assistant
