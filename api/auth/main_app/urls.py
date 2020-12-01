from django.urls import path, include
from .views import Login, UserViewSet
from rest_framework.routers import DefaultRouter
# test
router = DefaultRouter()
router.register(r'users', UserViewSet)
urlpatterns = [
    path('login/', Login.as_view(), name='login'),
    path('fancy/', include(router.urls)),
]
