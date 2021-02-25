from config.utils import MetaApiViewClass
from .models import ConfigMessages


class ConfigRetrieve(MetaApiViewClass):
    @MetaApiViewClass.generic_decor()
    def get(self, request):
        data = self.request.query_params
        config = ConfigMessages.objects.filter(name=data.get('name'), is_active=True)
        try:
            return self.success(data=self.serialize(config[0]))
        except IndexError:
            return self.not_found(message=[1])

    @MetaApiViewClass.generic_decor()
    def put(self, request):
        data = self.request.data
        try:
            config = ConfigMessages.objects.filter(name=data['name'], is_active=True)[0]
        except IndexError:
            return self.not_found(message=[1])
        if not config.is_editable:
            return self.bad_request(message=[2])
        for attr in data:
            setattr(config, attr, data['attr'])
        config.save()
        return self.success(message=[3], data=self.serialize(config))

