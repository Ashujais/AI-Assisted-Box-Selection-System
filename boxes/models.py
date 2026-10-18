from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    """
    Represents an ecommerce sellable product with physical dimensions and weight.
    Dimensions are stored in centimeters (cm), weight in kilograms (kg).
    """
    name = models.CharField(max_length=200, help_text="Product name/title")
    sku = models.CharField(max_length=64, unique=True, help_text="Unique Stock Keeping Unit")
    length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Length in centimeters (cm)"
    )
    width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Width in centimeters (cm)"
    )
    height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Height in centimeters (cm)"
    )
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Weight in kilograms (kg)"
    )
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return f"{self.name} ({self.sku}) - {self.length}x{self.width}x{self.height}cm, {self.weight}kg"

    @property
    def volume(self) -> Decimal:
        """Returns the bounding volume in cubic centimeters (cm³)."""
        return self.length * self.width * self.height

    @property
    def dimensions_sorted(self) -> tuple[Decimal, Decimal, Decimal]:
        """Returns dimensions sorted in ascending order (d_min, d_mid, d_max)."""
        return tuple(sorted([self.length, self.width, self.height]))


class Box(models.Model):
    """
    Represents a shipping cardboard box with internal usable dimensions,
    maximum weight capacity, and cost.
    """
    name = models.CharField(max_length=150, help_text="Descriptive box name (e.g. Small Mailer Box)")
    code = models.CharField(max_length=50, unique=True, help_text="Unique box identifier code (e.g. BOX-S-01)")
    length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Internal length in centimeters (cm)"
    )
    width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Internal width in centimeters (cm)"
    )
    height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Internal height in centimeters (cm)"
    )
    max_weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Maximum weight capacity in kilograms (kg)"
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Cost of the shipping box (e.g. in USD or INR)"
    )
    empty_weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0.000'),
        validators=[MinValueValidator(Decimal('0.000'))],
        help_text="Tare weight of the empty box itself (kg)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this box is currently available for packaging in the warehouse"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['cost', 'name']
        verbose_name = _("Shipping Box")
        verbose_name_plural = _("Shipping Boxes")

    def __str__(self):
        return f"{self.name} [{self.code}] ({self.length}x{self.width}x{self.height}cm, Max {self.max_weight}kg, Cost: ${self.cost})"

    @property
    def volume(self) -> Decimal:
        """Returns internal usable volume in cubic centimeters (cm³)."""
        return self.length * self.width * self.height

    @property
    def dimensions_sorted(self) -> tuple[Decimal, Decimal, Decimal]:
        """Returns internal dimensions sorted in ascending order (d_min, d_mid, d_max)."""
        return tuple(sorted([self.length, self.width, self.height]))


class Order(models.Model):
    """
    Represents a customer order containing one or more products.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending Packing'),
        ('PACKED', 'Packed'),
        ('SHIPPED', 'Shipped'),
        ('CANCELLED', 'Cancelled'),
    ]

    FIT_STATUS_CHOICES = [
        ('NOT_EVALUATED', 'Not Evaluated'),
        ('OPTIMAL_FIT', 'Optimal Box Found'),
        ('ALTERNATIVE_FIT', 'Alternative Box Fit'),
        ('MULTI_BOX_NEEDED', 'Multiple Boxes Required'),
        ('NO_FIT', 'No Suitable Box Available'),
    ]

    order_number = models.CharField(max_length=64, unique=True, help_text="Unique customer order reference")
    customer_name = models.CharField(max_length=150, help_text="Customer full name")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    recommended_box = models.ForeignKey(
        Box,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='recommended_orders',
        help_text="System-recommended box based on dimensions, weight, and cost"
    )
    selected_box = models.ForeignKey(
        Box,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='selected_orders',
        help_text="Actual box selected or confirmed by warehouse staff"
    )
    box_fit_status = models.CharField(
        max_length=30,
        choices=FIT_STATUS_CHOICES,
        default='NOT_EVALUATED'
    )
    packing_notes = models.TextField(blank=True, default="", help_text="Notes or override reasons")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return f"Order #{self.order_number} - {self.customer_name} ({self.get_status_display()})"

    @property
    def total_weight(self) -> Decimal:
        """Total weight of all ordered items in kilograms."""
        total = Decimal('0.000')
        for item in self.items.all():
            total += item.total_weight
        return total

    @property
    def total_volume(self) -> Decimal:
        """Total volume of all ordered items in cm³."""
        total = Decimal('0.00')
        for item in self.items.all():
            total += item.total_volume
        return total

    @property
    def total_quantity(self) -> int:
        """Total number of individual items in the order."""
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    """
    Represents an item line in an order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")
        unique_together = ('order', 'product')

    def __str__(self):
        return f"{self.quantity}x {self.product.name} (in Order #{self.order.order_number})"

    @property
    def total_weight(self) -> Decimal:
        return self.quantity * self.product.weight

    @property
    def total_volume(self) -> Decimal:
        return self.quantity * self.product.volume


class PackingLog(models.Model):
    """
    Audit log of box recommendation calculations, candidate box evaluations,
    utilization metrics, and 3D placement results.
    """
    order = models.ForeignKey(
        Order,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='packing_logs'
    )
    recommended_box = models.ForeignKey(
        Box,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='packing_evaluations'
    )
    success = models.BooleanField(default=False)
    volume_utilization_percent = models.FloatField(default=0.0)
    weight_utilization_percent = models.FloatField(default=0.0)
    evaluation_summary = models.JSONField(
        default=dict,
        help_text="Detailed evaluation results of each candidate box evaluated"
    )
    placements = models.JSONField(
        default=list,
        help_text="3D coordinates and orientations for placed items"
    )
    reason = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Packing Log")
        verbose_name_plural = _("Packing Logs")

    def __str__(self):
        order_ref = f"Order #{self.order.order_number}" if self.order else "Ad-hoc Order"
        box_ref = self.recommended_box.name if self.recommended_box else "No Box"
        return f"PackingLog ({order_ref}) -> {box_ref} [Success: {self.success}]"
