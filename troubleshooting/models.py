from django.db import models
from django.contrib.auth.models import User


class ErrorCode(models.Model):
    CATEGORY_CHOICES = [
        ('AUTH', 'Authentication & Verification'),
        ('CART', 'Cart & Inventory'),
        ('DISCOUNT', 'Discount & Coupons'),
        ('ORDER', 'Order & Tracking'),
        ('PAYMENT', 'Payment & Corporate Billing'),
        ('API', 'System & External Integrations'),
        ('SECURITY', 'Security & Access Control'),
    ]

    SEVERITY_CHOICES = [
        ('LOW', 'Low Severity (Informational)'),
        ('MEDIUM', 'Medium Severity (Actionable)'),
        ('HIGH', 'High Severity (Blocking Workflow)'),
        ('CRITICAL', 'Critical Severity (Immediate Escalation)'),
    ]

    code = models.CharField(max_length=30, unique=True, primary_key=True)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='MEDIUM')
    description = models.TextField()
    possible_causes = models.TextField(
        help_text='Itemized potential root causes'
    )
    troubleshooting_steps = models.TextField(
        help_text='Numbered step-by-step resolution steps for employees'
    )
    preventive_recommendations = models.TextField(
        help_text='Preventative best practices for employees and administrators'
    )
    action_url = models.CharField(
        max_length=200,
        blank=True,
        help_text='Direct in-app route to resolve, e.g. /login/ or /profile/verification/'
    )
    action_label = models.CharField(
        max_length=80,
        blank=True,
        default='Resolve Issue'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code}: {self.title} [{self.severity}]"

    def causes_list(self):
        return [c.strip() for c in self.possible_causes.split('\n') if c.strip()]

    def steps_list(self):
        return [s.strip() for s in self.troubleshooting_steps.split('\n') if s.strip()]

    def recommendations_list(self):
        return [r.strip() for r in self.preventive_recommendations.split('\n') if r.strip()]


class AppErrorLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    error_code = models.CharField(max_length=40, blank=True, default='SYS-GENERIC')
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='logged_errors'
    )
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=15, default='GET')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    message = models.TextField()
    context_data = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.error_code}] {self.path} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
