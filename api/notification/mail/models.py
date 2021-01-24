import notification.utils as utils

from django.db import models


generate_table_name = utils.Helpers.generate_table_name('mail')


class SentMail(utils.AbstractModel):
    from_email = models.CharField(max_length=100)
    recipient = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    message = models.CharField(max_length=1000)

    class Meta:
        db_table = generate_table_name('sent_mail')

    def __str__(self):
        return f'{self.from_email} - {self.recipient} - {self.subject}'
