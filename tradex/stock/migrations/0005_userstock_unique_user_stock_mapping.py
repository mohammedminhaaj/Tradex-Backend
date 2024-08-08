# Generated by Django 5.1 on 2024-08-08 15:52

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0004_userstock_quantity'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='userstock',
            constraint=models.UniqueConstraint(fields=('user', 'stock'), name='unique_user_stock_mapping'),
        ),
    ]