# Generated by Django 4.0.10 on 2024-01-15 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_alter_product_vendor'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='status',
            field=models.CharField(choices=[('Expired', 'Expired'), ('Not Expired', 'Not Expired')], default='Not Expired', max_length=20),
        ),
    ]
