from sms.utils import MetaApiViewClass
from django.core.mail import send_mail


class SendEmail(MetaApiViewClass):
    def post(self, request):
        data = self.request.data
        subject = data['subject']
        body = data['body']
        from_addr = data['from']
        to_addr = data['to']
        send_mail(subject, body, from_addr,
                  [to_addr])
        return self.success(message=['sent'])
