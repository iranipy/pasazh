from main.utils import MetaApiViewClass, JsonValidation
from .models import Product, Category


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


#  ToDO
class ProductAttachmentManagement(MetaApiViewClass):
    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def get(self, request):
        pass

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def post(self, request):
        pass

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def put(self, request):
        pass

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def delete(self, request):
        pass


class OptionManagement(MetaApiViewClass):
    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def get(self, request):
        pass

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def post(self, request):
        pass

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def put(self, request):
        pass

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def delete(self, request):
        pass


class OptionValueManagement(MetaApiViewClass):
    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def get(self, request):
        pass

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def post(self, request):
        pass

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def put(self, request):
        pass

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def delete(self, request):
        pass
