# Generated by Django 3.1.3 on 2020-12-08 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0006_auto_20201203_1412'),
    ]

    operations = [
        migrations.AddField(
            model_name='otp',
            name='try_count',
            field=models.IntegerField(default=0),
        ),
    ]
