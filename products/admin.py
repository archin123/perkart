from django.contrib import admin
from .models import ProductCategory, Product, Offer, Wishlist


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'icon', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', 'is_active')
    search_fields = ('name', 'description')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'corporate_price', 'original_price', 'stock_quantity', 'is_featured', 'is_active')
    list_filter = ('category', 'is_featured', 'is_active')
    search_fields = ('name', 'sku', 'description', 'tagline')
    list_editable = ('corporate_price', 'stock_quantity', 'is_featured', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ("Basic Information", {
            'fields': ('name', 'slug', 'category', 'sku', 'tagline', 'badge', 'is_featured', 'is_active')
        }),
        ("Pricing & Stock", {
            'fields': ('original_price', 'corporate_price', 'stock_quantity')
        }),
        ("Product Details & Specs", {
            'fields': ('description', 'specs', 'image_url')
        }),
        ("Customer Ratings", {
            'fields': ('rating', 'review_count')
        }),
    )


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'discount_percent', 'min_order_amount', 'is_active', 'valid_until')
    list_filter = ('is_active', 'is_corporate_only')
    search_fields = ('code', 'title', 'description')
    list_editable = ('discount_percent', 'is_active')


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'product__name')
