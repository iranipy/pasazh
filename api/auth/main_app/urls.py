from django.urls import path
from .views import (FindUserByMobile, CreateOtp, ConfirmCode, FindUserByToken,
                    DeleteById, UserProfileUpdate, SalesManView)

urlpatterns = [
    path('find-user-by-mobile/', FindUserByMobile.as_view(), name='find-user-by-mobile'),
    path('create-otp/', CreateOtp.as_view(), name='create-otp'),
    path('confirm-code/', ConfirmCode.as_view(), name='confirm-code'),
    path('find-user-by-token/', FindUserByToken.as_view(), name='find-user-by-token'),
    path('delete-by-id/<int:user_id>/', DeleteById.as_view(), name='delete-by-id'),
    path('update-profile/', UserProfileUpdate.as_view(), name='update-profile'),
    path('create-salesman/', SalesManView.as_view(), name='create-salesman')
]
