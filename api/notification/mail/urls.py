from notification.utils import Helpers
from .views import SendMail, SendMassMail


gen_url = Helpers.generate_url_item


urlpatterns = [
    gen_url('send-mail', SendMail),
    gen_url('send-mass-mail', SendMassMail)
]
