from django.urls import path, re_path
from .views import (FindUserByMobile, CreateOtp, ConfirmCode, FindUserByToken,
                    DeleteAccountById, UserProfileUpdate, SalesManView)  # , UpdateSalesMan

urlpatterns = [
    re_path(r'^find-user-by-mobile/?$', FindUserByMobile.as_view(), name='find-user-by-mobile'),
    re_path(r'^create-otp/?$', CreateOtp.as_view(), name='create-otp'),
    re_path(r'^confirm-code/?$', ConfirmCode.as_view(), name='confirm-code'),
    re_path(r'^find-user-by-token/?$', FindUserByToken.as_view(), name='find-user-by-token'),
    re_path(r'^delete-by-id/<int:user_id>/?$', DeleteAccountById.as_view(), name='delete-by-id'),
    re_path(r'^update-profile/?$', UserProfileUpdate.as_view(), name='update-profile'),
    re_path(r'^create-salesman/?$', SalesManView.as_view(), name='create-salesman'),

]

# urlpatterns += [re_path(r'^update-salesman/?$', UpdateSalesMan.as_view(), name='update-salesman')]
