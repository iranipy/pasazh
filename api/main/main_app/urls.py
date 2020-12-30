from django.urls import re_path
from .views import (Login, ConfirmCode, Verify, UpdateUserProfile, DeleteAccount,
                    SalesManView, ProductManagement, CategoryManagement, Follow)

urlpatterns = [
    re_path(r'^login/?$', Login.as_view(), name='login'),
    re_path(r'^confirm-code/?$', ConfirmCode.as_view(), name='confirm-code'),
    re_path(r'^verify/?$', Verify.as_view(), name='Verify'),
    re_path(r'^update-profile/?$', UpdateUserProfile.as_view(), name='update-profile'),
    re_path(r'^delete-account/?$', DeleteAccount.as_view(), name='delete-account'),
    re_path(r'^salesman-profile/?$', SalesManView.as_view(), name='salesman'),
    re_path(r'^product/?$', ProductManagement.as_view(), name='product'),
    re_path(r'^category/?$', CategoryManagement.as_view(), name='category'),
    re_path(r'^follow-user/?$', Follow.as_view(), name='follow-user')
]

