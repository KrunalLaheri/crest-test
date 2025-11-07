import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains")
    title_exact = django_filters.CharFilter(field_name="title", lookup_expr="exact")
    description = django_filters.CharFilter(lookup_expr="icontains")
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    created_on_after = django_filters.DateTimeFilter(field_name="created_on", lookup_expr="gte")
    created_on_before = django_filters.DateTimeFilter(field_name="created_on", lookup_expr="lte")
    updated_on_after = django_filters.DateTimeFilter(field_name="updated_on", lookup_expr="gte")
    updated_on_before = django_filters.DateTimeFilter(field_name="updated_on", lookup_expr="lte")

    class Meta:
        model = Product
        fields = {
            "is_active": ["exact"],
            "ssn": ["exact"],
        }
