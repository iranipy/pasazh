# Generated by Django 3.1.3 on 2020-11-30 16:52

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
                ('uid', models.CharField(max_length=4)),
                ('name', models.CharField(max_length=50)),
                ('is_public', models.BooleanField(default=False)),
                ('user_uid', models.CharField(blank=True, max_length=8, null=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main_app.category')),
            ],
            options={
                'db_table': 'category',
            },
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=50)),
                ('user_uid', models.CharField(blank=True, max_length=8, null=True)),
                ('is_public', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'option',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
                ('uid', models.CharField(max_length=18)),
                ('name', models.CharField(max_length=50)),
                ('count', models.IntegerField()),
                ('description', models.TextField(max_length=1000)),
                ('price', models.FloatField()),
                ('rate', models.FloatField()),
                ('rate_count', models.IntegerField()),
                ('view_count', models.IntegerField()),
                ('thumbnail', models.BinaryField(null=True, validators=[django.core.validators.validate_image_file_extension])),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.category')),
            ],
            options={
                'db_table': 'product',
            },
        ),
        migrations.CreateModel(
            name='ProductAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
                ('type', models.CharField(max_length=50)),
                ('content', models.BinaryField()),
                ('size', models.IntegerField()),
                ('description', models.TextField(max_length=100)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.product')),
            ],
            options={
                'db_table': 'product_attachment',
            },
        ),
        migrations.CreateModel(
            name='OptionValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
                ('value', models.CharField(max_length=50)),
                ('is_public', models.BooleanField(default=False)),
                ('product_option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.option')),
            ],
            options={
                'db_table': 'option_value',
            },
        ),
        migrations.AddField(
            model_name='option',
            name='product',
            field=models.ManyToManyField(to='main_app.Product'),
        ),
    ]
