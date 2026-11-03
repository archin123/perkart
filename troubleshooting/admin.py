from django.contrib import admin
from .models import ErrorCode, AppErrorLog


@admin.register(ErrorCode)
class ErrorCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'category', 'severity', 'is_active', 'updated_at')
    list_filter = ('category', 'severity', 'is_active')
    search_fields = ('code', 'title', 'description', 'troubleshooting_steps')
    list_editable = ('severity', 'is_active')
    fieldsets = (
        ("Error Code Definition", {
            'fields': ('code', 'title', 'category', 'severity', 'is_active')
        }),
        ("Diagnostic Explanations", {
            'fields': ('description', 'possible_causes')
        }),
        ("Actionable Steps & Advice", {
            'fields': ('troubleshooting_steps', 'preventive_recommendations', 'action_url', 'action_label')
        }),
    )


@admin.register(AppErrorLog)
class AppErrorLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'error_code', 'user', 'path', 'method', 'timestamp', 'is_resolved')
    list_filter = ('error_code', 'method', 'is_resolved', 'timestamp')
    search_fields = ('error_code', 'path', 'message', 'user__username', 'ip_address')
    readonly_fields = ('timestamp', 'error_code', 'user', 'path', 'method', 'ip_address', 'message', 'context_data')
    list_editable = ('is_resolved',)
