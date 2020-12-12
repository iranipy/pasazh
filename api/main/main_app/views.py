from os import getenv
from .utils import MetaApiViewClass, ResponseUtils
from main_app.models import Product, Category


class Login(MetaApiViewClass):
    __login_attempt_limit_hour = getenv("LOGIN_ATTEMPT_LIMIT_HOUR")
    __confirm_code_expire_minutes = getenv("CONFIRM_CODE_EXPIRE_MINUTES")

    @MetaApiViewClass.generic_decor()
    def post(self, request):
        params_key = ['mobile']
        params = self.get_params(self.request.data, params_key)

        user = self.get_req("/find-user-by-mobile/", {
            'mobile': params['mobile'],
            'insert': True
        }, True)

        self.post_req("/create-otp/", {
            'user_id': user['id'],
            'login_attempt_limit_hour': self.__login_attempt_limit_hour,
            'confirm_code_expire_minutes': self.__confirm_code_expire_minutes
        })


class CategoryManagement(MetaApiViewClass):
    @MetaApiViewClass.generic_decor(True)
    def get(self, request):
        categories = Category.objects.filter(user_uid=self.user['uid']).values()

        return self.success(data={'categories': categories})

    @MetaApiViewClass.generic_decor(True)
    def post(self, request):
        params_key = ['name', 'user_uid']
        params = self.get_params(self.request.data, params_key)
        Category.objects.create(**params).save()
        return self.success(message=['CATEGORY_CREATED'])

    def delete(self, request):
        params_key = ['category_id']
        params = self.get_params(self.request.data, params_key)
        try:
            Category.objects.get(id=params['category_id']).delete()
        except Category.DoesNotExist:
            return self.not_found()
        return self.success()


class ProductManagement(MetaApiViewClass):
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
        # chek if product is belong to this id(based  on uid)
        for p in params:
            setattr(product, p, params[p])

        product.save()

    @MetaApiViewClass.generic_decor(True)
    def delete(self, request):
        params_key = ['product_id']
        params = self.get_params(self.request.data, params_key)
        # chek if product is belong to this id(based  on uid)
        Product.objects.get(id=params['product_id']).delete()
        return self.success(message=['PRODUCT_DELETED'])
