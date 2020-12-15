from django.urls import path
from .views import Login, ConfirmCode, Verify, UpdateUserProfile, DeleteAccount, CreateSalesMan

urlpatterns = [
    path('login/', Login.as_view(), name='login'),
    path('confirm-code/', ConfirmCode.as_view(), name='confirm-code'),
    path('Verify/', Verify.as_view(), name='Verify'),
    path('update-profile/', UpdateUserProfile.as_view(), name='update-profile'),
    path('delete-account/', DeleteAccount.as_view(), name='delete-account'),
    path('salesman/', Verify.as_view(), name='salesman')

]
# path('product/', ProductManagement.as_view(), name='product'),
# path('category/', CategoryManagement.as_view(), name='category')
