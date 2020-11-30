from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, validate_image_file_extension
from .utils import hex_generator


def uid_generator():
    uid = hex_generator()
    while User.objects.filter(uid=uid).exists():
        uid = hex_generator()
    return uid


class AbstractTimeModel(models.Model):
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


class Province(AbstractTimeModel):
    name = models.CharField(max_length=50, unique=True, default='')
    fa_name = models.CharField(max_length=50, unique=True, default='')


class City(AbstractTimeModel):
    name = models.CharField(max_length=50, unique=True, default='')
    fa_name = models.CharField(max_length=50, unique=True, default='')
    code = models.CharField(max_length=5)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)


class User(AbstractTimeModel):
    uid = models.CharField(max_length=8, unique=True, default=uid_generator)
    seller_uid = models.CharField(max_length=16, unique=True, null=True, blank=True)
    mobile = models.CharField(max_length=13, unique=True, validators=[RegexValidator(r'^(\+98|0)?9\d{9}$]$')])
    fullname = models.CharField(max_length=50)
    username = models.CharField(max_length=20, null=True, blank=True, unique=True)
    email = models.EmailField(null=True, blank=True, unique=True)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    city = models.ForeignKey(City, null=True, on_delete=models.SET_NULL)
    address = models.TextField(max_length=200)
    picture = models.BinaryField(null=True, validators=[validate_image_file_extension])
    is_deleted = models.BooleanField(default=False)
    


class OTP(AbstractTimeModel):
    code = models.CharField(max_length=128)
    expire = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class BlackList(AbstractTimeModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    banned_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='banned_user')


class Following(AbstractTimeModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    followed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed_user')