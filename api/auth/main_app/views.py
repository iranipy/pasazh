import datetime
from .models import User, OTP, City, SalesMan, JobCategory
from .utils import MetaApiViewClass, OTPRecord, ResponseUtils, Security
from .schema import JsonValidation


class FindUserByMobile(MetaApiViewClass):

    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def get(self, request):
        data = self.request.data
        try:
            user = User.objects.get(mobile=data['mobile'])
        except User.DoesNotExist:
            if not data['insert']:
                return self.not_found(message=['USER_NOT_FOUND'])

            new_user = User.objects.create(mobile=data['mobile'])
            new_user.save()
            user = User.objects.get(id=new_user.id)

        user = self.serialize(user)

        if ResponseUtils.check_user(user):
            return self.bad_request(message=['DELETED/BANNED_ACCOUNT'])

        return self.success(data=user)


class CreateOtp(MetaApiViewClass):

    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data
        try:
            user = User.objects.get(id=data['user_id'])
        except User.DoesNotExist:
            return self.not_found(message=['USER_NOT_FOUND'])

        try:
            confirmation_try = OTP.objects.filter(user=user).exclude(expire=0).order_by('-created_at')[2]
            now = datetime.datetime.utcnow()
            confirmation_created_at = confirmation_try.created_at.replace(tzinfo=None)
            difference = (now - confirmation_created_at).seconds // (60 * 60)
            if difference < int(data['login_attempt_limit_hour']):
                return self.bad_request(message=['TOO_MANY_LOGIN_ATTEMPT'])
        except IndexError:
            pass

        otp = OTPRecord.create_fields(data['confirm_code_expire_minutes'])
        OTP.objects.create(user=user, **otp).save()

        return self.success(message=['CODE_SENT'], data={'code': otp['code']})  # for development purpose


class ConfirmCode(MetaApiViewClass):

    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data
        user = User.objects.get(id=data['user_id'])
        if ResponseUtils.check_user(user):
            return self.bad_request(message=['DELETED/BANNED_ACCOUNT'])

        otp = OTP.objects.filter(user=user).order_by('-created_at')[0]

        if otp.expire < OTPRecord.current_time():
            return self.bad_request(message=['CODE_EXPIRED'])
        elif otp.try_count >= int(data['confirm_code_try_count_limit']):
            return self.bad_request(message=['TOO_MANY_REQUESTS'])

        otp.try_count += 1

        if data['confirm_code'] != otp.code:
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
    @JsonValidation.validate
    def put(self, request):
        data = self.request.data
        for item in data:
            setattr(self.user, item, data[item])
        self.user.save()
        return self.success(message=['USER_UPDATED'])


class DeleteAccountById(MetaApiViewClass):

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
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data

        try:
            city = City.objects.get(id=data['city_id'])
        except City.DoesNotExist:
            return self.bad_request(message=['INVALID_CITY_ID'])

        try:
            job_category = JobCategory.objects.get(id=data['job_category_id'])
        except City.DoesNotExist:
            return self.bad_request(message=['INVALID_JOB_CATEGORY_ID'])

        SalesMan.objects.create(
            user=self.user_by_id, store_name=data['store_name'], city=city, address=data['address'],
            open_time=data['open_time'], close_time=data['close_time'],
            working_days=data['working_days'], activity_type=data['activity_type'],
            uid=f'{ResponseUtils.standard_four_digits(city.code)}-{self.user_by_id.uid}-{job_category.uid}'
        ).save()

        return self.success(message=['SALESMAN_CREATED'])


# class UpdateSalesMan(MetaApiViewClass):
#     @MetaApiViewClass.generic_decor(True)
#     def put(self, request):
#         data = self.request.data
#         for item in data:
#             setattr(self.user.salesman, item, data[item])
#         return self.success(message='SALESMAN_UPDATED')
