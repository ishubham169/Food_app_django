# Generated by Django 2.0.13 on 2020-03-23 19:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_auto_20200322_0859'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='user_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.Users'),
        ),
    ]
