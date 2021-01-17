import datetime

from django.db import models
from django.utils import timezone
from django.core.validators import validate_image_file_extension


def gen_table_name(name: str):
    prefix = 'main_app'
    return f'{prefix}_{name}'


class AbstractModel(models.Model):
    created_at = models.DateTimeField(default=datetime.datetime.utcnow)
    modified = models.DateTimeField(default=datetime.datetime.utcnow)
    # created_by = models.ForeignKey(User, on_delete=models.SET_NULL)
    # modified_by = models.ForeignKey(User, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super().save(*args, **kwargs)


class Category(AbstractModel):
    uid = models.CharField(max_length=4)
    name = models.CharField(max_length=50)
    parent = models.ForeignKey('Category', on_delete=models.RESTRICT, null=True, blank=True)
    is_public = models.BooleanField(default=False)
    user_uid = models.CharField(max_length=8, null=True, blank=True)

    class Meta:
        db_table = gen_table_name('category')

    def __str__(self):
        return self.name


class Product(AbstractModel):
    uid = models.CharField(max_length=20)
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
        db_table = gen_table_name('product')

    def __str__(self):
        return self.name


class ProductAttachment(AbstractModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    content = models.BinaryField()
    size = models.IntegerField()
    description = models.TextField(max_length=100)

    class Meta:
        db_table = gen_table_name('product_attachment')

    def __str__(self):
        return f'{self.product} - {self.type} ({self.size})'


class Option(AbstractModel):
    name = models.CharField(max_length=50)
    user_uid = models.CharField(max_length=8, null=True, blank=True)
    is_public = models.BooleanField(default=False)
    product = models.ManyToManyField(Product)

    class Meta:
        db_table = gen_table_name('option')

    def __str__(self):
        return self.name


class OptionValue(AbstractModel):
    value = models.CharField(max_length=50)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=False)

    class Meta:
        db_table = gen_table_name('option_value')

    def __str__(self):
        return f'{self.option.name} - {self.value}'
