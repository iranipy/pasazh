from django.urls import re_path

from .views import FindUserByMobile, FindUserByToken, CreateOtp, ConfirmCode, \
    UserProfile, SalesManView, Block, Follow


def generate_url_item(url, view):
    url = f'^{url}/?$'
    return re_path(url, view.as_view(), name=url)


urlpatterns = [
    generate_url_item('find-user-by-mobile', FindUserByMobile),
    generate_url_item('find-user-by-token', FindUserByToken),
    generate_url_item('create-otp', CreateOtp),
    generate_url_item('confirm-code', ConfirmCode),
    generate_url_item('user-profile', UserProfile),
    generate_url_item('salesman-profile', SalesManView),
    generate_url_item('block-user', Block),
    generate_url_item('follow-user', Follow),
]
