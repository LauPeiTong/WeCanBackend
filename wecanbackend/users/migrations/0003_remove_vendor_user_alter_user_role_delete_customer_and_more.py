# Generated by Django 4.0.10 on 2024-01-12 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_customer_user_alter_vendor_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vendor',
            name='user',
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('C', 'Customer'), ('V', 'Vendor'), ('A', 'Admin')], max_length=15),
        ),
        migrations.DeleteModel(
            name='Customer',
        ),
        migrations.DeleteModel(
            name='Vendor',
        ),
    ]
