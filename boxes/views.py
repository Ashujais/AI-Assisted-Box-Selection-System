from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib import messages
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from boxes.models import Product, Box, Order, OrderItem, PackingLog
from boxes.serializers import (
    ProductSerializer,
    BoxSerializer,
    OrderSerializer,
    OrderItemSerializer,
    PackingLogSerializer,
    AdHocPackingRequestSerializer,
)
from boxes.services.recommendation import RecommendationService


# ==============================================================================
# REST API VIEWSETS & ENDPOINTS
# ==============================================================================

class ProductViewSet(viewsets.ModelViewSet):
    """CRUD API for ecommerce products."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    search_fields = ['name', 'sku']


class BoxViewSet(viewsets.ModelViewSet):
    """CRUD API for shipping box types."""
    queryset = Box.objects.all()
    serializer_class = BoxSerializer
    filterset_fields = ['is_active']


class OrderViewSet(viewsets.ModelViewSet):
    """CRUD API for customer orders."""
    queryset = Order.objects.prefetch_related('items__product').select_related('recommended_box', 'selected_box').all()
    serializer_class = OrderSerializer

    @action(detail=True, methods=['post'])
    def recommend(self, request, pk=None):
        """
        Calculates and saves optimal box recommendation for the specified order.
        """
        order = self.get_object()
        result = RecommendationService.recommend_for_order(order, persist=True)
        return Response(result.to_dict(), status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def select_box(self, request, pk=None):
        """
        Allows warehouse staff to manually confirm or override the selected box.
        Payload: {'box_id': <int>, 'notes': <str>}
        """
        order = self.get_object()
        box_id = request.data.get('box_id')
        notes = request.data.get('notes', '')

        if not box_id:
            return Response({'error': 'box_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        box = get_object_or_404(Box, id=box_id)
        order.selected_box = box
        if notes:
            order.packing_notes = notes
        order.status = 'PACKED'
        order.save(update_fields=['selected_box', 'packing_notes', 'status', 'updated_at'])

        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)


class PackingLogViewSet(viewsets.ReadOnlyModelViewSet):
    """API for viewing packing recommendation history and audit logs."""
    queryset = PackingLog.objects.select_related('order', 'recommended_box').all()
    serializer_class = PackingLogSerializer


class RecommendBoxAPIView(APIView):
    """
    Direct Box Recommendation API endpoint:
    Accepts:
    1. Custom items payload:
       {
           "items": [
               {"name": "Book", "length": 20, "width": 15, "height": 3, "weight": 0.5, "quantity": 2},
               {"name": "Mug", "length": 12, "width": 10, "height": 10, "weight": 0.4, "quantity": 1}
           ],
           "box_ids": [1, 2, 3] (optional filter)
       }
    OR
    2. Order reference payload:
       {
           "order_id": 1
       }
    """
    def post(self, request, *args, **kwargs):
        order_id = request.data.get('order_id')
        if order_id:
            try:
                order = Order.objects.prefetch_related('items__product').get(id=order_id)
            except Order.DoesNotExist:
                return Response({'error': f'Order with id {order_id} not found.'}, status=status.HTTP_404_NOT_FOUND)

            result = RecommendationService.recommend_for_order(order, persist=True)
            return Response(result.to_dict(), status=status.HTTP_200_OK)

        serializer = AdHocPackingRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        items_data = serializer.validated_data['items']
        box_ids = serializer.validated_data.get('box_ids', None)

        result = RecommendationService.recommend_for_custom_items(
            raw_items=items_data,
            specific_box_ids=box_ids if box_ids else None
        )
        return Response(result.to_dict(), status=status.HTTP_200_OK)


# ==============================================================================
# WAREHOUSE WEB UI VIEWS
# ==============================================================================

class DashboardView(TemplateView):
    """Warehouse operations overview dashboard."""
    template_name = 'boxes/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_boxes'] = Box.objects.filter(is_active=True).count()
        ctx['total_products'] = Product.objects.count()
        ctx['pending_orders'] = Order.objects.filter(status='PENDING').count()
        ctx['packed_orders'] = Order.objects.filter(status='PACKED').count()
        ctx['recent_orders'] = Order.objects.prefetch_related('items__product').select_related('recommended_box')[:8]
        ctx['recent_logs'] = PackingLog.objects.select_related('order', 'recommended_box')[:6]
        return ctx


class OrderListView(ListView):
    """List of warehouse customer orders."""
    model = Order
    template_name = 'boxes/order_list.html'
    context_object_name = 'orders'
    paginate_by = 15

    def get_queryset(self):
        qs = Order.objects.prefetch_related('items__product').select_related('recommended_box', 'selected_box')
        status_filter = self.request.GET.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs.order_by('-created_at')


class OrderDetailView(DetailView):
    """Detailed packing view for a specific order."""
    model = Order
    template_name = 'boxes/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.prefetch_related('items__product').select_related('recommended_box', 'selected_box')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        order = self.object
        # Compute fresh recommendation if not evaluated or on request
        rec_result = RecommendationService.recommend_for_order(order, persist=False)
        ctx['recommendation'] = rec_result
        ctx['available_boxes'] = Box.objects.filter(is_active=True).order_by('cost')
        ctx['latest_log'] = order.packing_logs.first()
        return ctx

    def post(self, request, *args, **kwargs):
        order = self.get_object()
        action_type = request.POST.get('action')

        if action_type == 'run_recommendation':
            rec_result = RecommendationService.recommend_for_order(order, persist=True)
            messages.success(request, f"Recommendation updated: {rec_result.message}")
            return redirect('boxes:order_detail', pk=order.pk)

        elif action_type == 'select_box':
            box_id = request.POST.get('box_id')
            notes = request.POST.get('notes', '')
            if box_id:
                box = get_object_or_404(Box, id=box_id)
                order.selected_box = box
                order.status = 'PACKED'
                order.packing_notes = notes
                order.save(update_fields=['selected_box', 'status', 'packing_notes', 'updated_at'])
                messages.success(request, f"Box '{box.name}' confirmed for Order #{order.order_number}.")
            return redirect('boxes:order_detail', pk=order.pk)

        return redirect('boxes:order_detail', pk=order.pk)


class InteractiveRecommenderView(TemplateView):
    """Interactive sandbox tool for warehouse packers to test arbitrary items or products."""
    template_name = 'boxes/recommender.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['products'] = Product.objects.all().order_by('name')
        ctx['boxes'] = Box.objects.filter(is_active=True).order_by('cost')
        return ctx


class BoxListView(ListView):
    """Catalog of shipping box types."""
    model = Box
    template_name = 'boxes/box_list.html'
    context_object_name = 'boxes'

    def get_queryset(self):
        return Box.objects.all().order_by('cost', 'name')


class ProductListView(ListView):
    """Catalog of ecommerce products."""
    model = Product
    template_name = 'boxes/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        return Product.objects.all().order_by('name')
