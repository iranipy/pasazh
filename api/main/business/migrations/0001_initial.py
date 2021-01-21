# Generated by Django 3.1.3 on 2021-01-21 09:31

import datetime
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=datetime.datetime.utcnow)),
                ('modified_at', models.DateTimeField(default=datetime.datetime.utcnow)),
                ('is_active', models.BooleanField(default=True)),
                ('uid', models.CharField(max_length=4, unique=True)),
                ('name', models.CharField(max_length=50)),
                ('is_public', models.BooleanField(default=False)),
                ('user_uid', models.CharField(blank=True, max_length=8, null=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='business.category')),
            ],
            options={
                'db_table': 'business_category',
            },
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=datetime.datetime.utcnow)),
                ('modified_at', models.DateTimeField(default=datetime.datetime.utcnow)),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=50)),
                ('user_uid', models.CharField(blank=True, max_length=8, null=True)),
                ('is_public', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'business_option',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=datetime.datetime.utcnow)),
                ('modified_at', models.DateTimeField(default=datetime.datetime.utcnow)),
                ('is_active', models.BooleanField(default=True)),
                ('uid', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=80)),
                ('quantity', models.IntegerField()),
                ('description', models.TextField(max_length=1000)),
                ('price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('rate', models.FloatField(default=0)),
                ('rate_count', models.IntegerField(default=0)),
                ('view_count', models.IntegerField(default=0)),
                ('thumbnail', models.BinaryField(null=True, validators=[django.core.validators.validate_image_file_extension])),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='business.category')),
            ],
            options={
                'db_table': 'business_product',
            },
        ),
        migrations.CreateModel(
            name='ProductAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=datetime.datetime.utcnow)),
                ('modified_at', models.DateTimeField(default=datetime.datetime.utcnow)),
                ('is_active', models.BooleanField(default=True)),
                ('type', models.CharField(max_length=50)),
                ('content', models.BinaryField()),
                ('size', models.IntegerField()),
                ('description', models.TextField(max_length=100)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='business.product')),
            ],
            options={
                'db_table': 'business_product_attachment',
            },
        ),
        migrations.CreateModel(
            name='OptionValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=datetime.datetime.utcnow)),
                ('modified_at', models.DateTimeField(default=datetime.datetime.utcnow)),
                ('is_active', models.BooleanField(default=True)),
                ('value', models.CharField(max_length=50)),
                ('is_public', models.BooleanField(default=False)),
                ('option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='business.option')),
            ],
            options={
                'db_table': 'business_option_value',
            },
        ),
        migrations.AddField(
            model_name='option',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='business.product'),
        ),
        migrations.AddConstraint(
            model_name='product',
            constraint=models.UniqueConstraint(fields=('category', 'name'), name='product_name'),
        ),
        migrations.AddConstraint(
            model_name='optionvalue',
            constraint=models.UniqueConstraint(fields=('option', 'value'), name='option_value'),
        ),
        migrations.AddConstraint(
            model_name='option',
            constraint=models.UniqueConstraint(fields=('user_uid', 'product', 'name'), name='option_name'),
        ),
        migrations.AddConstraint(
            model_name='category',
            constraint=models.UniqueConstraint(fields=('user_uid', 'name', 'parent'), name='category_name'),
        ),
    ]
