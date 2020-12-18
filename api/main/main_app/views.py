from os import getenv
from .utils import MetaApiViewClass, ResponseUtils
from main_app.models import Product, Category
from .schema import JsonValidation


class Login(MetaApiViewClass):
    __login_attempt_limit_hour = getenv("LOGIN_ATTEMPT_LIMIT_HOUR")
    __confirm_code_expire_minutes = getenv("CONFIRM_CODE_EXPIRE_MINUTES")

    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def post(self, request):
        user = self.get_req("/find-user-by-mobile/", {
            'mobile': self.request.data['mobile'],
            'insert': True
        }, True)

        self.post_req("/create-otp/", {
            'user_id': user['id'],
            'login_attempt_limit_hour': self.__login_attempt_limit_hour,
            'confirm_code_expire_minutes': self.__confirm_code_expire_minutes
        })


class ConfirmCode(MetaApiViewClass):
    __confirm_code_try_count_limit = getenv("CONFIRM_CODE_TRY_COUNT_LIMIT")

    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def post(self, request):
        user = self.get_req("/find-user-by-mobile/", {
            'mobile': self.request.data['mobile'],
            'insert': False
        }, True)

        self.post_req('/confirm-code/', {
            'confirm_code': self.request.data['confirm_code'],
            'user_id': user['id'],
            'confirm_code_try_count_limit': self.__confirm_code_try_count_limit

        })


class Verify(MetaApiViewClass):
    @MetaApiViewClass.generic_decor(True)
    def get(self, request):
        return self.success(data={'user': self.user})


class DeleteAccount(MetaApiViewClass):
    @MetaApiViewClass.generic_decor(True)
    def delete(self, request):
        self.del_req('/delete-by-id/', self.user['id'])


class UpdateUserProfile(MetaApiViewClass):
    @MetaApiViewClass.generic_decor(True)
    @JsonValidation.validate
    def put(self, request):
        self.put_req('/update-profile/', dict(**self.request.data))


class CreateSalesMan(MetaApiViewClass):
    @MetaApiViewClass.generic_decor(True)
    @JsonValidation.validate
    def post(self, request):
        self.post_req('/create-salesman/', dict(**self.request.data))


class UpdateSalesManProfile(MetaApiViewClass):
    @MetaApiViewClass.generic_decor(True)
    @JsonValidation.validate
    def put(self, request):
        self.post_req('/create-salesman/', dict(**self.request.data))


class CategoryManagement(MetaApiViewClass):
    @MetaApiViewClass.generic_decor(True)
    def get(self, request):
        params_key = ['category_id']
        params = self.get_params(self.request.data, params_key)
        category = Category.objects.get(id=params['category_id']).values()
        if category.is_public == False:
            if self.user['uid'] != category.user_uid:
                return self.bad_request(message=['FORBIDDEN'])
            return self.success(data={'categories': category})
        return self.success(data={'categories': category})

    @MetaApiViewClass.generic_decor(True)
    def post(self, request):
        params_key = ['name']
        params = self.get_params(self.request.data, params_key)
        params['user_uid'] = self.user['uid']
        Category.objects.create(**params).save()
        return self.success(message=['CATEGORY_CREATED'])

    @MetaApiViewClass.generic_decor(True)
    def put(self):
        params_key = ['category_id', 'name', 'is_public']
        params = self.get_params(self.request.data, params_key)
        try:
            category = Category.objects.get(id=params['category_id'])
        except Category.DoesNotExist:
            return self.not_found()
        if self.user['uid'] != category.uid:
            return self.bad_request(message=['FORBIDDEN'])
        for param in params:
            setattr(category, params, params[param])
        return self.success(message=['CATEGORY_UPDATED'])

    @MetaApiViewClass.generic_decor(True)
    def delete(self, request):
        params_key = ['category_id']
        params = self.get_params(self.request.data, params_key)
        try:
            category = Category.objects.get(id=params['category_id'])
        except Category.DoesNotExist:
            return self.not_found()
        if self.user['uid'] != category.uid:
            return self.bad_request(message=['FORBIDDEN'])
        category.delete()
        return self.success()


class ProductManagement(MetaApiViewClass):
    @MetaApiViewClass.generic_decor()
    def get(self):
        params_key = ['product_id']
        params = self.get_params(self.request.data, params_key)
        try:
            product = Product.objects.get(id=params['product_id'])
        except Product.DoesNotExist:
            return self.not_found()
        return self.success(data={'product': ResponseUtils.serialize(product)})

    @MetaApiViewClass.generic_decor(True)
    def post(self, request):
        params_key = ['name', 'count', 'description', 'price', 'category_id']
        params = self.get_params(self.request.data, params_key)
        category = Category.objects.get(id=params['category_id'])
        params.pop('category_id')
        params['category'] = category
        params['uid'] = f"{self.user['uid'] - {category.uid} - ResponseUtils.rand_digit(6)}"
        Product.objects.create(**params).save()
        return self.success(message=['PRODUCT_CREATED'])

    @MetaApiViewClass.generic_decor(True)
    def put(self, request):
        params_key = ['product_id']
        params = self.get_params(self.request.data, params_key)
        try:
            product = Product.objects.get(id=params['product_id'])
        except Product.DoesNotExist:
            return self.not_found()
        if self.user['uid'] != product.uid.split('-')[0]:
            return self.bad_request(message=['FORBIDDEN'])
        for p in params:
            setattr(product, p, params[p])

        product.save()

    @MetaApiViewClass.generic_decor(True)
    def delete(self, request):
        params_key = ['product_id']
        params = self.get_params(self.request.data, params_key)
        product = Product.objects.get(id=params['product_id'])
        if self.user['uid'] != product.uid.split('-')[0]:
            return self.bad_request(message=['FORBIDDEN'])
        product.delete()
        return self.success(message=['PRODUCT_DELETED'])
