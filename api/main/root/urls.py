from django.urls import re_path

from .views import Login, ConfirmCode, Verify, UpdateUserProfile, \
    SalesManView, ProductManagement, CategoryManagement, Follow


def generate_url_item(url, view):
    url = f'^{url}/?$'
    return re_path(url, view.as_view(), name=url)


urlpatterns = [
    generate_url_item('login', Login),
    generate_url_item('confirm-code', ConfirmCode),
    generate_url_item('verify', Verify),
    generate_url_item('update-profile', UpdateUserProfile),
    generate_url_item('salesman-profile', SalesManView),
    generate_url_item('product', ProductManagement),
    generate_url_item('category', CategoryManagement),
    generate_url_item('follow-user', Follow),
]
