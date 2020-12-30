import datetime
from .models import User, OTP, City, SalesMan, JobCategory, BlackList, Following
from .utils import MetaApiViewClass, OTPRecord, ResponseUtils, Security
from .schema import JsonValidation
from rest_framework import response, reverse
from .serializers import UserSerializer


class FindUserByMobile(MetaApiViewClass):

    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def get(self, request):
        data = self.request.query_params
        mobile_number = data['mobile']
        try:
            user = User.objects.get(mobile=mobile_number)
        except User.DoesNotExist:
            if not data['insert']:
                return self.not_found(message=['USER_NOT_FOUND'])
            new_user = User.objects.create(mobile=mobile_number)
            new_user.save()
            user = User.objects.get(id=new_user.id)

        if ResponseUtils.check_user(user):
            return self.bad_request(message=['DELETED/BANNED_ACCOUNT'])
        user = self.serialize(user)

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
        try:
            user = User.objects.get(id=data['user_id'])
        except User.DoesNotExist:
            return self.not_found(message=['USER_NOT_FOUND'])
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


class UserProfile(MetaApiViewClass):
    @MetaApiViewClass.generic_decor()
    def get(self, request):
        if self.request.user.is_superuser:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return response.Response(serializer.data)
        return self.bad_request(message=['PERMISSION_DENIED'])

    @MetaApiViewClass.generic_decor(True)
    @JsonValidation.validate
    def put(self, request):
        data = self.request.data
        for item in data:
            if item == 'user_id':
                continue

            setattr(self.user_by_id, item, data[item])
        self.user_by_id.save()
        return self.success(message=['USER_UPDATED'])


class DeleteAccountById(MetaApiViewClass):

    @MetaApiViewClass.generic_decor()
    def delete(self, request):
        try:
            user = User.objects.get(id=self.request.query_params.get('user_id'))
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
        except JobCategory.DoesNotExist:
            return self.bad_request(message=['INVALID_JOB_CATEGORY_ID'])
        open_time = ResponseUtils.iso_date_parser(data['open_time'], 'time')
        close_time = ResponseUtils.iso_date_parser(data['close_time'], 'time')
        try:
            _ = SalesMan.objects.filter(user=self.user_by_id.id)[0]
            return self.bad_request(message=['SALESMAN_PROFILE_ALREADY_EXIST'])
        except IndexError:
            SalesMan.objects.create(
                user=self.user_by_id, store_name=data['store_name'], job_category=job_category,
                city=city, address=data['address'], open_time=open_time, close_time=close_time,
                working_days=data['working_days'], activity_type=data['activity_type'],
                uid=f'{ResponseUtils.standard_four_digits(city.code)}-{self.user_by_id.uid}-{job_category.uid}'
            ).save()

        return self.success(message=['SALESMAN_CREATED'])

    @MetaApiViewClass.generic_decor(True)
    @JsonValidation.validate
    def put(self, request):
        data = self.request.data
        try:
            salesman = SalesMan.objects.filter(user=self.user_by_id)[0]
        except IndexError:
            return self.not_found(message=['SALESMAN_PROFILE_NOT_FOUND'])
        self.request.data['open_time'] = ResponseUtils.iso_date_parser(data['open_time'], 'time')
        self.request.data['close_time'] = ResponseUtils.iso_date_parser(data['close_time'], 'time')
        for item in data:
            if item == 'user_id':
                continue
            setattr(salesman, item, data[item])
        salesman.save()
        return self.success(message=['SALESMAN_UPDATED'])


