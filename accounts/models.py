from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    VERIFICATION_STATUSES = [
        ('PENDING', 'Pending Verification'),
        ('APPROVED', 'Approved / Verified Employee'),
        ('REJECTED', 'Verification Rejected'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company_name = models.CharField(max_length=150, default='Corporate Partner Inc.')
    employee_id = models.CharField(max_length=50, blank=True)
    corporate_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    shipping_address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUSES,
        default='PENDING'
    )
    is_corporate_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.company_name} - {self.verification_status})"

    def is_verified(self):
        return self.is_corporate_verified or self.verification_status == 'APPROVED'

    def can_access_corporate_deals(self):
        # In PerkCart corporate store, users who are pending can preview deals,
        # but verified users receive confirmed employee pricing and checkout access.
        return self.is_verified()


class EmployeeVerification(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_requests')
    company_name = models.CharField(max_length=150)
    corporate_email = models.EmailField()
    employee_id = models.CharField(max_length=50)
    work_location = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    rejection_reason = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reviewed_verifications'
    )

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Verification #{self.id} - {self.user.username} ({self.status})"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
