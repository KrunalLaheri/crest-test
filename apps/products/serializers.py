from rest_framework import serializers

from .models import Product


class ProductListSerializer(serializers.ModelSerializer):
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "price",
            "discount",
            "final_price",
            "is_active",
            "created_on",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)
    updated_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = "__all__"


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["title", "description", "price", "discount", "image", "ssn"]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate_discount(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Discount must be between 0 and 100")
        return value

    def validate_ssn(self, value):
        if Product.objects.filter(ssn=value).exists():
            raise serializers.ValidationError("A product with this SSN already exists")
        return value


class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["title", "description", "price", "discount", "image", "ssn"]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate_discount(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Discount must be between 0 and 100")
        return value

    def validate_ssn(self, value):
        instance = self.instance
        if instance and Product.objects.filter(ssn=value).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError("A product with this SSN already exists")
        elif not instance and Product.objects.filter(ssn=value).exists():
            raise serializers.ValidationError("A product with this SSN already exists")
        return value


class ProductBulkCreateSerializer(serializers.Serializer):
    products = ProductCreateSerializer(many=True)

    def validate_products(self, value):
        if not value:
            raise serializers.ValidationError("Products list cannot be empty")

        ssns = [product.get("ssn") for product in value if "ssn" in product]
        if len(ssns) != len(set(ssns)):
            raise serializers.ValidationError("Duplicate SSNs found in the request")

        existing_ssns = Product.objects.filter(ssn__in=ssns).values_list("ssn", flat=True)
        if existing_ssns:
            raise serializers.ValidationError(
                f"The following SSNs already exist: {', '.join(existing_ssns)}"
            )

        return value

    def create(self, validated_data):
        products_data = validated_data.get("products", [])
        user = self.context.get("request").user

        products = []
        for product_data in products_data:
            product = Product.objects.create(
                **product_data,
                created_by=user,
                updated_by=user,
            )
            products.append(product)

        return products
