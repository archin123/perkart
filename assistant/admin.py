from django.contrib import admin
from .models import AIConversation, AIMessage


class AIMessageInline(admin.TabularInline):
    model = AIMessage
    extra = 0
    readonly_fields = ('role', 'content', 'engine_used', 'created_at')


@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'title', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('user__username', 'session_key', 'title')
    inlines = [AIMessageInline]


@admin.register(AIMessage)
class AIMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'role', 'engine_used', 'created_at')
    list_filter = ('role', 'engine_used', 'created_at')
    search_fields = ('content', 'conversation__user__username')
    readonly_fields = ('created_at',)
