from django.contrib import admin, messages
from django.utils.html import format_html
from boxes.models import Product, Box, Order, OrderItem, PackingLog
from boxes.services.recommendation import RecommendationService


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'length', 'width', 'height', 'weight', 'get_volume_display', 'updated_at')
    search_fields = ('name', 'sku', 'description')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')

    @admin.display(description="Volume (cm³)")
    def get_volume_display(self, obj):
        return f"{obj.volume:,.2f}"


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'length', 'width', 'height', 'max_weight', 'cost', 'get_volume_display', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code')
    list_editable = ('is_active', 'cost')
    actions = ['activate_boxes', 'deactivate_boxes']

    @admin.display(description="Internal Vol (cm³)")
    def get_volume_display(self, obj):
        return f"{obj.volume:,.2f}"

    @admin.action(description="Mark selected boxes as Active")
    def activate_boxes(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} box(es) marked active.")

    @admin.action(description="Mark selected boxes as Inactive")
    def deactivate_boxes(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} box(es) marked inactive.")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    autocomplete_fields = ['product']
    fields = ('product', 'quantity', 'get_subtotal_weight', 'get_subtotal_volume')
    readonly_fields = ('get_subtotal_weight', 'get_subtotal_volume')

    @admin.display(description="Weight (kg)")
    def get_subtotal_weight(self, obj):
        return f"{obj.total_weight:.3f} kg" if obj.product_id else "-"

    @admin.display(description="Volume (cm³)")
    def get_subtotal_volume(self, obj):
        return f"{obj.total_volume:,.2f} cm³" if obj.product_id else "-"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'customer_name', 'status', 'recommended_box',
        'selected_box', 'box_fit_status', 'get_total_weight', 'get_total_volume', 'created_at'
    )
    list_filter = ('status', 'box_fit_status', 'created_at')
    search_fields = ('order_number', 'customer_name', 'packing_notes')
    inlines = [OrderItemInline]
    actions = ['run_box_recommendation']

    @admin.display(description="Total Wt (kg)")
    def get_total_weight(self, obj):
        return f"{obj.total_weight:.3f}"

    @admin.display(description="Total Vol (cm³)")
    def get_total_volume(self, obj):
        return f"{obj.total_volume:,.2f}"

    @admin.action(description="Run Box Recommendation for selected orders")
    def run_box_recommendation(self, request, queryset):
        count = 0
        for order in queryset:
            RecommendationService.recommend_for_order(order, persist=True)
            count += 1
        self.message_user(request, f"Ran box recommendation engine on {count} order(s).", messages.SUCCESS)


@admin.register(PackingLog)
class PackingLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'recommended_box', 'success', 'volume_utilization_percent', 'weight_utilization_percent', 'created_at')
    list_filter = ('success', 'created_at')
    search_fields = ('order__order_number', 'recommended_box__name', 'reason')
    readonly_fields = [f.name for f in PackingLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
