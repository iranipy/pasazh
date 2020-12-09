import datetime
from os import getenv
from .models import User, OTP, City, SalesMan
from .utils import MetaApiViewClass, OTPRecord, Security, UserResponse


class Login(MetaApiViewClass):

    __login_attempt_limit_hour = getenv("LOGIN_ATTEMPT_LIMIT_HOUR")

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
            now = datetime.datetime.utcnow()
            confirmation_created_at = confirmation_try.created_at.replace(tzinfo=None)
            difference = (now - confirmation_created_at).seconds // (60 * 60)
            if difference < int(self.__login_attempt_limit_hour):
                return self.bad_request(message=['TOO_MANY_LOGIN_ATTEMPT'])
        except IndexError:
            pass

        otp = OTPRecord.create_fields()
        OTP.objects.create(user=user, **otp).save()

        return self.success(message=['CODE_SENT'], data={'confirm_code': otp['code']})


class ConfirmCode(MetaApiViewClass):

    __confirm_code_try_count_limit = getenv("CONFIRM_CODE_TRY_COUNT_LIMIT")

    @MetaApiViewClass.generic_decor
    def post(self, request):
        params_key = ['confirm_code', 'mobile']
        params = self.get_params(self.request.data, params_key)

        user = User.objects.get(mobile=params['mobile'])
        if UserResponse.check(user):
            return self.bad_request(message=['DELETED/BANNED_ACCOUNT'])

        otp = OTP.objects.filter(user=user).order_by('-created_at')[0]

        if otp.expire < OTPRecord.current_time():
            return self.bad_request(message=['CODE_EXPIRED'])
        elif otp.try_count >= int(self.__confirm_code_try_count_limit):
            return self.bad_request(message=['TOO_MANY_REQUESTS'])

        otp.try_count += 1

        if params['confirm_code'] != otp.code:
            otp.save()
            return self.bad_request(message=['WRONG_CODE'])

        otp.expire = 0
        otp.save()

        token = Security.jwt_token_generator(user_id=user.id)

        return self.success(message=['CODE_CONFIRMED'], data={'token': token})


class Verify(MetaApiViewClass):

    @MetaApiViewClass.generic_decor
    @MetaApiViewClass.check_token(True)
    def get(self, request):
        return self.success(data=self.user)


class DeleteAccount(MetaApiViewClass):

    @MetaApiViewClass.generic_decor
    @MetaApiViewClass.check_token(False)
    def put(self, request):
        self.user.is_deleted = True
        self.user.save()
        return self.success(message=['USER_DELETED'])


class SalesManView(MetaApiViewClass):

    @MetaApiViewClass.generic_decor
    @MetaApiViewClass.check_token(False)
    def post(self, request):
        params = self.get_params(self.request.data, [
            'store_name', 'city_id', 'address', 'open_time',
            'close_time', 'working_days', 'activity_type'
        ])

        city = City.objects.get(id=params['city_id'])
        if not city:
            return self.bad_request(message=['INVALID_CITY_ID'])

        SalesMan.objects.create(
            store_name=params['store_name'], city=city, address=params['address'],
            open_time=params['open_time'], close_time=params['close_time'],
            working_days=params['working_days'], activity_type=params['activity_type']
        ).save()

        return self.success(message=['SALESMAN_CREATED'])
