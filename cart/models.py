from django.db import models
from django.contrib.auth.models import User
from products.models import Product
import uuid


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Confirmation'),
        ('PROCESSING', 'Processing & Corporate Validation'),
        ('SHIPPED', 'Dispatched / In Transit'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    PAYMENT_METHODS = [
        ('SIMULATED_CORP_PAYROLL', 'Corporate Payroll Deduction (Simulated)'),
        ('SIMULATED_CORP_CARD', 'Corporate Corporate Card (Simulated)'),
        ('SIMULATED_UPI', 'Instant UPI / Corporate NetBanking (Simulated)'),
    ]

    PAYMENT_STATUSES = [
        ('PAID', 'Authorized & Paid (Simulated)'),
        ('PENDING', 'Pending Approval'),
        ('FAILED', 'Failed / Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=40, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PROCESSING')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon_code = models.CharField(max_length=40, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Shipping & Employee details
    full_name = models.CharField(max_length=150)
    corporate_email = models.EmailField()
    phone = models.CharField(max_length=20)
    shipping_address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    company_name = models.CharField(max_length=150, blank=True)
    employee_id = models.CharField(max_length=50, blank=True)

    # Simulated Payment confirmation
    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_METHODS,
        default='SIMULATED_CORP_PAYROLL'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUSES,
        default='PAID'
    )
    transaction_id = models.CharField(max_length=80, blank=True)
    tracking_number = models.CharField(max_length=80, blank=True)
    estimated_delivery = models.CharField(max_length=80, blank=True, default='3-5 Business Days')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"PKC-{uuid.uuid4().hex[:8].upper()}"
        if not self.transaction_id:
            self.transaction_id = f"TXN-CORP-{uuid.uuid4().hex[:10].upper()}"
        if not self.tracking_number:
            self.tracking_number = f"EXP-BLUEDART-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_number} - {self.user.username} (₹{self.total_amount})"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items'
    )
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product_name} in {self.order.order_number}"

    @property
    def item_total(self):
        return self.price * self.quantity
