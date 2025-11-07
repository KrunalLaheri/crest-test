from django.contrib import admin
from django.utils.html import format_html

from .models import Product, ProductChangeLog


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "price",
        "discount",
        "final_price_display",
        "is_active",
        "created_on",
    )
    list_display_links = ("title",)
    list_editable = ("price", "discount", "is_active")
    list_filter = ("is_active", "created_on", "updated_on")
    search_fields = ("title", "description", "ssn")
    ordering = ("-created_on",)
    readonly_fields = (
        "id",
        "final_price_display",
        "created_on",
        "updated_on",
        "created_by",
        "updated_by",
    )
    fieldsets = (
        (
            "Product Information",
            {
                "fields": (
                    "id",
                    "title",
                    "description",
                    "ssn",
                    "image",
                ),
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "price",
                    "discount",
                    "final_price_display",
                ),
            },
        ),
        (
            "Status",
            {
                "fields": ("is_active",),
            },
        ),
        (
            "Tracking Information",
            {
                "fields": (
                    "created_on",
                    "created_by",
                    "updated_on",
                    "updated_by",
                ),
                "classes": ("collapse",),
            },
        ),
    )
    actions = ["disable_products", "enable_products"]

    @admin.display(description="Final Price")
    def final_price_display(self, obj):
        if obj.discount > 0:
            return format_html(
                '<span style="text-decoration: line-through; color: #6c757d;">'
                "${:.2f}</span> "
                '<span style="font-weight: bold; color: #dc3545; font-size: 1.1em;">'
                "${:.2f}</span>",
                obj.price,
                obj.final_price,
            )
        return format_html(
            '<span style="font-weight: bold; color: #28a745;">${:.2f}</span>',
            obj.final_price,
        )

    @admin.action(description="Disable selected products")
    def disable_products(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f"{updated} product(s) were successfully disabled.",
        )

    @admin.action(description="Enable selected products")
    def enable_products(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f"{updated} product(s) were successfully enabled.",
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("created_by", "updated_by")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ProductChangeLog)
class ProductChangeLogAdmin(admin.ModelAdmin):
    list_display = (
        "product_title",
        "action_badge",
        "changed_by_display",
        "changed_at",
    )
    list_display_links = ("product_title",)
    list_filter = ("action", "changed_at")
    search_fields = (
        "product__title",
        "product__ssn",
        "changed_by__email",
        "changed_by__username",
    )
    ordering = ("-changed_at",)
    readonly_fields = (
        "product",
        "action",
        "changed_by",
        "changed_at",
        "changes_display",
    )
    fieldsets = (
        (
            "Change Information",
            {
                "fields": (
                    "product",
                    "action",
                    "changed_by",
                    "changed_at",
                ),
            },
        ),
        (
            "Detailed Changes",
            {
                "fields": ("changes_display",),
                "classes": ("collapse",),
            },
        ),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="Product", ordering="product__title")
    def product_title(self, obj):
        return obj.product.title

    @admin.display(description="Action", ordering="action")
    def action_badge(self, obj):
        colors = {
            ProductChangeLog.ACTION_CREATED: "#28a745",
            ProductChangeLog.ACTION_UPDATED: "#007bff",
            ProductChangeLog.ACTION_DELETED: "#dc3545",
            ProductChangeLog.ACTION_DISABLED: "#fd7e14",
        }
        color = colors.get(obj.action, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_action_display(),
        )

    @admin.display(description="Changed By")
    def changed_by_display(self, obj):
        if obj.changed_by:
            return format_html(
                '{} <span style="color: #6c757d;">({})</span>',
                obj.changed_by.username,
                obj.changed_by.email,
            )
        return format_html('<span style="color: #6c757d;">System</span>')

    @admin.display(description="Changes")
    def changes_display(self, obj):
        if obj.changes:
            import json

            formatted_json = json.dumps(obj.changes, indent=2)
            return format_html(
                '<pre style="background-color: #f8f9fa; padding: 10px; '
                'border-radius: 5px; overflow-x: auto;">{}</pre>',
                formatted_json,
            )
        return format_html('<span style="color: #6c757d;">No changes recorded</span>')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("product", "changed_by")
