from config.utils import AbstractModel
from django.db import models


class ConfigMessages(AbstractModel):
    name = models.CharField(max_length=50, unique=True)
    value = models.CharField(max_length=200)
    is_editable = models.BooleanField()

    def __str__(self):
        return self.name
