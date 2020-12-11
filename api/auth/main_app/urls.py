from django.urls import path
from .views import Login, Verify, ConfirmCode, DeleteAccount, UserProfileUpdate

urlpatterns = [
    path('login/', Login.as_view(), name='login'),
    path('verify/', Verify.as_view(), name='verify'),
    path('confirm-code/', ConfirmCode.as_view(), name='confirm'),
    path('delete-account/', DeleteAccount.as_view(), name='delete-account'),
    path('update-profile/', UserProfileUpdate.as_view(), name='update-profile')
]
