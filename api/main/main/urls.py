from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('/auth', include('authentication.urls')),
    path('/user', include('user.urls')),
    path('/salesman', include('salesman.urls')),
    path('/business', include('business.urls')),
    # path('', include('root.urls')),
]
