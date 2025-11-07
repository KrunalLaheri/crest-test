from datetime import datetime

from django.db.models import Q
from django.http import HttpResponse
from openpyxl import Workbook
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.authentication.permissions import IsAdminOrReadOnly

from .filters import ProductFilter
from .models import Product
from .serializers import (
    ProductBulkCreateSerializer,
    ProductCreateSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ProductUpdateSerializer,
)


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filterset_class = ProductFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_on", "updated_on", "price", "title"]
    ordering = ["-created_on"]

    def get_queryset(self):
        queryset = Product.objects.all()

        if self.action == "list" and not self.request.user.is_admin():
            queryset = queryset.filter(is_active=True)

        return queryset.select_related("created_by", "updated_by")

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        elif self.action in ["create", "bulk_create"]:
            return ProductCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return ProductUpdateSerializer
        return ProductDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete(user=request.user)
        return Response(
            {"message": "Product soft deleted successfully"},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsAdminOrReadOnly])
    def disable(self, request, pk=None):
        product = self.get_object()
        product.soft_delete(user=request.user)
        return Response(
            {"message": f"Product '{product.title}' disabled successfully"},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def export(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        wb = Workbook()
        ws = wb.active
        ws.title = "Products"

        headers = [
            "ID",
            "Title",
            "Description",
            "Price",
            "Discount (%)",
            "Final Price",
            "SSN",
            "Is Active",
            "Created On",
            "Updated On",
        ]
        ws.append(headers)

        for product in queryset:
            ws.append(
                [
                    str(product.id),
                    product.title,
                    product.description,
                    float(product.price),
                    float(product.discount),
                    float(product.final_price),
                    product.ssn,
                    "Yes" if product.is_active else "No",
                    product.created_on.strftime("%Y-%m-%d %H:%M:%S"),
                    product.updated_on.strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )

        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        filename = f'products_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        wb.save(response)
        return response

    @action(detail=False, methods=["get"])
    def search(self, request):
        query = request.query_params.get("q", "").strip()

        if not query:
            return Response(
                {"error": "Search query parameter 'q' is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated, IsAdminOrReadOnly])
    def bulk_create(self, request):
        serializer = ProductBulkCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        products = serializer.save()

        return Response(
            {
                "message": f"{len(products)} products created successfully",
                "count": len(products),
                "products": ProductDetailSerializer(products, many=True).data,
            },
            status=status.HTTP_201_CREATED,
        )
