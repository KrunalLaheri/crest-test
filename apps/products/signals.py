from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import Product, ProductChangeLog


@receiver(post_save, sender=Product)
def log_product_save(sender, instance, created, **kwargs):
    if created:
        ProductChangeLog.objects.create(
            product=instance,
            action=ProductChangeLog.ACTION_CREATED,
            changed_by=instance.created_by,
            changes={"message": "Product created"},
        )
    else:
        changes = {}
        if hasattr(instance, "_old_values"):
            for field in ["title", "description", "price", "discount", "is_active"]:
                old_value = getattr(instance._old_values, field, None)
                new_value = getattr(instance, field)
                if old_value != new_value:
                    changes[field] = {"old": str(old_value), "new": str(new_value)}

        action = (
            ProductChangeLog.ACTION_DISABLED
            if not instance.is_active
            else ProductChangeLog.ACTION_UPDATED
        )

        ProductChangeLog.objects.create(
            product=instance,
            action=action,
            changed_by=instance.updated_by,
            changes=changes if changes else {"message": "Product updated"},
        )


@receiver(pre_delete, sender=Product)
def log_product_delete(sender, instance, **kwargs):
    ProductChangeLog.objects.create(
        product=instance,
        action=ProductChangeLog.ACTION_DELETED,
        changed_by=getattr(instance, "updated_by", None),
        changes={"message": "Product deleted"},
    )
