# Generated by Django 4.2.7 on 2023-11-24 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vendorapp", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="purchaseorder",
            name="delivery_date",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Expected or actual delivery date of the order",
            ),
        ),
        migrations.AlterField(
            model_name="purchaseorder",
            name="issue_date",
            field=models.DateTimeField(
                auto_now_add=True,
                verbose_name="Timestamp when the PO was issued to the vendor",
            ),
        ),
        migrations.AlterField(
            model_name="purchaseorder",
            name="order_date",
            field=models.DateTimeField(
                auto_now_add=True, verbose_name="Date when the order was placed"
            ),
        ),
    ]
