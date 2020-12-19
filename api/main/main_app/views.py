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
        params = {"user_id": self.user['id']}
        self.del_req('/delete-account-by-id/', params=params)


class UpdateUserProfile(MetaApiViewClass):
    @MetaApiViewClass.generic_decor(True)
    @JsonValidation.validate
    def put(self, request):
        self.request.data['user_id'] = self.user['id']
        self.put_req('/update-profile/', dict(**self.request.data))


class SalesManView(MetaApiViewClass):
    @MetaApiViewClass.generic_decor(True)
    @JsonValidation.validate
    def post(self, request):
        self.request.data['user_id'] = self.user['id']
        self.post_req('/salesman-profile/', dict(**self.request.data))

    @MetaApiViewClass.generic_decor(True)
    @JsonValidation.validate
    def put(self, request):
        self.request.data['user_id'] = self.user['id']
        self.put_req('/salesman-profile/', dict(**self.request.data))


class CategoryManagement(MetaApiViewClass):
    @MetaApiViewClass.generic_decor(True)
    def get(self, request):

        category = Category.objects.get(id=self.request.query_params['category_id']).values()
        if category.is_public:
            return self.success(data={'category': category})
        if self.user['uid'] != category.user_uid:
            return self.bad_request(message=['FORBIDDEN'])

    @MetaApiViewClass.generic_decor(True)
    def post(self, request):
        data = self.request.data
        data['user_uid'] = self.user['uid']
        Category.objects.create(**data).save()
        return self.success(message=['CATEGORY_CREATED'])

    @MetaApiViewClass.generic_decor(True)
    def put(self):
        data = self.request.data
        try:
            category = Category.objects.get(id=data['category_id'])
        except Category.DoesNotExist:
            return self.not_found()
        if self.user['uid'] != category.user_uid:
            return self.bad_request(message=['FORBIDDEN'])
        for item in data:
            if item == 'category_id':
                continue
            setattr(category, data, data[item])
        return self.success(message=['CATEGORY_UPDATED'])

    @MetaApiViewClass.generic_decor(True)
    def delete(self, request):
        data = self.request.query_params
        try:
            category = Category.objects.get(id=data['category_id'])
        except Category.DoesNotExist:
            return self.not_found()
        if self.user['uid'] != category.user_uid:
            return self.bad_request(message=['FORBIDDEN'])
        category.delete()
        return self.success(message=['CATEGORY_DELETED'])


class ProductManagement(MetaApiViewClass):
    @MetaApiViewClass.generic_decor()
    def get(self):
        data = self.request.query_params
        try:
            product = Product.objects.get(id=data['product_id'])
        except Product.DoesNotExist:
            return self.not_found()
        return self.success(data={'product': ResponseUtils.serialize(product)})

    @MetaApiViewClass.generic_decor(True)
    def post(self, request):
        data = self.request.data
        try:
            category = Category.objects.get(id=data['category_id'])
        except Category.DoesNotExist:
            return self.bad_request(message=["INVALID_CATEGORY"])
        data.pop('category_id')
        data['category'] = category
        data['uid'] = f"{self.user['uid']}-{category.uid}-{ResponseUtils.rand_digit(6)}"
        Product.objects.create(**data).save()
        return self.success(message=['PRODUCT_CREATED'])

    @MetaApiViewClass.generic_decor(True)
    def put(self, request):
        data = self.request.data
        try:
            product = Product.objects.get(id=data['product_id'])
        except Product.DoesNotExist:
            return self.not_found()
        if self.user['uid'] != product.uid.split('-')[0]:
            return self.bad_request(message=['FORBIDDEN'])
        category = Category.objects.get(id=data['category_id'])
        data.pop('category_id')
        data['category'] = category
        for item in data:
            setattr(product, item, data[item])

        product.save()
        return self.success(message=['PRODUCT_UPDATED'])

    @MetaApiViewClass.generic_decor(True)
    def delete(self, request):
        data = self.request.query_params
        try:
            product = Product.objects.get(id=data['product_id'])
        except Product.DoesNotExist:
            return self.not_found(message=['PRODUCT_NOT_FOUND'])
        if self.user['uid'] != product.uid.split('-')[0]:
            return self.bad_request(message=['FORBIDDEN'])
        product.delete()
        return self.success(message=['PRODUCT_DELETED'])
