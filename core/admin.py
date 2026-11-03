from django.contrib import admin
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'company_name', 'category', 'rating', 'is_reviewed', 'created_at')
    list_filter = ('rating', 'category', 'is_reviewed', 'created_at')
    search_fields = ('name', 'email', 'company_name', 'subject', 'message')
    list_editable = ('is_reviewed',)
    readonly_fields = ('created_at',)
    actions = ['mark_as_reviewed']

    @admin.action(description="Mark selected feedback items as Reviewed")
    def mark_as_reviewed(self, request, queryset):
        queryset.update(is_reviewed=True)
