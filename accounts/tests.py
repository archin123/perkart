from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import UserProfile, EmployeeVerification


class AccountsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='Password@123'
        )
        self.user = User.objects.create_user(
            username='testemployee',
            email='test@corporate.internal',
            password='Password@123'
        )
        self.profile = self.user.profile
        self.profile.company_name = 'Test Partner Corp'
        self.profile.employee_id = 'EMP-001'
        self.profile.verification_status = 'APPROVED'
        self.profile.is_corporate_verified = True
        self.profile.save()

    def test_registration(self):
        resp = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'Employee',
            'corporate_email': 'new@partner.internal',
            'company_name': 'Partner Tech',
            'employee_id': 'EMP-777',
            'password': 'SecurePassword@123',
            'confirm_password': 'SecurePassword@123'
        })
        self.assertEqual(resp.status_code, 302)
        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.profile.verification_status, 'PENDING')
        self.assertFalse(new_user.profile.is_corporate_verified)

    def test_login_and_logout(self):
        # Valid login
        login_resp = self.client.post(reverse('accounts:login'), {
            'username': 'testemployee',
            'password': 'Password@123'
        })
        self.assertEqual(login_resp.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

        # Logout
        logout_resp = self.client.get(reverse('accounts:logout'))
        self.assertEqual(logout_resp.status_code, 302)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_profile_view_requires_login(self):
        resp = self.client.get(reverse('accounts:profile'))
        self.assertEqual(resp.status_code, 302)

        self.client.login(username='testemployee', password='Password@123')
        resp = self.client.get(reverse('accounts:profile'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Test Partner Corp')

    def test_admin_verification_action(self):
        # Unprivileged user denied
        self.client.login(username='testemployee', password='Password@123')
        resp = self.client.get(reverse('accounts:admin_verifications'))
        self.assertEqual(resp.status_code, 302)

        # Admin user allowed
        self.client.login(username='admin_test', password='Password@123')
        resp = self.client.get(reverse('accounts:admin_verifications'))
        self.assertEqual(resp.status_code, 200)
