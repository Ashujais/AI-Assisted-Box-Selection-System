from decimal import Decimal
from rest_framework import serializers
from boxes.models import Product, Box, Order, OrderItem, PackingLog


class ProductSerializer(serializers.ModelSerializer):
    volume = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    dimensions_sorted = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'length', 'width', 'height',
            'weight', 'volume', 'dimensions_sorted', 'description',
            'created_at', 'updated_at'
        ]

    def get_dimensions_sorted(self, obj):
        return [float(d) for d in obj.dimensions_sorted]


class BoxSerializer(serializers.ModelSerializer):
    volume = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    dimensions_sorted = serializers.SerializerMethodField()

    class Meta:
        model = Box
        fields = [
            'id', 'name', 'code', 'length', 'width', 'height',
            'max_weight', 'cost', 'empty_weight', 'is_active',
            'volume', 'dimensions_sorted', 'created_at', 'updated_at'
        ]

    def get_dimensions_sorted(self, obj):
        return [float(d) for d in obj.dimensions_sorted]


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_sku = serializers.ReadOnlyField(source='product.sku')
    product_dimensions = serializers.SerializerMethodField()
    unit_weight = serializers.ReadOnlyField(source='product.weight')
    total_weight = serializers.DecimalField(max_digits=10, decimal_places=3, read_only=True)
    total_volume = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_sku',
            'product_dimensions', 'unit_weight', 'quantity',
            'total_weight', 'total_volume'
        ]

    def get_product_dimensions(self, obj):
        return {
            'length': float(obj.product.length),
            'width': float(obj.product.width),
            'height': float(obj.product.height),
        }


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    recommended_box_detail = BoxSerializer(source='recommended_box', read_only=True)
    selected_box_detail = BoxSerializer(source='selected_box', read_only=True)
    total_weight = serializers.DecimalField(max_digits=10, decimal_places=3, read_only=True)
    total_volume = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer_name', 'status',
            'recommended_box', 'recommended_box_detail',
            'selected_box', 'selected_box_detail',
            'box_fit_status', 'packing_notes',
            'total_weight', 'total_volume', 'total_quantity',
            'items', 'created_at', 'updated_at'
        ]


class PackingLogSerializer(serializers.ModelSerializer):
    box_name = serializers.ReadOnlyField(source='recommended_box.name')
    box_code = serializers.ReadOnlyField(source='recommended_box.code')
    order_number = serializers.ReadOnlyField(source='order.order_number')

    class Meta:
        model = PackingLog
        fields = [
            'id', 'order', 'order_number', 'recommended_box',
            'box_name', 'box_code', 'success',
            'volume_utilization_percent', 'weight_utilization_percent',
            'evaluation_summary', 'placements', 'reason', 'created_at'
        ]


class AdHocItemInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150, default="Item")
    sku = serializers.CharField(max_length=50, required=False, default="")
    length = serializers.FloatField(min_value=0.01)
    width = serializers.FloatField(min_value=0.01)
    height = serializers.FloatField(min_value=0.01)
    weight = serializers.FloatField(min_value=0.001)
    quantity = serializers.IntegerField(min_value=1, default=1)


class AdHocPackingRequestSerializer(serializers.Serializer):
    items = serializers.ListField(
        child=AdHocItemInputSerializer(),
        allow_empty=False,
        help_text="List of items to pack with dimensions and weights"
    )
    box_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list,
        help_text="Optional list of specific box IDs to restrict evaluation to"
    )
