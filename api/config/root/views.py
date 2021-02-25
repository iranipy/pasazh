from config.utils import MetaApiViewClass
from .models import Configs


class Config(MetaApiViewClass):

    @MetaApiViewClass.generic_decor()
    def get(self, request):
        data = self.request.query_params

        try:
            config = Configs.objects.get(name=data.get('name'), is_active=True)
            return self.success(data=self.serialize(config))
        except IndexError:
            return self.not_found(message=[5])

    @MetaApiViewClass.generic_decor()
    def put(self, request):
        data = self.request.data

        try:
            config = Configs.objects.get(name=data.get('name'), is_active=True)
        except Configs.DoesNotExist:
            return self.not_found(message=[5])

        if not config.is_editable:
            return self.bad_request(message=[6])

        for attr in data:
            setattr(config, attr, data['attr'])

        config.save()

        return self.success(message=[7], data=self.serialize(config))
