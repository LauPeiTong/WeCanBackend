# Generated by Django 4.0.10 on 2024-01-17 02:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_vendor_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='category',
            field=models.CharField(choices=[('Restaurant', 'Restaurant'), ('Convenient Store', 'Convenient Store')], max_length=255),
        ),
    ]