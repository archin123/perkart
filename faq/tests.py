from django.test import TestCase, Client
from django.urls import reverse
from .models import FAQCategory, FAQ, FAQVote, UnansweredQuestion


class FAQTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = FAQCategory.objects.create(name='Delivery', slug='delivery', order=1)
        self.faq = FAQ.objects.create(
            category=self.category,
            question='How fast is corporate delivery?',
            answer='Expedited shipping takes 2-4 business days.',
            order=1,
            helpful_count=5
        )

    def test_faq_list_and_search(self):
        resp = self.client.get(reverse('faq:faq_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'How fast is corporate delivery?')

        # Search query
        search_resp = self.client.get(reverse('faq:faq_list') + '?q=delivery')
        self.assertEqual(search_resp.status_code, 200)
        self.assertContains(search_resp, 'Expedited shipping')

    def test_faq_ajax_helpful_voting(self):
        resp = self.client.post(
            reverse('faq:faq_vote', kwargs={'faq_id': self.faq.id}),
            {'vote_type': 'helpful'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['helpful_count'], 6)

    def test_submit_unanswered_question(self):
        resp = self.client.post(reverse('faq:faq_list'), {
            'submit_question': '1',
            'name': 'Pooja Nair',
            'email': 'pooja@company.com',
            'company_name': 'Tech Corp',
            'question': 'Can I order dual monitors with single invoice?'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(UnansweredQuestion.objects.filter(email='pooja@company.com').exists())
