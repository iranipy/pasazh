from django.urls import path
from .views import Login, Verify, DeleteAccount

urlpatterns = [
    path('login/', Login.as_view(), name='login'),
    path('verify/<int:pk>', Verify.as_view(), name='verify'),
    path('delete-account/', DeleteAccount.as_view(), name='delete-account')
]
