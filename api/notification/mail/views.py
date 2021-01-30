from notification.utils import MetaApiViewClass, JsonValidation

from os import getenv
from smtplib import SMTPException
from django.core.mail import BadHeaderError, send_mail, send_mass_mail

from .models import SentMail


class SendMail(MetaApiViewClass):
    __email_host_user = getenv("EMAIL_HOST_USER")

    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data

        from_email = self.__email_host_user
        recipient = data['recipient']
        subject = data['subject']
        message = data['message']

        try:
            res = send_mail(subject, message, from_email, [recipient])
            if not res:
                raise SMTPException

            SentMail.objects.create(
                from_email=from_email, recipient=recipient,
                message=message, subject=subject
            ).save()

        except (SMTPException, BadHeaderError) as e:
            return self.internal_error(message=[6, str(e)])

        return self.success(message=[5])


class SendMassMail(MetaApiViewClass):
    __email_host_user = getenv("EMAIL_HOST_USER")

    # @MetaApiViewClass.generic_decor()
    # @JsonValidation.validate
    def post(self, requests):
        data = self.request.data
        from_email = self.__email_host_user
        recipients = data['recipients']
        subject = data['subject']
        message = data['message']
        final_message = (subject, message, from_email, recipients)
        try:
            res = send_mass_mail((final_message,), fail_silently=False)
            if not res:
                raise SMTPException
            entries = [SentMail(from_email=from_email, message=message,
                                subject=subject, recipient=rec_email) for rec_email in recipients]
            SentMail.objects.bulk_create(entries)

        except (SMTPException, BadHeaderError) as e:
            return self.internal_error(message=[6, str(e)])

        return self.success(message=[5])
