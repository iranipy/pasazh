from django.urls import path
from .views import Login, CategoryManagement, ProductManagement

urlpatterns = [
    path('login/', Login.as_view(), name='login'),
    path('product/', ProductManagement.as_view(), name='product'),
    path('category/', CategoryManagement.as_view(), name='category')

]
