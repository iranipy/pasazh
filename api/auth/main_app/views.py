import datetime
from os import getenv
from .models import User, OTP, City, SalesMan
from .utils import MetaApiViewClass, OTPRecord, Security, UserResponse

login_limitation_hour = getenv("LOGIN_ATTEMPT_LIMIT_HOUR")


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
        try:
            confirmation_try = OTP.objects.filter(user=user).exclude(expire=0).order_by('-created_at')[2]
        except IndexError:
            otp = OTPRecord.create_fields()
            OTP.objects.create(user=user, **otp).save()

            return self.success(message=['CODE_SENT'], data={'confirm_code': otp['code']})
        difference = datetime.datetime.utcnow() - confirmation_try.created_at.replace(tzinfo=None)
        difference = difference.seconds // 3600
        if difference < login_limitation_hour:
            return self.bad_request(message=['TOO_MANY_LOGIN_ATTEMPT'])
        otp = OTPRecord.create_fields()
        OTP.objects.create(user=user, **otp).save()

        return self.success(message=['CODE_SENT'], data={'confirm_code': otp['code']})


class ConfirmCode(MetaApiViewClass):

    @MetaApiViewClass.generic_decor
    def post(self, request):
        params_key = ['confirm_code', 'mobile']
        params = self.get_params(self.request.data, params_key)

        user = User.objects.get(mobile=params['mobile'])
        otp = OTP.objects.filter(user=user).order_by('-created_at')[0]
        otp.try_count += 1
        otp.save()
        if UserResponse.check(user):
            return self.bad_request(message=['DELETED/BANNED_ACCOUNT'])
        elif otp.expire < OTPRecord.current_time():
            return self.bad_request(message=['CODE_EXPIRED'])
        elif otp.try_count > 4:
            return self.bad_request(message=['TOO_MANY_REQUEST'])
        elif not params['confirm_code'] == otp.code:
            return self.bad_request(message=['WRONG_CODE'])

        otp.expire = 0
        otp.save()

        token = Security.jwt_token_generator(user_id=user.id)

        return self.success(message=['CODE_CONFIRMED'], data={'token': token})


class Verify(MetaApiViewClass):

    @MetaApiViewClass.generic_decor
    @MetaApiViewClass.check_token(serialize=True)
    def get(self, request):
        return self.success(data=self.user_info)


class DeleteAccount(MetaApiViewClass):

    @MetaApiViewClass.generic_decor
    @MetaApiViewClass.check_token(serialize=False)
    def put(self, request):
        self.user.is_deleted = True
        self.user.save()
        return self.success(message=['USER_DELETED'])


class SalesManView(MetaApiViewClass):

    @MetaApiViewClass.generic_decor
    @MetaApiViewClass.check_token(serialize=False)
    def post(self, request):
        params_key = ['store_name', 'city_id', 'address', 'open_time',
                      'close_time', 'working_days', 'activity_type']

        params = self.get_params(self.request.data, params_key)

        city = City.objects.get(id=params['city_id'])

        SalesMan.objects.create(store_name=params['store_name'], city=city, address=params['address'],
                                open_time=params['open_time'], close_time=params['close_time'],
                                working_days=params['working_days'],
                                activity_type=params['activity_type']).save()

        return self.success(message=['SALESMAN_CREATED'], data={'userid': self.user.id})
