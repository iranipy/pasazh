# Generated by Django 3.1.3 on 2021-01-09 07:42

from django.db import migrations, models
import main_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0002_auto_20210109_1050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_deleted_uid',
            field=models.CharField(blank=True, max_length=8, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='mobile',
            field=models.CharField(max_length=13),
        ),
        migrations.AlterField(
            model_name='user',
            name='uid',
            field=models.CharField(default=main_app.models.uid_generator, max_length=8, unique=True),
        ),
    ]