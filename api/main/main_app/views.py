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
        self.request.data['insert'] = str(self.request.data["insert"]).lower()
        user = self.get_req("/find-user-by-mobile/", params=self.request.data, return_data=True)
        self.post_req("/create-otp/", json={
            'user_id': int(user['id']),
            'login_attempt_limit_hour': int(self.__login_attempt_limit_hour),
            'confirm_code_expire_minutes': int(self.__confirm_code_expire_minutes)
        })
        return self.success()


class ConfirmCode(MetaApiViewClass):
    __confirm_code_try_count_limit = getenv("CONFIRM_CODE_TRY_COUNT_LIMIT")

    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def post(self, request):
        user = self.get_req("/find-user-by-mobile/", params={
            'mobile': self.request.data['mobile'], 'insert': 'true'
        }, return_data=True)

        self.post_req('/confirm-code/', json={
            'confirm_code': self.request.data['confirm_code'],
            'user_id': int(user['id']),
            'confirm_code_try_count_limit': int(self.__confirm_code_try_count_limit)

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
        self.put_req('/update-profile/', json=dict(**self.request.data))


class SalesManView(MetaApiViewClass):
    @MetaApiViewClass.generic_decor(True)
    @JsonValidation.validate
    def post(self, request):
        self.request.data['user_id'] = self.user['id']
        self.post_req('/salesman-profile/', json=dict(**self.request.data))

    @MetaApiViewClass.generic_decor(True)
    @JsonValidation.validate
    def put(self, request):
        self.request.data['user_id'] = self.user['id']
        self.put_req('/salesman-profile/', json=dict(**self.request.data))


class CategoryManagement(MetaApiViewClass):
    @MetaApiViewClass.generic_decor(True)
    def get(self, request):

        category = Category.objects.get(id=self.request.query_params['category_id'])
        dict_category = ResponseUtils.serialize(category)
        if category.is_public is False:
            if self.user['uid'] != category.user_uid:
                return self.bad_request(message=['FORBIDDEN'])
            return self.success(data={'category': dict_category})
        return self.success(data={'category': dict_category})

    @MetaApiViewClass.generic_decor(True)
    def post(self, request):
        data = self.request.data
        data['user_uid'] = self.user['uid']
        try:
            _ = Category.objects.filter(name=self.request.data['name'])[0]
            return self.bad_request(message=['CATEGORY_ALREADY_EXIST'])
        except IndexError:
            Category.objects.create(**data).save()
            return self.success(message=['CATEGORY_CREATED'])

    @MetaApiViewClass.generic_decor(True)
    def put(self, request):
        data = self.request.data
        try:
            category = Category.objects.get(id=data['category_id'])
        except Category.DoesNotExist:
            return self.not_found(message=['CATEGORY_NOT_FOUND'])
        if self.user['uid'] != category.user_uid:
            return self.bad_request(message=['FORBIDDEN'])
        print(data)
        for item in data:
            if item == 'category_id':
                continue
            setattr(category, item, data[item])
        category.save()
        return self.success(message=['CATEGORY_UPDATED'])

    @MetaApiViewClass.generic_decor(True)
    def delete(self, request):
        data = self.request.query_params
        try:
            category = Category.objects.get(id=data['category_id'])
        except Category.DoesNotExist:
            return self.not_found(message=['CATEGORY_NOT_FOUND'])
        if self.user['uid'] != category.user_uid:
            return self.bad_request(message=['FORBIDDEN'])
        category.delete()
        return self.success(message=['CATEGORY_DELETED'])


class ProductManagement(MetaApiViewClass):
    @MetaApiViewClass.generic_decor()
    def get(self, request):
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
            return self.not_found(message=['PRODUCT_NOT_FOUND'])
        if self.user['uid'] != product.uid.split('-')[0]:
            return self.bad_request(message=['FORBIDDEN'])
        try:
            category = Category.objects.get(id=data['category_id'])
        except Category.DoesNotExist:
            return self.bad_request(meeage=['INVALID_CATEGORY'])
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
