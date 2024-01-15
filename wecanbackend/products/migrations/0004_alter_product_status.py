# Generated by Django 4.0.10 on 2024-01-15 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_product_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.CharField(choices=[('Expired', 'Expired'), ('Within Shelf Life', 'Within Shelf Life'), ('Near Expiry', 'Near Expiry')], default='Within Shelf Life', max_length=20),
        ),
    ]
