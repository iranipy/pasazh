from django.db import models
from django.utils import timezone
from django.core.validators import validate_image_file_extension


class AbstractModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)
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
    parent = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)
    is_public = models.BooleanField(default=False)
    user_uid = models.CharField(max_length=8, null=True, blank=True)

    class Meta:
        db_table = 'category'


class Product(AbstractModel):
    uid = models.CharField(max_length=18)
    name = models.CharField(max_length=50)
    count = models.IntegerField()
    description = models.TextField(max_length=1000)
    price = models.FloatField()
    rate = models.FloatField(null=True, blank=True)
    rate_count = models.IntegerField(null=True, blank=True)
    view_count = models.IntegerField(default=1)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    thumbnail = models.BinaryField(null=True, validators=[validate_image_file_extension])

    class Meta:
        db_table = 'product'


class ProductAttachment(AbstractModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    content = models.BinaryField()
    size = models.IntegerField()
    description = models.TextField(max_length=100)

    class Meta:
        db_table = 'product_attachment'


class Option(AbstractModel):
    name = models.CharField(max_length=50)
    user_uid = models.CharField(max_length=8, null=True, blank=True)
    is_public = models.BooleanField(default=False)
    product = models.ManyToManyField(Product)

    class Meta:
        db_table = 'option'


class OptionValue(AbstractModel):
    value = models.CharField(max_length=50)
    product_option = models.ForeignKey(Option, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=False)

    class Meta:
        db_table = 'option_value'
