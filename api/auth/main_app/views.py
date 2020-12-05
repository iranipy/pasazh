from .models import User, OTP, City, SalesMan
from .utils import MetaApiViewClass, OTPRecord, Security, UserResponse


class Login(MetaApiViewClass):
    @MetaApiViewClass.generic_decor
    def post(self, request):
        params_key = ['mobile']
        params = self.get_params(self.request, params_key)
        try:
            user = User.objects.get(mobile=params['mobile'])
        except User.DoesNotExist:
            User.objects.create(mobile=params['mobile']).save()
            user = User.objects.get(mobile=params['mobile'])

        if UserResponse.check(user):
            return self.bad_request(message=['DELETED/BANNED_ACCOUNT'])
        record = OTPRecord()
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
            return self.bad_request(message=['WRONG_CODE'])
        if UserResponse.check(user):
            return self.bad_request(message=['DELETED/BANNED_ACCOUNT'])
        elif otp.expire < OTPRecord.current_time():
            return self.bad_request(message=['CODE_EXPIRED'])
        token = Security.jwt_token_generator(userid=user.id)
        otp.expire = 0
        otp.save()
        return self.success(message=['CODE_CONFIRMED'], data={'token': token})


class Verify(MetaApiViewClass):
    @MetaApiViewClass.generic_decor
    def post(self, request):
        params_key = ['authorization']
        params = self.get_params(self.request, params_key, option='header')
        token = Security.jwt_token_decoder(params['authorization'])
        if token:
            user = User.objects.get(pk=token['userid'])
            if UserResponse.check(user):
                return self.bad_request(message=['DELETED/BANNED_ACCOUNT'])
            user = UserResponse.serialize(user)
            return self.success(data=user)

        return self.bad_request(message=['TOKEN_EXPIRED'])


class DeleteAccount(MetaApiViewClass):
    @MetaApiViewClass.generic_decor
    def put(self, request):
        params_key = ['authorization']
        params = self.get_params(self.request, params_key, option='header')
        token = Security.jwt_token_decoder(params['authorization'])
        if token:
            user = User.objects.get(pk=token['userid'])
            if UserResponse.check(user):
                return self.bad_request(message=['DELETED/BANNED_ACCOUNT'])
            user.is_deleted = True
            user.save()
            return self.success(message=['USER_DELETED'])
        return self.bad_request(message=['TOKEN_EXPIRED'])


class SalesManView(MetaApiViewClass):
    @MetaApiViewClass.generic_decor
    def post(self, request):
        params_key = ['authorization']
        params = self.get_params(self.request, params_key, option='header')
        token = Security.jwt_token_decoder(params['authorization'])
        if token:
            user = User.objects.get(pk=token['userid'])
            if UserResponse.check(user):
                return self.bad_request(message=['DELETED/BANNED_ACCOUNT'])
            params_key = ['store_name', 'city', 'address', 'open_time',
                          'close_time', 'working_days', 'activity_type']

            params = self.get_params(self.request, params_key)

            city = City.objects.get(pk=params['city'])
            SalesMan.objects.create(store_name=params['store_name'], city=city, address=params['address'],
                                    open_time=params['open_time'], close_time=params['close_time'],
                                    working_days=params['working_days'],
                                    activity_type=params['activity_type']).save()
            return self.success(message=['CREATED'], data={'userid': user.id})
        return self.bad_request(message=['TOKEN_EXPIRED'])
