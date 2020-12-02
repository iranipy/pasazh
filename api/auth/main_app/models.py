from django.db import models
from django.utils import timezone
from django.core.validators import validate_image_file_extension
from .utils import Security


def uid_generator():
    uid = Security.hex_generator()
    while User.objects.filter(uid=uid).exists():
        uid = Security.hex_generator()
    return uid


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


class Province(AbstractModel):
    name = models.CharField(max_length=50, unique=True, default='')
    fa_name = models.CharField(max_length=50, unique=True, default='')


class City(AbstractModel):
    name = models.CharField(max_length=50, unique=True, default='')
    fa_name = models.CharField(max_length=50, unique=True, default='')
    code = models.CharField(max_length=5)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)


class User(AbstractModel):
    uid = models.CharField(max_length=8, unique=True, default=uid_generator)
    mobile = models.CharField(max_length=13, unique=True)
    nick_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True, unique=True)
    score = models.IntegerField(default=100)
    picture = models.BinaryField(null=True, validators=[validate_image_file_extension])
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.mobile


class SalesMan(AbstractModel):
    choices = (
        ('ON', 'Online'),
        ('OFF', 'Offline'),
        ('ALL', 'All')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uid = models.CharField(max_length=16, unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=50, null=True, blank=True)
    username = models.CharField(max_length=20, null=True, blank=True, unique=True)
    store_name = models.CharField(max_length=50)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    city = models.ForeignKey(City, null=True, on_delete=models.SET_NULL)
    address = models.TextField(max_length=200)
    open_time = models.TimeField()
    close_time = models.TimeField()
    working_days = models.CharField(max_length=27)
    activity_type = models.CharField(max_length=3, choices=choices)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.user.mobile


class OTP(AbstractModel):
    code = models.CharField(max_length=128)
    expire = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class BlackList(AbstractModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    banned_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='banned_user')


class Following(AbstractModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    followed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed_user')
