from django.contrib import admin
from django.urls import path, include
from main_app.views import APIRoot


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main_app.urls')),
    path('', APIRoot.as_view()),
    path('auth/', include('rest_framework.urls'))
]
