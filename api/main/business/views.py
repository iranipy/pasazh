from main.utils import MetaApiViewClass, JsonValidation
from .models import Product, Category, ProductAttachment, Option, OptionValue


class CategoryManagement(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(protected=True, check_user=True)
    @JsonValidation.validate
    def get(self, request):
        categories = Category.objects.filter(is_public=True) | Category.objects.filter(user_uid=self.user['uid'])

        if len(categories) == 0:
            return self.not_found(message=[13])

        return self.success(data={'categories': list(map(self.serialize, categories))})

    @MetaApiViewClass.generic_decor(protected=True, check_user=True)
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

    @MetaApiViewClass.generic_decor(protected=True, check_user=True)
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

    @MetaApiViewClass.generic_decor(protected=True, check_user=True)
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

    @MetaApiViewClass.generic_decor(protected=True, check_user=True)
    @JsonValidation.validate
    def get(self, request):
        data = self.request.query_params

        products = Product.objects.filter(category_id=data['category_id'])

        if len(products) == 0:
            return self.not_found(message=[16])

        return self.success(data={'products': list(map(self.serialize, products))})

    @MetaApiViewClass.generic_decor(protected=True, check_user=True)
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

    @MetaApiViewClass.generic_decor(protected=True, check_user=True)
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

    @MetaApiViewClass.generic_decor(protected=True, check_user=True)
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


class ProductAttachmentManagement(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(protected=True, check_user=True)
    @JsonValidation.validate
    def get(self, request):
        data = self.request.query_params

        try:
            product = Product.objects.get(data['product_uid'])
        except Product.DoesNotExist:
            return self.not_found(message=[5])

        product_attachments = ProductAttachment.objects.filter(product)

        return self.success(data={'product_attachment': list(map(self.serialize, product_attachments))})

    @MetaApiViewClass.generic_decor(protected=True, check_user=True)
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data

        try:
            product = Product.objects.get(uid=data['product_uid'])
        except Product.DoesNotExist:
            return self.not_found(message=[5])
        if self.user.uid != product.uid.split('-')[0]:
            return self.bad_request(message=[18])
        new_attachment = ProductAttachment.objects.create(
            product=product, type=data['type'], content=data['content'],
            size=data['size'], description=data['description']
        )
        new_attachment.save()

        return self.success(message=[17])

    @MetaApiViewClass.generic_decor(protected=True, check_user=True)
    @JsonValidation.validate
    def delete(self, request):
        data = self.request.query_params

        try:
            Product.objects.get(data['product_uid'])
        except Product.DoesNotExist:
            return self.not_found(message=[5])
        if self.user.uid != data['product_uid'].split('-')[0]:
            return self.bad_request(message=[18])
        try:
            ProductAttachment.objects.get(id=data['product_att_id']).delete()
        except ProductAttachment.DoesNotExist:
            return self.not_found(message=[24])
        return self.success(message=[25])


class OptionManagement(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(protected=True, check_user=True)
    @JsonValidation.validate
    def get(self, request):
        data = self.request.query_params

        try:
            product = Product.objects.get(uid=data['product_uid'])
        except Product.DoesNotExist:
            return self.not_found(message=[5])

        options = Option.objects.filter(product=product)

        return self.success(data={'product_options': list(map(self.serialize, options))})

    @MetaApiViewClass.generic_decor(protected=True, check_user=True)
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data
        try:
            product = Product.objects.get(uid=data['product_uid'])
        except Product.DoesNotExist:
            return self.not_found(message=[5])
        if self.user.uid != data['product_uid'].split('-')[0]:
            return self.bad_request(message=[18])
        user_uid = product.uid.split('-')[0]
        new_option = Option.objects.create(product=product, name=data['name'],
                                           is_public=data['is_public'], user_uid=user_uid)
        new_option.save()
        return self.success(message=[20])

    @MetaApiViewClass.generic_decor(protected=True, check_user=True)
    @JsonValidation.validate
    def delete(self, request):
        data = self.request.query_params

        try:
            Product.objects.get(data['product_uid'])
        except Product.DoesNotExist:
            return self.not_found(message=[5])
        if self.user.uid != data['product_uid'].split('-')[0]:
            return self.bad_request(message=[18])
        try:
            Option.objects.get(id=data['option_id']).delete()
        except Option.DoesNotExist:
            return self.not_found(message=[21])
        return self.success(message=[26])


class OptionValueManagement(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(protected=True, check_user=True)
    @JsonValidation.validate
    def get(self, request):
        data = self.request.query_params
        values = OptionValue.objects.filter(option_id=data['option_id'])
        if not values:
            return self.not_found(message=[22])
        return self.success(data={'option_values': list(map(self.serialize, values))})

    @MetaApiViewClass.generic_decor(protected=True, check_user=True)
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data
        try:
            option = Option.objects.get(id=data['option_id'])
        except Product.DoesNotExist:
            return self.not_found(message=[21])
        OptionValue.objects.create(option=option, value=data['value'], is_public=data['is_public'])
        return self.success(message=[23])

    @MetaApiViewClass.generic_decor(protected=True, check_user=True)
    @JsonValidation.validate
    def delete(self, request):
        data = self.request.query_params
        try:
            OptionValue.objects.get(id=data['option_value_id']).delete()
        except OptionValue.DoesNotExist:
            return self.not_found()
        return self.success(message=[27])
