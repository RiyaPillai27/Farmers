# Generated by Django 4.2.5 on 2023-11-06 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farmer_app', '0003_cart'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='qty',
            field=models.IntegerField(default=1),
        ),
    ]
