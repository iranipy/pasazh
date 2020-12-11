from django.urls import path
from .views import FindUserByMobile, CreateOtp

urlpatterns = [
    path('find-user-by-mobile/', FindUserByMobile.as_view(), name='find-user-by-mobile'),
    path('create-otp/', CreateOtp.as_view(), name='create-otp')
]
