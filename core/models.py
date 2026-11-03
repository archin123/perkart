from django.db import models
from django.contrib.auth.models import User


class Feedback(models.Model):
    CATEGORY_CHOICES = [
        ('EXPERIENCE', 'Overall Shopping Experience'),
        ('PRODUCTS', 'Product Catalogue & Availability'),
        ('DISCOUNT', 'Corporate Pricing & Discount Offers'),
        ('DELIVERY', 'Order Delivery & Shipping Support'),
        ('TECHNICAL', 'Bug Report / Website Troubleshooting'),
        ('OTHER', 'General Suggestion'),
    ]

    RATING_CHOICES = [
        (5, '⭐⭐⭐⭐⭐ Excellent (5/5)'),
        (4, '⭐⭐⭐⭐ Good (4/5)'),
        (3, '⭐⭐⭐ Average (3/5)'),
        (2, '⭐⭐ Needs Improvement (2/5)'),
        (1, '⭐ Poor (1/5)'),
    ]

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='feedbacks'
    )
    name = models.CharField(max_length=120)
    email = models.EmailField()
    company_name = models.CharField(max_length=150, blank=True)
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default='EXPERIENCE')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=5)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    is_reviewed = models.BooleanField(default=False)
    admin_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback from {self.name} ({self.rating}/5) - {self.category}"
