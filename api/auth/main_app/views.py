from .models import User, OTP, City, SalesMan
from .utils import MetaApiViewClass, OTPRecord, Security, UserResponse


class Login(MetaApiViewClass):

    @MetaApiViewClass.generic_decor
    def post(self, request):
        params_key = ['mobile']
        params = self.get_params(self.request.data, params_key)

        try:
            user = User.objects.get(mobile=params['mobile'])
        except User.DoesNotExist:
            new_user = User.objects.create(mobile=params['mobile'])
            new_user.save()
            user = User.objects.get(id=new_user.id)

        if UserResponse.check(user):
            return self.bad_request(message=['DELETED/BANNED_ACCOUNT'])

        new_otp = OTP.objects.create(user=user, **OTPRecord.create_fields())
        new_otp.save()
        otp = OTP.objects.get(id=new_otp.id)

        return self.success(message=['CODE_SENT'], data={'confirm_code': otp.code})


class ConfirmCode(MetaApiViewClass):

    @MetaApiViewClass.generic_decor
    def post(self, request):
        params_key = ['confirm_code', 'mobile']
        params = self.get_params(self.request.data, params_key)

        try:
            user = User.objects.get(mobile=params['mobile'])
            otp = OTP.objects.filter(code=params['confirm_code'], user=user).order_by('-created_at')[0]
        except OTP.DoesNotExist:
            return self.bad_request(message=['WRONG_CODE'])

        if UserResponse.check(user):
            return self.bad_request(message=['DELETED/BANNED_ACCOUNT'])
        elif otp.expire < OTPRecord.current_time():
            return self.bad_request(message=['CODE_EXPIRED'])

        otp.expire = -1
        otp.save()

        token = Security.jwt_token_generator(user_id=user.id)

        return self.success(message=['CODE_CONFIRMED'], data={'token': token})


class Verify(MetaApiViewClass):

    @MetaApiViewClass.generic_decor
    def get(self, request):
        params_key = ['authorization']
        params = self.get_params(self.request.headers, params_key)

        token = Security.jwt_token_decoder(params['authorization'])
        if not token:
            return self.bad_request(message=['INVALID_TOKEN'])

        user = User.objects.get(id=token['user_id'])
        if UserResponse.check(user):
            return self.bad_request(message=['DELETED/BANNED_ACCOUNT'])

        user = UserResponse.serialize(user)
        return self.success(data=user)


class DeleteAccount(MetaApiViewClass):

    @MetaApiViewClass.generic_decor
    def put(self, request):
        params_key = ['authorization']
        params = self.get_params(self.request.headers, params_key)

        token = Security.jwt_token_decoder(params['authorization'])
        if not token:
            return self.bad_request(message=['INVALID_TOKEN'])

        user = User.objects.get(id=token['user_id'])
        if UserResponse.check(user):
            return self.bad_request(message=['DELETED/BANNED_ACCOUNT'])

        user.is_deleted = True
        user.save()

        return self.success(message=['USER_DELETED'])


class SalesManView(MetaApiViewClass):

    @MetaApiViewClass.generic_decor
    def post(self, request):
        params_key = ['authorization']
        params = self.get_params(self.request.headers, params_key)

        token = Security.jwt_token_decoder(params['authorization'])
        if not token:
            return self.bad_request(message=['INVALID_TOKEN'])

        user = User.objects.get(id=token['user_id'])
        if UserResponse.check(user):
            return self.bad_request(message=['DELETED/BANNED_ACCOUNT'])

        params_key = ['store_name', 'city_id', 'address', 'open_time',
                      'close_time', 'working_days', 'activity_type']

        params = self.get_params(self.request.data, params_key)

        city = City.objects.get(id=params['city_id'])

        SalesMan.objects.create(store_name=params['store_name'], city=city, address=params['address'],
                                open_time=params['open_time'], close_time=params['close_time'],
                                working_days=params['working_days'],
                                activity_type=params['activity_type']).save()

        return self.success(message=['SALESMAN_CREATED'], data={'userid': user.id})
