# Generated by Django 5.1 on 2024-08-08 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0002_alter_stock_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='price',
            field=models.DecimalField(decimal_places=6, max_digits=12),
        ),
    ]