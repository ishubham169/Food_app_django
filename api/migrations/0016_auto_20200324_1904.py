# Generated by Django 2.0.13 on 2020-03-24 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_food_orders'),
    ]

    operations = [
        migrations.AlterField(
            model_name='food',
            name='food_type',
            field=models.CharField(max_length=10),
        ),
    ]
