# vendors/models.py

from django.db import models
from django.db.models import Count, Avg, F, ExpressionWrapper, FloatField, Q
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.db.models.functions import Coalesce
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

class Vendor(models.Model):
    name = models.CharField(max_length=255, verbose_name="Vendor's name")
    contact_details = models.TextField(verbose_name="Contact information of the vendor")
    address = models.TextField(verbose_name="Physical address of the vendor")
    on_time_delivery_rate = models.FloatField(null=True, blank=True, verbose_name="On-Time Delivery Rate")
    quality_rating_avg = models.FloatField(null=True, blank=True, verbose_name="Average rating of quality based on purchase orders")
    average_response_time = models.FloatField(null=True, blank=True, verbose_name="Average time taken to acknowledge purchase orders")
    fulfillment_rate = models.FloatField(null=True, blank=True, verbose_name="Percentage of purchase orders fulfilled successfully")

    def calculate_on_time_delivery_rate(self):
        completed_pos = self.purchaseorder_set.filter(status='completed')
        total_completed_pos = completed_pos.count()
        on_time_delivery_pos = completed_pos.filter(delivery_date__lte=F('delivery_date'))
        on_time_delivery_rate = on_time_delivery_pos.count() / total_completed_pos * 100 if total_completed_pos > 0 else 0
        return on_time_delivery_rate

    def calculate_quality_rating_avg(self):
        completed_pos_with_rating = self.purchaseorder_set.filter(status='completed', quality_rating__isnull=False)
        quality_rating_avg = completed_pos_with_rating.aggregate(avg_rating=Coalesce(Avg('quality_rating', output_field=FloatField()), 0.0))['avg_rating']      
        return quality_rating_avg

    def calculate_average_response_time(self):
        acknowledged_pos = self.purchaseorder_set.filter(acknowledgment_date__isnull=False)
        response_times = [(po.acknowledgment_date - po.issue_date).seconds/3600 for po in acknowledged_pos]
        average_response_time = sum(response_times) / len(response_times) if len(response_times) > 0 else 0
        average_response_time = round(average_response_time, 2)
        return average_response_time

    def calculate_fulfillment_rate(self):
        total_pos = self.purchaseorder_set.count()
        completed_pos = self.purchaseorder_set.filter(status='completed')
        # quality_rating__isnull=True
        fulfillment_rate = completed_pos.count() / total_pos * 100 if total_pos > 0 else 0
        return fulfillment_rate

    def update_performance_metrics(self):
        self.on_time_delivery_rate = self.calculate_on_time_delivery_rate()
        self.quality_rating_avg = self.calculate_quality_rating_avg()
        self.average_response_time = self.calculate_average_response_time()
        self.fulfillment_rate = self.calculate_fulfillment_rate()
        self.save()

    def get_performance_metrics(self):
        return {
            'on_time_delivery_rate': self.on_time_delivery_rate,
            'quality_rating_avg': self.quality_rating_avg,
            'average_response_time': self.average_response_time,
            'fulfillment_rate': self.fulfillment_rate,
        }

    @classmethod
    def retrieve_vendor_performance(cls, vendor_id):
        vendor = cls.objects.get(id=vendor_id)
        return vendor.get_performance_metrics()

    def acknowledge_purchase_order(self, po_id):
        po = self.purchaseorder_set.get(id=po_id)
        po.acknowledgment_date = timezone.now()
        po.save()
        self.update_performance_metrics()


class PurchaseOrder(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, verbose_name="Link to the Vendor model")
    order_date = models.DateTimeField(auto_now_add=True,verbose_name="Date when the order was placed")
    delivery_date = models.DateTimeField(null=True, blank=True,verbose_name="Expected or actual delivery date of the order")
    items = models.JSONField(verbose_name="Details of items ordered")
    quantity = models.IntegerField(verbose_name="Total quantity of items in the PO")
    status = models.CharField(max_length=50, verbose_name="Current status of the PO", choices=[('pending', 'Pending'), ('completed', 'Completed'), ('canceled', 'Canceled')])
    quality_rating = models.FloatField(null=True, blank=True, verbose_name="Rating given to the vendor for this PO")
    issue_date = models.DateTimeField(auto_now_add=True,verbose_name="Timestamp when the PO was issued to the vendor")
    acknowledgment_date = models.DateTimeField(null=True, blank=True, verbose_name="Timestamp when the vendor acknowledged the PO")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.vendor:
            self.vendor.update_performance_metrics()

    def __str__(self):
        formatted_order_date = self.order_date.strftime("%b %d, %Y %H:%M:%S")
        formatted_delivery_date = self.delivery_date.strftime("%b %d, %Y %H:%M:%S") if self.delivery_date else None
        formatted_issue_date = self.issue_date.strftime("%b %d, %Y %H:%M:%S")
        formatted_acknowledgment_date = self.acknowledgment_date.strftime("%b %d, %Y %H:%M:%S") if self.acknowledgment_date else None

        return f"Order Date: {formatted_order_date}, Delivery Date: {formatted_delivery_date}, Issue Date: {formatted_issue_date}, Acknowledgment Date: {formatted_acknowledgment_date}"



class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, verbose_name="Link to the Vendor model")
    date = models.DateTimeField(verbose_name="Date of the performance record")
    on_time_delivery_rate = models.FloatField(verbose_name="Historical record of the on-time delivery rate")
    quality_rating_avg = models.FloatField(verbose_name="Historical record of the quality rating average")
    average_response_time = models.FloatField(verbose_name="Historical record of the average response time")
    fulfillment_rate = models.FloatField(verbose_name="Historical record of the fulfilment rate")

    def __str__(self):
        return f"Performance record for {self.vendor.name} on {self.date}"


@receiver(post_save, sender=PurchaseOrder)
@receiver(post_delete, sender=PurchaseOrder)
def update_vendor_performance_metrics(sender, instance, **kwargs):
    if instance.vendor:
        instance.vendor.update_performance_metrics()
