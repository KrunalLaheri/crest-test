from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import UserTrackingModel


class Product(UserTrackingModel):
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)],
    )
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    ssn = models.CharField(max_length=100, unique=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "products"
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["-created_on"]
        indexes = [
            models.Index(fields=["title", "is_active"]),
            models.Index(fields=["price", "is_active"]),
        ]

    def __str__(self):
        return self.title

    @property
    def final_price(self):
        if self.discount > 0:
            discount_amount = self.price * (self.discount / 100)
            return self.price - discount_amount
        return self.price

    def soft_delete(self, user=None):
        self.is_active = False
        if user:
            self.updated_by = user
        self.save(update_fields=["is_active", "updated_by", "updated_on"])


class ProductChangeLog(models.Model):
    ACTION_CREATED = "CREATED"
    ACTION_UPDATED = "UPDATED"
    ACTION_DELETED = "DELETED"
    ACTION_DISABLED = "DISABLED"

    ACTION_CHOICES = [
        (ACTION_CREATED, "Created"),
        (ACTION_UPDATED, "Updated"),
        (ACTION_DELETED, "Deleted"),
        (ACTION_DISABLED, "Disabled"),
    ]

    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="change_logs",
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "product_change_logs"
        verbose_name = "Product Change Log"
        verbose_name_plural = "Product Change Logs"
        ordering = ["-changed_at"]

    def __str__(self):
        return f"{self.product.title} - {self.action} at {self.changed_at}"
