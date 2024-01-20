# Generated by Django 4.0.10 on 2024-01-20 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_product_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(blank=True, default='Food', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
