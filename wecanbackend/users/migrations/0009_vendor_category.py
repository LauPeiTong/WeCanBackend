# Generated by Django 4.0.10 on 2024-01-17 02:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_alter_user_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='category',
            field=models.CharField(default='Restaurant', max_length=255),
            preserve_default=False,
        ),
    ]
