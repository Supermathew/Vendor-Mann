# vendors/views.py

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from datetime import datetime,timezone

from vendorapp.models import Vendor, PurchaseOrder
from .serializers import VendorSerializer,PurchaseOrderSerializer

class VendorListCreateView(generics.ListCreateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

class VendorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        po_id = kwargs.get('pod_id')

        try:
            print("hello")
            instance = PurchaseOrder.objects.get(id = po_id)
        except :
            return Response({'detail': 'No po order with this ide .'}, status=status.HTTP_400_BAD_REQUEST)
        print(po_id)
        if po_id:
            instance.vendor.acknowledge_purchase_order(po_id)
            return Response({'detail': 'Purchase Order acknowledged successfully'}, status=status.HTTP_200_OK)
        else:
            print("hello")
            return Response({'detail': 'Missing po_id in request data'}, status=status.HTTP_400_BAD_REQUEST)


class PurchaseOrderListCreateView(generics.ListCreateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

    def get_queryset(self):
        vendor_id = self.request.query_params.get('vendor_id')
        if vendor_id:
            return PurchaseOrder.objects.filter(vendor_id=vendor_id)
        else:
            return PurchaseOrder.objects.all()

class PurchaseOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        acknowledgment_date = instance.acknowledgment_date
        new_delivery_date = request.data.get('delivery_date')


        try:
            new_delivery_date = datetime.strptime(new_delivery_date, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except ValueError:
            return Response({'detail': 'Invalid date format for delivery date.'}, status=status.HTTP_400_BAD_REQUEST)

        if acknowledgment_date is None:
            return Response({'detail': 'Purchase Order must be acknowledged before updating delivery date.'}, status=status.HTTP_400_BAD_REQUEST)

        if new_delivery_date < acknowledgment_date:
            return Response({'detail': 'New delivery date must be equal to or greater than the acknowledgment date.'}, status=status.HTTP_400_BAD_REQUEST)

        return super().update(request, *args, **kwargs)

