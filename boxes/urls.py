from django.urls import path, include
from rest_framework.routers import DefaultRouter

from boxes.views import (
    ProductViewSet,
    BoxViewSet,
    OrderViewSet,
    PackingLogViewSet,
    RecommendBoxAPIView,
    DashboardView,
    OrderListView,
    OrderDetailView,
    InteractiveRecommenderView,
    BoxListView,
    ProductListView,
)

app_name = 'boxes'

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='api-product')
router.register(r'boxes', BoxViewSet, basename='api-box')
router.register(r'orders', OrderViewSet, basename='api-order')
router.register(r'packing-logs', PackingLogViewSet, basename='api-packing-log')

urlpatterns = [
    # Web UI URLs
    path('', DashboardView.as_view(), name='dashboard'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('recommender/', InteractiveRecommenderView.as_view(), name='recommender'),
    path('boxes/', BoxListView.as_view(), name='box_list'),
    path('products/', ProductListView.as_view(), name='product_list'),

    # REST API URLs
    path('api/', include(router.urls)),
    path('api/recommend/', RecommendBoxAPIView.as_view(), name='api-recommend-box'),
]
