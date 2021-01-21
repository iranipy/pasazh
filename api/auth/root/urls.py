from auth.utils import Helpers
from .views import FindUserByMobile, FindUserByToken, CreateOtp, ConfirmCode, \
UserProfile, SalesManView, Block, Follow


gen_url = Helpers.generate_url_item


urlpatterns = [
    gen_url('find-user-by-mobile', FindUserByMobile),
    gen_url('find-user-by-token', FindUserByToken),
    gen_url('create-otp', CreateOtp),
    gen_url('confirm-code', ConfirmCode),
    gen_url('user-profile', UserProfile),
    gen_url('salesman-profile', SalesManView),
    gen_url('block-user', Block),
    gen_url('follow-user', Follow),
]
