from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "username",
        "role_badge",
        "is_active_badge",
        "date_joined",
    )
    list_display_links = ("email", "username")
    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )
    search_fields = ("email", "username")
    ordering = ("-date_joined",)
    readonly_fields = ("id", "date_joined", "last_login")

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("id", "email", "username", "password"),
            },
        ),
        (
            "Permissions & Role",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        (
            "Groups & Permissions",
            {
                "fields": ("groups", "user_permissions"),
                "classes": ("collapse",),
            },
        ),
        (
            "Important Dates",
            {
                "fields": ("date_joined", "last_login"),
                "classes": ("collapse",),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                    "role",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    filter_horizontal = ("groups", "user_permissions")

    @admin.display(description="Role", ordering="role")
    def role_badge(self, obj):
        colors = {
            User.ADMIN: "#dc3545",
            User.USER: "#28a745",
        }
        color = colors.get(obj.role, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_role_display(),
        )

    @admin.display(description="Active", boolean=True, ordering="is_active")
    def is_active_badge(self, obj):
        return obj.is_active

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related()

    def save_model(self, request, obj, form, change):
        if obj.role == User.ADMIN:
            obj.is_staff = True
        super().save_model(request, obj, form, change)
