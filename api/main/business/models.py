from main.utils import AbstractModel, Helpers
from django.db import models
from django.core.validators import validate_image_file_extension


generate_table_name = Helpers.generate_table_name('business')


class Category(AbstractModel):
    uid = models.CharField(max_length=4, unique=True)
    name = models.CharField(max_length=50)
    parent = models.ForeignKey('Category', on_delete=models.RESTRICT, null=True, blank=True)
    is_public = models.BooleanField(default=False)
    user_uid = models.CharField(max_length=8, null=True, blank=True)

    class Meta:
        db_table = generate_table_name('category')
        constraints = [
            models.UniqueConstraint(
                fields=['user_uid', 'name', 'parent'],
                name='category_name'
            )
        ]

    def __str__(self):
        return self.name


class Product(AbstractModel):
    uid = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=80)
    quantity = models.IntegerField()
    description = models.TextField(max_length=1000)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    rate = models.FloatField(default=0)
    rate_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.RESTRICT)
    thumbnail = models.BinaryField(null=True, validators=[validate_image_file_extension])

    class Meta:
        db_table = generate_table_name('product')
        constraints = [
            models.UniqueConstraint(
                fields=['category', 'name'],
                name='product_name'
            )
        ]

    def __str__(self):
        return self.name


class ProductAttachment(AbstractModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    content = models.BinaryField()
    size = models.IntegerField()
    description = models.TextField(max_length=100)

    class Meta:
        db_table = generate_table_name('product_attachment')

    def __str__(self):
        return f'{self.product} - {self.type} ({self.size})'


class Option(AbstractModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    user_uid = models.CharField(max_length=8, null=True, blank=True)
    is_public = models.BooleanField(default=False)

    class Meta:
        db_table = generate_table_name('option')
        constraints = [
            models.UniqueConstraint(
                fields=['user_uid', 'product', 'name'],
                name='option_name'
            )
        ]

    def __str__(self):
        return self.name


class OptionValue(AbstractModel):
    value = models.CharField(max_length=50)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=False)

    class Meta:
        db_table = generate_table_name('option_value')
        constraints = [
            models.UniqueConstraint(
                fields=['option', 'value'],
                name='option_value'
            )
        ]

    def __str__(self):
        return f'{self.option.name} - {self.value}'
