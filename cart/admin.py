from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'price', 'quantity', 'item_total')

    def item_total(self, instance):
        return f"₹{instance.item_total:,.2f}"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'user', 'full_name', 'total_amount',
        'status', 'payment_status', 'payment_method', 'created_at'
    )
    list_filter = ('status', 'payment_status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__username', 'full_name', 'corporate_email', 'phone', 'transaction_id')
    readonly_fields = ('order_number', 'transaction_id', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    fieldsets = (
        ("Order Information", {
            'fields': ('order_number', 'user', 'status', 'created_at', 'updated_at')
        }),
        ("Financial Breakdown", {
            'fields': ('subtotal', 'discount_amount', 'coupon_code', 'shipping_cost', 'total_amount')
        }),
        ("Employee & Shipping Details", {
            'fields': ('full_name', 'corporate_email', 'phone', 'company_name', 'employee_id', 'shipping_address', 'city', 'postal_code')
        }),
        ("Payment & Dispatch Status", {
            'fields': ('payment_method', 'payment_status', 'transaction_id', 'tracking_number', 'estimated_delivery')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'price', 'quantity')
    search_fields = ('order__order_number', 'product_name')