class Block(MetaApiViewClass):
    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def get(self, request):
        user = User.objects.get(id=self.request.query_params['user_id'])
        banned_users = BlackList.objects.filter(user=user)
        black_list = {usr.banned_user.mobile: usr.banned_user.nick_name if usr.banned_user.nick_name else None for usr
                      in banned_users}

        return self.success(data={'BlackList': black_list})

    @MetaApiViewClass.generic_decor(True)
    @JsonValidation.validate
    def post(self, request):
        if self.user_by_id.id == self.request.data['banned_user_id']:
            return self.bad_request(message=['USERS_CAN_NOT_BLOCK_THEMSELVES'])
        try:
            banned_user = User.objects.get(id=self.request.data['banned_user_id'])
        except User.DoesNotExist:
            return self.not_found(message=['USER_NOT_FOUND'])
        try:
            _ = BlackList.objects.filter(user=self.request.data['user_id'],
                                         banned_user=self.request.data['banned_user_id'])[0]
            return self.bad_request(message=['USER_ALREADY_IS_IN_BLACKLIST'])
        except IndexError:
            BlackList.objects.create(user=self.user_by_id, banned_user=banned_user).save()
            return self.success(message=['USER_BANNED'])

    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def delete(self, request):
        try:
            banned_user = BlackList.objects.filter(user=self.request.query_params['user_id'],
                                                   banned_user=self.request.query_params['banned_user_id'])[0]
        except IndexError:
            return self.bad_request(message=['USER_IS_NOT_IN_BLACKLIST'])
        banned_user.delete()
        return self.success(message=['USER_UNBANNED'])


class Follow(MetaApiViewClass):
    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def get(self, request):
        try:
            user = User.objects.get(id=self.request.query_params['user_id'])
        except User.DoesNotExist:
            return self.not_found(message=['USER_NOT_FOUND'])
        followers = Following.objects.filter(user=user)
        followers_list = {usr.followed_user.mobile: usr.followed_user.nick_name if usr.followed_user.nick_name else None
                          for
                          usr in followers}

        return self.success(data={'follower_count': len(followers_list), 'followers': followers_list})

    @MetaApiViewClass.generic_decor(True)
    @JsonValidation.validate
    def post(self, request):
        if self.user_by_id.id == self.request.data['followed_user_id']:
            return self.bad_request(message=['USERS_CAN_NOT_FOLLOW_THEMSELVES'])
        try:
            followed_user = User.objects.get(id=self.request.data['followed_user_id'])
        except User.DoesNotExist:
            return self.not_found(message=['USER_NOT_FOUND'])
        if ResponseUtils.check_user(followed_user):
            return self.bad_request(message=['DELETED/BANNED_ACCOUNT'])
        second_user = SalesMan.objects.filter(user=followed_user)
        if not second_user:
            return self.bad_request(message=['FOLLOWING_NON_SALESMAN_USERS_IS_UNAVAILABLE'])
        try:
            _ = Following.objects.filter(user=self.request.data['user_id'],
                                         followed_user=self.request.data['followed_user_id'])[0]
            return self.bad_request(message=['USER_ALREADY_IS_IN_FOLLOWINGS'])
        except IndexError:
            Following.objects.create(user=self.user_by_id, followed_user=followed_user).save()
            return self.success(message=['USER_FOLLOWED'])

    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def delete(self, request):
        try:
            following = Following.objects.filter(user=self.request.query_params['user_id'],
                                                 followed_user=self.request.query_params['followed_user_id'])[0]
        except IndexError:
            return self.bad_request(message=['USER_IS_NOT_IN_FOLLOWINGS'])
        following.delete()
        return self.success(message=['USER_UNFOLLOWED'])


class APIRoot(MetaApiViewClass):
    def get(self, request, format=None):
        return response.Response({
            reverse.reverse('find-user-by-mobile', request=request, format=format),
            reverse.reverse('create-otp', request=request, format=format),
            reverse.reverse('confirm-code', request=request, format=format),
            reverse.reverse('find-user-by-token', request=request, format=format),
            reverse.reverse('delete-account-by-id', request=request, format=format),
            reverse.reverse('user-profile', request=request, format=format),
            reverse.reverse('salesman-profile', request=request, format=format),
            reverse.reverse('block-user', request=request, format=format),
            reverse.reverse('follow-user', request=request, format=format),
        })
