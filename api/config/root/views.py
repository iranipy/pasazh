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
        data['modified_by'] = data.pop('user_id')

        try:
            config = Configs.objects.get(name=data.get('name'), is_active=True)
        except Configs.DoesNotExist:
            return self.not_found(message=[5])

        if not config.is_editable:
            return self.bad_request(message=[6])

        for item in data:
            setattr(config, item, data[item])

        config.save()

        return self.success(message=[7], data=self.serialize(config))


class OTPConfig(MetaApiViewClass):
    @MetaApiViewClass.generic_decor()
    def get(self, request):
        data = self.request.query_params
        otp_code = data.get('otp_code')
        config_text = Configs.objects.filter(name='OTP')[0]
        body = f'{config_text.value}: {otp_code}'
        return self.success(data={'body': body})
