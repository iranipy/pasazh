from django.db import models
from main_app.models import *


class AbstractSaleModel(AbstractModel):
    choices = (
        ('A', 'All'),
        ('F', 'Followers'),
    )
    percentage = models.FloatField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    receiver = models.CharField(max_length=1, choices=choices)
    user_score = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract =True


class CategorySale(AbstractSaleModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        db_table = 'category_sale'


class ProductSale(AbstractSaleModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        db_table = 'product_sale'
