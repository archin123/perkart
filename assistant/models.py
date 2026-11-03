from django.db import models
from django.contrib.auth.models import User


class AIConversation(models.Model):
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='ai_conversations'
    )
    session_key = models.CharField(max_length=64, blank=True)
    title = models.CharField(max_length=150, default='Corporate Shopping Inquiry')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        username = self.user.username if self.user else f"Guest ({self.session_key[:8]})"
        return f"Chat #{self.id} - {username}: {self.title}"


class AIMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System Context'),
    ]

    conversation = models.ForeignKey(
        AIConversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    engine_used = models.CharField(
        max_length=80,
        default='SearchFallbackEngine',
        help_text='Gemini-2.5-Flash or Search-Based Fallback Engine'
    )
    retrieved_sources = models.JSONField(
        default=list,
        blank=True,
        help_text='Structured list of referenced items (Products, FAQs, Error Codes, Offers, Orders)'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role.capitalize()} on Chat #{self.conversation_id}: {self.content[:40]}..."
