from django.db.models import Q

from main.utils import MetaApiViewClass, JsonValidation
from .models import Product, Category, ProductAttachment, Option, OptionValue


class CategoryManagement(MetaApiViewClass):

    @MetaApiViewClass.verify_token(check_user=True)
    @JsonValidation.validate
    def get(self, request):
        categories = Category.objects.filter(Q(is_public=True) | Q(created_by=self.user['id']))

        if not categories:
            return self.not_found(message=[13])

        return self.success(data={'categories': self.serialize_list(categories)})

    @MetaApiViewClass.verify_token(check_user=True)
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data

        try:
            Category.objects.get(name=data['name'], parent_id=data['parent_id'], created_by=self.user['id'])
            return self.bad_request(message=[7])
        except Category.DoesNotExist:
            Category.objects.create(created_by=self.user['id'], **data).save()
            return self.success(message=[8])

    @MetaApiViewClass.verify_token(check_user=True)
    @JsonValidation.validate
    def put(self, request):
        data = self.request.data

        try:
            category = Category.objects.get(id=data.pop('category_id'), created_by=self.user['id'])
        except Category.DoesNotExist:
            return self.not_found(message=[9])

        for item in data:
            setattr(category, item, data[item])

        category.modified_by = self.user['id']
        category.save()

        return self.success(message=[10])

    @MetaApiViewClass.verify_token(check_user=True)
    @JsonValidation.validate
    def delete(self, request):
        data = self.request.query_params

        try:
            category = Category.objects.get(id=data['category_id'], created_by=self.user['id'])
        except Category.DoesNotExist:
            return self.not_found(message=[9])

        category.delete()

        return self.success(message=[11])


class ProductManagement(MetaApiViewClass):

    @classmethod
    def get_category(cls, category_id: int, user_id: int):
        try:
            return Category.objects.get(
                Q(id=category_id),
                Q(is_public=True) | Q(created_by=user_id)
            )
        except Category.DoesNotExist:
            cls.bad_request(message=[9])

    @MetaApiViewClass.verify_token(check_user=True)
    @JsonValidation.validate
    def get(self, request):
        data = self.request.query_params

        products = Product.objects.filter(category_id=data['category_id'])

        if not products:
            return self.not_found(message=[16])

        return self.success(data={'products': self.serialize_list(products)})

    @MetaApiViewClass.verify_token(check_user=True)
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data

        data['category'] = category = self.get_category(data.pop('category_id'), self.user['id'])

        try:
            Product.objects.get(name=data['name'], category_id=data['category_id'])
            return self.bad_request(message=[6])
        except Product.DoesNotExist:
            data['uid'] = f'{self.user["uid"]}-{category.uid}-{self.generate_rand_decimal(6)}'
            Product.objects.create(created_by=self.user['id'], **data).save()
            return self.success(message=[28])

    @MetaApiViewClass.verify_token(check_user=True)
    @JsonValidation.validate
    def put(self, request):
        data = self.request.data

        try:
            product = Product.objects.get(id=data.pop('product_id'), created_by=self.user['id'])
        except Product.DoesNotExist:
            return self.not_found(message=[5])

        data['category'] = product.category
        if data['category_id']:
            data['category'] = self.get_category(data.pop('category_id'), self.user['id'])

        for item in data:
            setattr(product, item, data[item])

        product.modified_by = self.user['id']
        product.save()

        return self.success(message=[14])

    @MetaApiViewClass.verify_token(check_user=True)
    @JsonValidation.validate
    def delete(self, request):
        data = self.request.query_params

        try:
            Product.objects.get(id=data['product_id'], created_by=self.user['id']).delete()
        except Product.DoesNotExist:
            return self.not_found(message=[5])

        return self.success(message=[15])


class ProductAttachmentManagement(MetaApiViewClass):

    @MetaApiViewClass.verify_token(check_user=True)
    @JsonValidation.validate
    def get(self, request):
        data = self.request.query_params

        product_attachments = ProductAttachment.objects.filter(product_id=data['product_id'])

        if not product_attachments:
            return self.not_found(message=[31])

        return self.success(data={'product_attachments': self.serialize_list(product_attachments)})

    @MetaApiViewClass.verify_token(check_user=True)
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data

        try:
            product = Product.objects.get(id=data.pop('product_id'), created_by=self.user['id'])
        except Product.DoesNotExist:
            return self.not_found(message=[5])

        ProductAttachment.objects.create(product=product, created_by=self.user['id'], **data).save()

        return self.success(message=[17])

    @MetaApiViewClass.verify_token(check_user=True)
    @JsonValidation.validate
    def delete(self, request):
        data = self.request.query_params

        try:
            ProductAttachment.objects.get(
                id=data['product_attachment_id'], created_by=self.user['id']
            ).delete()
        except ProductAttachment.DoesNotExist:
            return self.not_found(message=[24])

        return self.success(message=[25])


class OptionManagement(MetaApiViewClass):

    @MetaApiViewClass.verify_token(check_user=True)
    @JsonValidation.validate
    def get(self, request):
        data = self.request.query_params

        options = Option.objects.filter(product_id=data['product_id'])

        if not options:
            return self.not_found(message=[30])

        return self.success(data={'options': self.serialize_list(options)})

    @MetaApiViewClass.verify_token(check_user=True)
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data

        try:
            product = Product.objects.get(id=data['product_id'], created_by=self.user['id'])
        except Product.DoesNotExist:
            return self.not_found(message=[5])

        try:
            Option.objects.get(product=product, name=data['name'], created_by=self.user['id'])
            return self.bad_request(message=[29])
        except Product.DoesNotExist:
            Option.objects.create(
                product=product, name=data['name'],
                created_by=self.user['id']
            ).save()
            return self.success(message=[20])

    @MetaApiViewClass.verify_token(check_user=True)
    @JsonValidation.validate
    def delete(self, request):
        data = self.request.query_params

        try:
            Option.objects.get(id=data['option_id'], created_by=self.user['id']).delete()
        except Option.DoesNotExist:
            return self.not_found(message=[21])

        return self.success(message=[26])


class OptionValueManagement(MetaApiViewClass):

    @MetaApiViewClass.verify_token(check_user=True)
    @JsonValidation.validate
    def get(self, request):
        data = self.request.query_params

        option_values = OptionValue.objects.filter(option_id=data['option_id'])

        if not option_values:
            return self.not_found(message=[22])

        return self.success(data={'option_values': self.serialize_list(option_values)})

    @MetaApiViewClass.verify_token(check_user=True)
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data

        try:
            option = Option.objects.get(id=data['option_id'], created_by=self.user['id'])
        except Product.DoesNotExist:
            return self.not_found(message=[21])

        OptionValue.objects.create(option=option, value=data['value'], created_by=self.user['id'])

        return self.success(message=[23])

    @MetaApiViewClass.verify_token(check_user=True)
    @JsonValidation.validate
    def delete(self, request):
        data = self.request.query_params

        try:
            OptionValue.objects.get(id=data['option_value_id'], created_by=self.user['id']).delete()
        except OptionValue.DoesNotExist:
            return self.not_found()

        return self.success(message=[27])
