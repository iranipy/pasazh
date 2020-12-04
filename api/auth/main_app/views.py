from .models import User
from .utils import MetaApiViewClass, OTPRecord, Security
from .models import OTP


class Login(MetaApiViewClass):
    @MetaApiViewClass.generic_decor
    def post(self, request):
        params_key = ['mobile']
        params = self.get_params(self.request, params_key)
        try:
            User.objects.get(mobile=params['mobile'])
        except User.DoesNotExist:
            User.objects.create(mobile=params['mobile']).save()

        record = OTPRecord()
        user = User.objects.get(mobile=params['mobile'])
        OTP.objects.create(code=record.code, expire=record.expire, user=user).save()
        otp = OTP.objects.filter(user=user).order_by('-created_at')[0]
        return self.success(message=['USER_CREATED', 'CODE_SENT'], data={'userid': user.id, 'otp': otp.code})


class ConfirmCode(MetaApiViewClass):

    @MetaApiViewClass.generic_decor
    def post(self, request):
        params_key = ['confirm_code', 'mobile']
        params = self.get_params(self.request, params_key)
        try:
            user = User.objects.get(mobile=params['mobile'])
            otp = OTP.objects.filter(code=params['confirm_code'], user=user).order_by('-created_at')[0]
        except OTP.DoesNotExist:
            return self.NotFound(message=['WRONG_CODE'])

        if otp.expire < OTPRecord.current_time():
            return self.success(message=['CODE_EXPIRED'])
        token = Security.jwt_token_generator(userid=user.id)
        otp.expire = 0
        otp.save()
        return self.success(message=['CODE_CONFIRMED'], data={'token': token})


class Verify(MetaApiViewClass):
    @MetaApiViewClass.generic_decor
    def post(self, request):
        params_key = ['token']
        params = self.get_params(self.request, params_key)
        token = Security.jwt_token_decoder(params['token'])
        if token:
            user = User.objects.get(pk=token['userid'])
            return self.success(data=user.mobile)  # TEST
        return self.success(message=['TOKEN_EXPIRED'])


class DeleteAccount(MetaApiViewClass):
    @MetaApiViewClass.generic_decor
    def put(self, request):
        params_key = ['token']
        params = self.get_params(self.request, params_key)
        token = Security.jwt_token_decoder(params['token'])
        if token:
            user = User.objects.get(pk=token['userid'])
            user.is_active = False
            user.is_deleted = True
            user.save()
            return self.success(message=['USER_DELETED'])
        return self.success(message=['TOKEN_EXPIRED'])
