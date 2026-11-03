from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile


class Command(BaseCommand):
    help = "Creates or resets the PerkCart Master Admin superuser with full portal privileges."

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='masteradmin', help='Username for the master admin')
        parser.add_argument('--email', type=str, default='masteradmin@perkcart.com', help='Email for the master admin')
        parser.add_argument('--password', type=str, default='MasterAdmin@2026', help='Password for the master admin')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': 'Master',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )

        user.email = email
        user.first_name = 'Master'
        user.last_name = 'Administrator'
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.company_name = 'PerkCart Global Master HQ'
        profile.employee_id = 'MASTER-001'
        profile.corporate_email = email
        profile.phone = '+91 99999 00000'
        profile.department = 'Executive IT Administration'
        profile.verification_status = 'APPROVED'
        profile.is_corporate_verified = True
        profile.save()

        action = "Created new" if created else "Updated existing"
        self.stdout.write(self.style.SUCCESS(
            f"Successfully {action} Master Admin:\n"
            f"  Username: {username}\n"
            f"  Password: {password}\n"
            f"  Email:    {email}\n"
            f"  Status:   Superuser + Staff (All Permissions Granted)"
        ))
