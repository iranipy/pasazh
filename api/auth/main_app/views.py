import datetime
from .models import User, OTP, City, SalesMan
from .utils import MetaApiViewClass, OTPRecord, ResponseUtils, Security
from .serializers import UserSerializer


class FindUserByMobile(MetaApiViewClass):

    @MetaApiViewClass.generic_decor()
    def get(self, request):
        params_key = ['mobile', 'insert']
        params = self.get_params(self.request.query_params, params_key)

        try:
            user = User.objects.get(mobile=params['mobile'])
        except User.DoesNotExist:
            if not params['insert']:
                return self.not_found(message=['USER_NOT_FOUND'])

            new_user = User.objects.create(mobile=params['mobile'])
            new_user.save()
            user = User.objects.get(id=new_user.id)

        user = self.serialize(user)

        if ResponseUtils.check_user(user):
            return self.bad_request(message=['DELETED/BANNED_ACCOUNT'])

        return self.success(data=user)


##################################################################


class LoginTWO(MetaApiViewClass):
    def post(self, request):
        user = UserSerializer(data=self.request.data)
        if user.is_valid():
            user.save()
            return self.success()
        return self.bad_request(data={'error': user.errors})


##################################################################

class CreateOtp(MetaApiViewClass):

    @MetaApiViewClass.generic_decor()
    def post(self, request):
        params_key = ['user_id', 'login_attempt_limit_hour', 'confirm_code_expire_minutes']
        params = self.get_params(self.request.data, params_key)

        try:
            user = User.objects.get(id=params['user_id'])
        except User.DoesNotExist:
            return self.not_found(message=['USER_NOT_FOUND'])

        try:
            confirmation_try = OTP.objects.filter(user=user).exclude(expire=0).order_by('-created_at')[2]
            now = datetime.datetime.utcnow()
            confirmation_created_at = confirmation_try.created_at.replace(tzinfo=None)
            difference = (now - confirmation_created_at).seconds // (60 * 60)
            if difference < int(params['login_attempt_limit_hour']):
                return self.bad_request(message=['TOO_MANY_LOGIN_ATTEMPT'])
        except IndexError:
            pass

        otp = OTPRecord.create_fields(params['confirm_code_expire_minutes'])
        OTP.objects.create(user=user, **otp).save()

        return self.success(message=['CODE_SENT'], data={'code': otp['code']})  # for development purpose


class ConfirmCode(MetaApiViewClass):

    @MetaApiViewClass.generic_decor()
    def post(self, request):
        params_key = ['confirm_code', 'user_id', 'confirm_code_try_count_limit']
        params = self.get_params(self.request.data, params_key)

        user = User.objects.get(id=params['user_id'])
        if ResponseUtils.check_user(user):
            return self.bad_request(message=['DELETED/BANNED_ACCOUNT'])

        otp = OTP.objects.filter(user=user).order_by('-created_at')[0]

        if otp.expire < OTPRecord.current_time():
            return self.bad_request(message=['CODE_EXPIRED'])
        elif otp.try_count >= int(params['confirm_code_try_count_limit']):
            return self.bad_request(message=['TOO_MANY_REQUESTS'])

        otp.try_count += 1

        if params['confirm_code'] != otp.code:
            otp.save()
            return self.bad_request(message=['WRONG_CODE'])

        otp.expire = 0
        otp.save()

        token = Security.jwt_token_generator(user_id=user.id)

        return self.success(message=['CODE_CONFIRMED'], data={'token': token})


class FindUserByToken(MetaApiViewClass):

    @MetaApiViewClass.generic_decor()
    @MetaApiViewClass.check_token(True)
    def get(self, request):
        return self.success(data={'user_data': self.user, 'token_data': self.decoded_token})


class UserProfileUpdate(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(True)
    def put(self, request):
        params_key = ['nick_name', 'email', 'picture']
        params = self.get_params(self.request.data, params_key, required=False)
        for item in params:
            setattr(self.user, item, params[item])
        self.user.save()
        return self.success(message=['USER_UPDATED'])


class DeleteById(MetaApiViewClass):

    @MetaApiViewClass.generic_decor()
    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return self.not_found(message=['USER_DOES_NOT_EXIST'])
        if ResponseUtils.check_user(user):
            return self.bad_request(message=['DELETED/BANNED_ACCOUNT'])
        user.is_deleted = True
        user.save()
        return self.success(message=['USER_DELETED'])


class SalesManView(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(True)
    def post(self, request):
        params = self.get_params(self.request.data, [
            'store_name', 'city_id', 'address', 'open_time',
            'close_time', 'working_days', 'activity_type',
        ])
        try:
            city = City.objects.get(id=params['city_id'])
        except City.DoesNotExist:
            return self.bad_request(message=['INVALID_CITY_ID'])

        SalesMan.objects.create(
            user=self.user_by_id, store_name=params['store_name'], city=city, address=params['address'],
            open_time=params['open_time'], close_time=params['close_time'],
            working_days=params['working_days'], activity_type=params['activity_type'],
            uid=f'{ResponseUtils.standard_city_code(city.code)}-{self.user_by_id.uid}-{params["job_category"]}'
        ).save()

        return self.success(message=['SALESMAN_CREATED'])

    @MetaApiViewClass.generic_decor(True)
    def put(self, request):
        params_key = ['full_name', 'username', 'store_name', 'telephone', 'city', 'address',
                      'open_time', 'close_time', 'working_days', 'activity_type', 'is_private']
        params = self.get_params(self.request.data, params_key, required=False)
        for item in params:
            setattr(self.user.salesman, item, params[item])
        return self.success(message='SLAESMAN_UPDATED')
