from django.urls import re_path
from .views import SendSMS

urlpatterns = [
    re_path(r'^send-sms/$', SendSMS.as_view(), name='send-sms')
]
