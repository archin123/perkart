from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class FAQCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(
        max_length=60,
        default='bi-question-circle',
        help_text='Bootstrap icon class name, e.g. bi-shield-check, bi-credit-card, bi-truck'
    )
    description = models.CharField(max_length=255, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'FAQ Categories'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class FAQ(models.Model):
    category = models.ForeignKey(
        FAQCategory,
        on_delete=models.CASCADE,
        related_name='faqs'
    )
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.IntegerField(default=0)
    helpful_count = models.PositiveIntegerField(default=0)
    unhelpful_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category__order', 'order', '-created_at']

    def __str__(self):
        return f"[{self.category.name}] {self.question}"


class FAQVote(models.Model):
    VOTE_CHOICES = [
        ('helpful', 'Helpful'),
        ('unhelpful', 'Unhelpful'),
    ]

    faq = models.ForeignKey(FAQ, on_delete=models.CASCADE, related_name='votes')
    session_key = models.CharField(max_length=64)
    vote_type = models.CharField(max_length=15, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('faq', 'session_key')

    def __str__(self):
        return f"{self.vote_type} vote on FAQ #{self.faq_id}"


class UnansweredQuestion(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('ANSWERED', 'Answered / Added to FAQ'),
        ('RESOLVED_BY_EMAIL', 'Resolved via Support Email'),
        ('CLOSED', 'Closed'),
    ]

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='unanswered_questions'
    )
    name = models.CharField(max_length=150)
    email = models.EmailField()
    company_name = models.CharField(max_length=150, blank=True)
    question = models.TextField()
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='PENDING')
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Question by {self.name} ({self.status}): {self.question[:60]}"
