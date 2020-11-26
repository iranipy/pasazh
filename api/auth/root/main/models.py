from django.db import models
from django.utils import timezone

class Province(models.Model):
    name = models.CharField(max_length=50)
    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Province, self).save(*args, **kwargs)


class City(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=5)
    povince = models.ForeignKey(Province, on_delete=models.CASCADE)
    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(City, self).save(*args, **kwargs)

class User(models.Model):
    mobile = models.CharField(max_length=11, unique=True)
    fullname = models.CharField(max_length=50)
    username = models.CharField(max_length=50, null=True, blank=True, unique=True)
    email = models.EmailField(null=True, blank=True, unique=True)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    city = models.ForeignKey(City, null=True, on_delete=models.SET_NULL)
    address = models.TextField(max_length=200)
    picture = models.BinaryField(null=True)
    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(User, self).save(*args, **kwargs)


class OTP(models.Model):
    code = models.CharField(max_length=128)
    expire = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(OTP, self).save(*args, **kwargs)
