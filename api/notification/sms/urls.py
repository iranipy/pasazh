from notification.utils import Helpers
from .views import SendSMS


gen_url = Helpers.generate_url_item


urlpatterns = [
    gen_url('send-sms', SendSMS),
]
