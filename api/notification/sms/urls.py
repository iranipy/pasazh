from notification.utils import Helpers
from .views import SendSMS, SendMassSMS, SMSStatus, SelectSMS, CancelSms, \
SelectOutBoxSMS, CountOutBoxSMS, CountInBoxSMS, ReadInbox


gen_url = Helpers.generate_url_item


urlpatterns = [
    gen_url('send-sms', SendSMS),
    gen_url('send-mass-sms', SendMassSMS),
    gen_url('sms-status', SMSStatus),
    gen_url('select-sms', SelectSMS),
    gen_url('cancel-sms', CancelSms),
    gen_url('select-outbox', SelectOutBoxSMS),
    gen_url('count-outbox', CountOutBoxSMS),
    gen_url('count-inbox', CountInBoxSMS),
    gen_url('read-inbox', ReadInbox),
]
