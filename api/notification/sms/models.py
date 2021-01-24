import notification.utils as utils

from django.db import models
from django.core.validators import RegexValidator


generate_table_name = utils.Helpers.generate_table_name('sms')
mobile_regex = RegexValidator(regex=r'^09\d{9}$', message='Enter a valid phone number')


class SentSms(utils.AbstractModel):
    sender = models.CharField(max_length=13, validators=[mobile_regex])
    receptor = models.CharField(max_length=13, validators=[mobile_regex])
    message = models.CharField(max_length=200)
    message_id = models.BigIntegerField()
    cost = models.FloatField()
    status = models.IntegerField()
    status_text = models.CharField(max_length=200)
    sent_date = models.BigIntegerField()

    class Meta:
        db_table = generate_table_name('sent_sms')

    def __str__(self):
        return f'{self.sender} - {self.receptor} - {self.message}'
