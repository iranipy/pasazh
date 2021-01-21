from main.utils import Helpers
from .views import Login, ConfirmCode, Verify


gen_url = Helpers.generate_url_item


urlpatterns = [
    gen_url('login', Login),
    gen_url('confirm-code', ConfirmCode),
    gen_url('verify', Verify),
]
