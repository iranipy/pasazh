from os import getenv

from main.utils import MetaApiViewClass, JsonValidation
from root.models import Product, Category


class Login(MetaApiViewClass):

    __login_attempt_limit_hour = getenv('LOGIN_ATTEMPT_LIMIT_HOUR')
    __confirm_code_expire_minutes = getenv('CONFIRM_CODE_EXPIRE_MINUTES')
    __otp_code_length = getenv('OTP_CODE_LENGTH')
    __deleted_account_limit_hours = getenv('DELETED_ACCOUNT_LIMIT_HOURS')

    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data

        user = self.get_req('/find-user-by-mobile/', params={
            'mobile': data['mobile'], 'insert': 'true',
            'deleted_account_limit_hours': self.__deleted_account_limit_hours
        }, return_data=True)

        self.post_req('/create-otp/', json={
            'user_id': int(user['id']),
            'login_attempt_limit_hour': int(self.__login_attempt_limit_hour),
            'confirm_code_expire_minutes': int(self.__confirm_code_expire_minutes),
            'otp_code_length': int(self.__otp_code_length)
        })

        return self.success()


class ConfirmCode(MetaApiViewClass):

    __confirm_code_try_count_limit = getenv('CONFIRM_CODE_TRY_COUNT_LIMIT')
    __deleted_account_limit_hours = getenv('DELETED_ACCOUNT_LIMIT_HOURS')

    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data

        user = self.get_req('/find-user-by-mobile/', params={
            'mobile': data['mobile'], 'insert': 'true',
            'deleted_account_limit_hours': self.__deleted_account_limit_hours
        }, return_data=True)

        self.post_req('/confirm-code/', json={
            'confirm_code': data['confirm_code'],
            'user_id': int(user['id']),
            'confirm_code_try_count_limit': int(self.__confirm_code_try_count_limit)
        })


class Verify(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(protected=True)
    def get(self, request):
        return self.success(data={'user': self.user})


class UpdateUserProfile(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def put(self, request):
        self.request.data['user_id'] = self.user['id']
        self.put_req('/user-profile/', json=dict(**self.request.data))

    @MetaApiViewClass.generic_decor(protected=True)
    def delete(self, request):
        self.del_req('/user-profile/', params={'user_id': self.user['id']})


class SalesManView(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def post(self, request):
        self.request.data['user_id'] = self.user['id']
        self.post_req('/salesman-profile/', json=dict(**self.request.data))

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def put(self, request):
        self.request.data['user_id'] = self.user['id']
        self.put_req('/salesman-profile/', json=dict(**self.request.data))


class Follow(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def get(self, request):
        self.get_req('/follow-user/', params={'user_id': self.user['id']})

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def post(self, request):
        self.request.data['user_id'] = self.user['id']
        self.post_req('/follow-user/', json=dict(**self.request.data))

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def delete(self, request):
        data = self.request.query_params
        params = {'user_id': self.user['id'], 'followed_user_id': data['followed_user_id']}
        self.del_req('/follow-user/', params=params)


class CategoryManagement(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def get(self, request):
        categories = Category.objects.filter(is_public=True) | Category.objects.filter(user_uid=self.user['uid'])

        if len(categories) == 0:
            return self.not_found(message=[13])

        return self.success(data={'categories': self.serialize(categories)})

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data
        data['user_uid'] = self.user['uid']

        try:
            _ = Category.objects.filter(name=data['name'], parent_id=data['parent_id'])[0]
            return self.bad_request(message=[7])
        except IndexError:
            Category.objects.create(**data).save()
            return self.success(message=[8])

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def put(self, request):
        data = self.request.data

        try:
            category = Category.objects.get(id=data['category_id'], user_uid=self.user['uid'])
        except Category.DoesNotExist:
            return self.not_found(message=[9])

        data.pop('category_id')
        for item in data:
            setattr(category, item, data[item])

        category.save()

        return self.success(message=[10])

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def delete(self, request):
        data = self.request.query_params

        try:
            category = Category.objects.get(id=data['category_id'], user_uid=self.user['uid'])
        except Category.DoesNotExist:
            return self.not_found(message=[9])

        category.delete()

        return self.success(message=[11])


class ProductManagement(MetaApiViewClass):

    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def get(self, request):
        data = self.request.query_params

        products = Product.objects.filter(category_id=data['category_id'])

        if len(products) == 0:
            return self.not_found(message=[16])

        return self.success(data={'products': self.serialize(products)})

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data

        try:
            category = Category.objects.get(id=data['category_id'])
            data.pop('category_id')
            data['category'] = category
        except Category.DoesNotExist:
            return self.bad_request(message=[9])

        try:
            _ = Product.objects.filter(name=data['name'], category_id=data['category_id'])[0]
            return self.bad_request(message=[6])
        except IndexError:
            data['uid'] = f'{self.user["uid"]}-{category.uid}-{self.generate_rand_decimal(6)}'

            Product.objects.create(**data).save()

            return self.success(message=['PRODUCT_CREATED'])

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def put(self, request):
        data = self.request.data

        try:
            product = Product.objects.get(id=data['product_id'])
        except Product.DoesNotExist:
            return self.not_found(message=[5])

        if self.user['uid'] != product.uid.split('-')[0]:
            return self.bad_request(message=[12])

        try:
            category = Category.objects.get(id=data['category_id'])
        except Category.DoesNotExist:
            return self.bad_request(meeage=[9])

        data.pop('category_id')
        data['category'] = category

        for item in data:
            setattr(product, item, data[item])

        product.save()

        return self.success(message=[14])

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def delete(self, request):
        data = self.request.query_params

        try:
            product = Product.objects.get(id=data['product_id'])
        except Product.DoesNotExist:
            return self.not_found(message=[5])

        if self.user['uid'] != product.uid.split('-')[0]:
            return self.bad_request(message=[12])

        product.delete()

        return self.success(message=[15])
