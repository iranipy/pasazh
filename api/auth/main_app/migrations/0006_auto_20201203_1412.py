# Generated by Django 3.1.3 on 2020-12-03 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0005_salesman_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otp',
            name='expire',
            field=models.BigIntegerField(),
        ),
    ]
