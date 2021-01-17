from django.urls import re_path
from .views import SendEmail
urlpatterns = [
    re_path(r'^send-email/?$', SendEmail.as_view(), name='send-email')
]