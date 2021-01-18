import datetime

import auth.utils as utils

from django.db import models
from django.core.validators import validate_image_file_extension, RegexValidator


def generate_table_name(name: str):
    prefix = 'root'
    return f'{prefix}_{name}'


def generate_decimal_uid():
    try:
        job_category = JobCategory.objects.order_by('-created_at')[0]
        uid = utils.ResponseUtils.add_lead_zero(str(int(job_category.uid) + 1), 4)
    except IndexError:
        uid = utils.ResponseUtils.add_lead_zero('1', 4)
    return uid


def generate_hex_uid():
    uid = utils.Security.generate_hex(4)
    while User.objects.filter(uid=uid).exists():
        uid = utils.Security.generate_hex(4)
    return uid


class AbstractModel(models.Model):
    created_at = models.DateTimeField(default=datetime.datetime.utcnow)
    modified_at = models.DateTimeField(default=datetime.datetime.utcnow)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()
        return super().save(*args, **kwargs)


class Province(AbstractModel):
    name = models.CharField(max_length=50, unique=True)
    fa_name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = generate_table_name('province')

    def __str__(self):
        return self.name


class City(AbstractModel):
    name = models.CharField(max_length=50, unique=True)
    fa_name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=5)
    province = models.ForeignKey(Province, on_delete=models.RESTRICT)

    class Meta:
        db_table = generate_table_name('city')

    def __str__(self):
        return f'{self.province.name} - {self.name} ({self.code})'


class JobCategory(AbstractModel):
    uid = models.CharField(max_length=4, unique=True, default=generate_decimal_uid)
    name = models.CharField(max_length=50, unique=True, default='')

    class Meta:
        db_table = generate_table_name('job_category')

    def __str__(self):
        return self.name


class User(AbstractModel):
    uid = models.CharField(max_length=8, unique=True, default=generate_hex_uid)
    mobile = models.CharField(
        max_length=13,
        validators=[RegexValidator(regex=r'^09\d{9}$', message='Enter a valid phone number')]
    )
    nick_name = models.CharField(max_length=50)
    email = models.EmailField(null=True, blank=True)
    score = models.IntegerField(default=100)
    picture = models.BinaryField(null=True, validators=[validate_image_file_extension])
    is_deleted = models.BooleanField(default=False)
    deleted_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = generate_table_name('user')
        constraints = [
            models.UniqueConstraint(
                fields=['mobile', 'deleted_date'],
                name='deleted_user'
            )
        ]

    def __str__(self):
        return f'{self.mobile} ({self.id})'


class SalesMan(AbstractModel):
    choices = (
        ('ON', 'Online'),
        ('OFF', 'Offline'),
        ('ALL', 'All')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_category = models.ForeignKey(JobCategory, on_delete=models.RESTRICT)
    job_category_description = models.CharField(max_length=50, null=True, blank=True)
    uid = models.CharField(max_length=18, unique=True)
    full_name = models.CharField(max_length=50, null=True, blank=True)
    username = models.CharField(max_length=20, null=True, blank=True, unique=True)
    store_name = models.CharField(max_length=50)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.RESTRICT)
    address = models.TextField(max_length=200)
    open_time = models.TimeField()
    close_time = models.TimeField()
    working_days = models.CharField(max_length=27)
    activity_type = models.CharField(max_length=3, choices=choices)
    is_private = models.BooleanField(default=False)

    class Meta:
        db_table = generate_table_name('sales_man')

    def __str__(self):
        return f'{self.store_name} - {self.user.mobile} ({self.user.id})'


class OTP(AbstractModel):
    code = models.CharField(max_length=16)
    expire = models.BigIntegerField()
    try_count = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = generate_table_name('otp')

    def __str__(self):
        return f'{self.user.mobile} ({self.code})'


class BlackList(AbstractModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    banned_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='banned_user')

    class Meta:
        db_table = generate_table_name('black_list')

    def __str__(self):
        return f'{self.user.mobile} ({self.banned_user.id})'


class Following(AbstractModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    followed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed_user')

    class Meta:
        db_table = generate_table_name('following')

    def __str__(self):
        return f'{self.user.mobile} ({self.followed_user.id})'