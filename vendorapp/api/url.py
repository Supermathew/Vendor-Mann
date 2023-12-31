# vendors/urls.py

from django.urls import path
from .views import VendorListCreateView, VendorDetailView, PurchaseOrderListCreateView, PurchaseOrderDetailView

urlpatterns = [
    path('api/vendors/', VendorListCreateView.as_view(), name='vendor-list-create'),
    path('api/vendors/<int:pk>/', VendorDetailView.as_view(), name='vendor-detail'),
    path('api/vendors/<int:pk>/performance/', VendorDetailView.as_view(), name='vendor-performanceeeee'),
    path('api/vendors/purchase_orders/<int:pod_id>/acknowledge/', VendorDetailView.as_view(), name='acknowledge-purchase-order'),
    path('api/purchase_orders/', PurchaseOrderListCreateView.as_view(), name='purchase-order-list-create'),
    path('api/purchase_orders/<int:pk>/', PurchaseOrderDetailView.as_view(), name='purchase-order-detail'),
]
