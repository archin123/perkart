from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class ProductCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=60,
        default='bi-laptop',
        help_text='Bootstrap icon class name, e.g. bi-laptop, bi-phone, bi-headphones'
    )
    image_url = models.URLField(max_length=500, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Product Categories'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name='products'
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    sku = models.CharField(max_length=60, unique=True)
    tagline = models.CharField(max_length=250, blank=True)
    description = models.TextField()
    specs = models.JSONField(
        default=dict,
        blank=True,
        help_text='JSON dictionary of key-value technical specifications'
    )
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    corporate_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=20)
    image_url = models.URLField(max_length=500)
    badge = models.CharField(
        max_length=80,
        blank=True,
        default='Corporate Exclusive'
    )
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.8)
    review_count = models.PositiveIntegerField(default=48)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.sku}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def discount_percent(self):
        if self.original_price and self.original_price > 0:
            discount = ((self.original_price - self.corporate_price) / self.original_price) * 100
            return int(round(discount))
        return 0

    @property
    def savings(self):
        if self.original_price and self.corporate_price:
            return max(self.original_price - self.corporate_price, 0)
        return 0

    def is_in_stock(self):
        return self.stock_quantity > 0


class Offer(models.Model):
    code = models.CharField(max_length=40, unique=True)
    title = models.CharField(max_length=150)
    description = models.TextField()
    discount_percent = models.PositiveIntegerField(
        default=10,
        help_text='Percentage discount applied at checkout'
    )
    max_discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    min_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    is_corporate_only = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    valid_until = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-discount_percent']

    def __str__(self):
        return f"{self.code} - {self.discount_percent}% off ({self.title})"


class Wishlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlist_items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='wishlisted_by'
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username} -> {self.product.name}"
