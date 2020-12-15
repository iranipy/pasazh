from django.urls import path
from .views import Login, ConfirmCode, Verify

urlpatterns = [
    path('login/', Login.as_view(), name='login'),
    path('confirm-code/', ConfirmCode.as_view(), name='confirm-code'),
    path('Verify/', Verify.as_view(), name='Verify')

]
# path('product/', ProductManagement.as_view(), name='product'),
# path('category/', CategoryManagement.as_view(), name='category')
