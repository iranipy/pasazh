from django.urls import re_path
from .views import (FindUserByMobile, CreateOtp, ConfirmCode, FindUserByToken,
                    DeleteAccountById, UserProfileUpdate, SalesManView, Block)

urlpatterns = [
    re_path(r'^find-user-by-mobile/?$', FindUserByMobile.as_view(), name='find-user-by-mobile'),
    re_path(r'^create-otp/?$', CreateOtp.as_view(), name='create-otp'),
    re_path(r'^confirm-code/?$', ConfirmCode.as_view(), name='confirm-code'),
    re_path(r'^find-user-by-token/?$', FindUserByToken.as_view(), name='find-user-by-token'),
    re_path(r'^update-profile/?$', UserProfileUpdate.as_view(), name='update-profile'),
    re_path(r'^delete-account-by-id/?$', DeleteAccountById.as_view(), name='delete-by-id'),
    re_path(r'^salesman-profile/?$', SalesManView.as_view(), name='salesman-profile'),
    re_path(r'^block-user/?$', Block.as_view(), name='block-user')
]

