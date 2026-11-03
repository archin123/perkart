from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import ErrorCode, AppErrorLog


class TroubleshootingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin_tb',
            email='admin@tb.internal',
            password='Password@123'
        )
        self.error = ErrorCode.objects.create(
            code='CART-001',
            title='Product Unavailable',
            category='CART',
            severity='MEDIUM',
            description='The product is currently out of stock.',
            possible_causes='High demand during corporate sale cycle.',
            troubleshooting_steps='1. Adjust quantity or remove item from cart.',
            preventive_recommendations='Check stock availability badge before checkout.'
        )

    def test_error_code_list_and_search(self):
        resp = self.client.get(reverse('troubleshooting:error_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'CART-001')

        # Filter by severity
        sev_resp = self.client.get(reverse('troubleshooting:error_list') + '?severity=MEDIUM')
        self.assertEqual(sev_resp.status_code, 200)
        self.assertContains(sev_resp, 'CART-001')

    def test_error_code_detail(self):
        resp = self.client.get(reverse('troubleshooting:error_detail', kwargs={'code': 'CART-001'}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Product Unavailable')
        self.assertContains(resp, 'High demand during corporate sale cycle')

    def test_safe_error_simulator_admin_access(self):
        # Admin triggers simulation
        self.client.login(username='admin_tb', password='Password@123')
        resp = self.client.post(reverse('troubleshooting:simulate_error'), {
            'error_code': 'CART-001',
            'simulation_note': 'Automated unit test simulation'
        })
        self.assertEqual(resp.status_code, 302)
        # Logged in AppErrorLog
        self.assertTrue(AppErrorLog.objects.filter(error_code='CART-001').exists())
