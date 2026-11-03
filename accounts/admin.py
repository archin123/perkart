from django.contrib import admin
from django.utils import timezone
from .models import UserProfile, EmployeeVerification


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'employee_id', 'verification_status', 'is_corporate_verified', 'phone')
    list_filter = ('verification_status', 'is_corporate_verified', 'company_name')
    search_fields = ('user__username', 'user__email', 'company_name', 'employee_id')
    actions = ['approve_selected_users', 'reject_selected_users']

    @admin.action(description="Approve selected user corporate employee status")
    def approve_selected_users(self, request, queryset):
        queryset.update(verification_status='APPROVED', is_corporate_verified=True)
        self.message_user(request, "Selected user profiles have been verified.")

    @admin.action(description="Reject selected user corporate employee status")
    def reject_selected_users(self, request, queryset):
        queryset.update(verification_status='REJECTED', is_corporate_verified=False)
        self.message_user(request, "Selected user profiles marked rejected.")


@admin.register(EmployeeVerification)
class EmployeeVerificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'company_name', 'employee_id', 'status', 'submitted_at', 'reviewed_at')
    list_filter = ('status', 'company_name', 'submitted_at')
    search_fields = ('user__username', 'user__email', 'company_name', 'employee_id')
    readonly_fields = ('submitted_at',)
    actions = ['approve_verifications', 'reject_verifications']

    @admin.action(description="Approve selected verification requests")
    def approve_verifications(self, request, queryset):
        now = timezone.now()
        for obj in queryset:
            obj.status = 'APPROVED'
            obj.reviewed_at = now
            obj.reviewed_by = request.user
            obj.admin_notes = "Approved via Django Admin."
            obj.save()
            profile = obj.user.profile
            profile.verification_status = 'APPROVED'
            profile.is_corporate_verified = True
            profile.save()
        self.message_user(request, f"{queryset.count()} verification requests approved.")

    @admin.action(description="Reject selected verification requests")
    def reject_verifications(self, request, queryset):
        now = timezone.now()
        for obj in queryset:
            obj.status = 'REJECTED'
            obj.reviewed_at = now
            obj.reviewed_by = request.user
            obj.rejection_reason = "Documentation rejected by admin."
            obj.save()
            profile = obj.user.profile
            profile.verification_status = 'REJECTED'
            profile.is_corporate_verified = False
            profile.save()
        self.message_user(request, f"{queryset.count()} verification requests rejected.")
