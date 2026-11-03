from django.contrib import admin
from .models import FAQCategory, FAQ, FAQVote, UnansweredQuestion


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'icon')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order',)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'order', 'helpful_count', 'unhelpful_count', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('question', 'answer')
    list_editable = ('order', 'is_active')


@admin.register(FAQVote)
class FAQVoteAdmin(admin.ModelAdmin):
    list_display = ('faq', 'session_key', 'vote_type', 'created_at')
    list_filter = ('vote_type', 'created_at')


@admin.register(UnansweredQuestion)
class UnansweredQuestionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'company_name', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'question', 'company_name')
    actions = ['mark_answered', 'mark_closed']

    @admin.action(description="Mark selected questions as Answered")
    def mark_answered(self, request, queryset):
        queryset.update(status='ANSWERED')

    @admin.action(description="Mark selected questions as Closed")
    def mark_closed(self, request, queryset):
        queryset.update(status='CLOSED')
