from django.db import models
from django.utils import timezone


class AbstractTimeModel(models.Model):
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super().save(*args, **kwargs)


class Province(AbstractTimeModel):
    name = models.CharField(max_length=50, unique=True, default='')
    fa_name = models.CharField(max_length=50, unique=True, default='')


class City(AbstractTimeModel):
    name = models.CharField(max_length=50, unique=True, default='')
    fa_name = models.CharField(max_length=50, unique=True, default='')
    code = models.CharField(max_length=5)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)


class User(AbstractTimeModel):
    mobile = models.CharField(max_length=11, unique=True)
    fullname = models.CharField(max_length=50)
    username = models.CharField(max_length=50, null=True, blank=True, unique=True)
    email = models.EmailField(null=True, blank=True, unique=True)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    city = models.ForeignKey(City, null=True, on_delete=models.SET_NULL)
    address = models.TextField(max_length=200)
    picture = models.BinaryField(null=True)


class OTP(AbstractTimeModel):
    code = models.CharField(max_length=128)
    expire = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)