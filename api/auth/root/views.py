from os import getenv
from django.db.models import Q

from auth.utils import MetaApiViewClass, OTPRecord, Security, JsonValidation
from .models import User, OTP, City, SalesMan, JobCategory, BlackList, Following


class FindUserByMobile(MetaApiViewClass):

    @MetaApiViewClass.generic_decor()
    @JsonValidation.validate
    def get(self, request):
        data = self.request.query_params
        user = None

        try:
            user = User.objects.filter(mobile=data.get('mobile')).order_by('-created_at')[0]

            check_deletion = not data.get('insert')
            self.check_user(user, raise_error=True, check_deletion=check_deletion, extra_messages=[5])

            deleted_account_limit_hours = data.get('deleted_account_limit_hours')
            if user.deleted_date and deleted_account_limit_hours:
                now = self.get_current_utc_time()
                if (now - user.deleted_date).seconds <= (deleted_account_limit_hours * 60 * 60):
                    return self.bad_request(message=[5])

        except IndexError:
            if not data.get('insert'):
                return self.not_found(message=[8])

        if not user and data.get('insert'):
            new_user = User.objects.create(mobile=data.get('mobile'))
            new_user.save()
            user = User.secure_objects.get(id=new_user.id)

        return self.success(data=self.serialize(user))


class FindUserByToken(MetaApiViewClass):

    __auth_token_key = getenv('AUTH_TOKEN_KEY')

    @MetaApiViewClass.generic_decor()
    def get(self, request):
        data = self.request.query_params
        token = self.request.headers.get(self.__auth_token_key)
        token_info = Security.decode_jwt_token(token)

        if not token_info or not token_info.get('user_id'):
            return self.bad_request(message=[9])

        if data.get('return_token_info'):
            return self.success(data={'token_info': token_info})

        try:
            user = User.objects.get(id=token_info['user_id'])
        except User.DoesNotExist:
            return self.bad_request(message=[8])

        self.check_user(user, raise_error=data.get('check_user'))

        user = self.serialize(user)

        return self.success(data={'user': user})


class CreateOtp(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(user_by_id=True)
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data

        try:
            confirmation_try = OTP.objects.filter(user=self.user).exclude(expire=0).order_by('-created_at')[2]
            now = self.get_current_utc_time()
            difference = (now - confirmation_try.created_at).seconds // (60 * 60)
            if difference < int(data['login_attempt_limit_hour']):
                return self.bad_request(message=[6])
        except IndexError:
            pass

        otp = OTPRecord.create_otp_fields(data['confirm_code_expire_minutes'], data['otp_code_length'])
        OTP.objects.create(user=self.user, created_by=self.user.id, **otp).save()

        res = self.get_req('config', url='/otp/', params={'otp_code': otp['code']}, return_data=True)
        # res = self.post_req('/sms/send-sms/', json_str={
        #     'receptor': self.user.mobile, 'message': res['body']
        # }, check_success=True)
        #
        if not res:
            return self.internal_error()
        return self.success(message=[10], data=res)

        # return self.success(message=[10], data={'code': otp['code']})


class ConfirmCode(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(user_by_id=True)
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data

        try:
            otp = OTP.objects.filter(user=self.user).order_by('-created_at')[0]
        except IndexError:
            return self.bad_request(message=[34])

        if otp.expire < self.get_current_time_in_milliseconds():
            return self.bad_request(message=[11])
        elif otp.try_count >= int(data['confirm_code_try_count_limit']):
            return self.bad_request(message=[12])

        otp.modified_by = self.user.id
        otp.try_count += 1

        if data['confirm_code'] != otp.code:
            otp.save()
            return self.bad_request(message=[13])

        otp.expire = 0
        otp.save()

        token = Security.generate_jwt_token(user_id=self.user.id)

        return self.success(message=[14], data={'token': token})


class UserProfile(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(user_by_id=True)
    @JsonValidation.validate
    def put(self, request):
        data = self.request.data

        data.pop('user_id')

        for item in data:
            setattr(self.user, item, data[item])

        self.user.modified_by = self.user.id
        self.user.save()

        return self.success(message=[15])

    @MetaApiViewClass.generic_decor(user_by_id=True, user_id_in_params=True)
    def delete(self, request):
        self.user.modified_by = self.user.id
        self.user.is_deleted = True
        self.user.deleted_date = self.get_current_utc_time()
        self.user.save()

        return self.success(message=[16])


class SalesManView(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(user_by_id=True, user_id_in_params=True)
    @JsonValidation.validate
    def get(self, request):
        try:
            sales_man = SalesMan.objects.filter(
                Q(is_deleted=False),
                Q(user=self.user) | Q(created_by=self.user.id)
            ).order_by('-created_at')[0]
        except IndexError:
            return self.not_found(message=[21])

        return self.success(data=self.serialize(sales_man))

    @MetaApiViewClass.generic_decor(user_by_id=True)
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data

        try:
            city = City.objects.get(id=data.pop('city_id'))
        except City.DoesNotExist:
            return self.bad_request(message=[17])

        try:
            job_category = JobCategory.objects.get(id=data.pop('job_category_id'))
        except JobCategory.DoesNotExist:
            return self.bad_request(message=[18])

        data['open_time'] = self.parse_iso_date(data['open_time'], 'time')
        data['close_time'] = self.parse_iso_date(data['close_time'], 'time')

        try:
            _ = SalesMan.objects.filter(
                Q(is_deleted=False),
                Q(user=self.user) | Q(username=data['username'])
            ).order_by('-created_at')[0]
            return self.bad_request(message=[19])
        except IndexError:
            SalesMan.objects.create(
                **data, user=self.user, city=city, job_category=job_category,
                uid=f'{self.add_lead_zero(city.code, 4)}-{self.user.uid}-{job_category.uid}',
                created_by=self.user.id
            ).save()

        return self.success(message=[20])

    @MetaApiViewClass.generic_decor(user_by_id=True)
    @JsonValidation.validate
    def put(self, request):
        data = self.request.data

        try:
            sales_man = SalesMan.objects.filter(
                Q(is_deleted=False),
                Q(user=self.user) | Q(created_by=self.user.id)
            ).order_by('-created_at')[0]
        except IndexError:
            return self.not_found(message=[21])

        data['open_time'] = self.parse_iso_date(data['open_time'], 'time')
        data['close_time'] = self.parse_iso_date(data['close_time'], 'time')

        data.pop('user_id')

        for item in data:
            setattr(sales_man, item, data[item])

        sales_man.modified_by = self.user.id
        sales_man.save()

        return self.success(message=[22])

    @MetaApiViewClass.generic_decor(user_by_id=True, user_id_in_params=True)
    @JsonValidation.validate
    def delete(self, request):
        try:
            sales_man = SalesMan.objects.filter(user=self.user, is_deleted=False).order_by('-created_at')[0]
        except IndexError:
            return self.not_found(message=[21])

        sales_man.modified_by = self.user.id
        self.user.is_deleted = True
        self.user.deleted_date = self.get_current_utc_time()

        return self.success(message=[35])


class Block(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(user_by_id=True, user_id_in_params=True)
    @JsonValidation.validate
    def get(self, request):
        banned_users = BlackList.objects.filter(user=self.user, created_by=self.user.id)

        black_list = [
            {'uid': usr.banned_user.uid, 'nick_name': usr.banned_user.nick_name}
            if not usr.banned_user.is_deleted else 'deleted_account' for usr in banned_users
        ]

        return self.success(data={'length': len(black_list), 'blackList': black_list})

    @MetaApiViewClass.generic_decor(user_by_id=True)
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data

        if self.user.id == data['banned_user_id']:
            return self.bad_request(message=[23])

        try:
            banned_user = User.objects.get(id=data['banned_user_id'])
        except User.DoesNotExist:
            return self.not_found(message=[8])

        self.check_user(banned_user)

        try:
            BlackList.objects.get(user=self.user, banned_user=banned_user)
            return self.bad_request(message=[24])
        except BlackList.DoesNotExist:
            BlackList.objects.create(user=self.user, banned_user=banned_user, created_by=self.user.id).save()

        return self.success(message=[25])

    @MetaApiViewClass.generic_decor(user_by_id=True, user_id_in_params=True)
    @JsonValidation.validate
    def delete(self, request):
        data = self.request.query_params

        try:
            banned_user = BlackList.objects.get(
                user=self.user, banned_user=data['banned_user_id'], created_by=self.user.id
            )
        except BlackList.DoesNotExist:
            return self.bad_request(message=[26])

        banned_user.delete()

        return self.success(message=[27])


class Follow(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(user_by_id=True, user_id_in_params=True)
    @JsonValidation.validate
    def get(self, request):
        followers = Following.objects.filter(user=self.user, created_by=self.user.id)

        follower_list = [
            {'uid': usr.followed.uid, 'nick_name': usr.followed.nick_name}
            for usr in followers if not usr.banned_user.is_deleted
        ]

        return self.success(data={'length': len(follower_list), 'followers': follower_list})

    @MetaApiViewClass.generic_decor(user_by_id=True)
    @JsonValidation.validate
    def post(self, request):
        data = self.request.data

        if self.user.id == data['followed_user_id']:
            return self.bad_request(message=[28])

        try:
            followed_user = User.objects.get(id=data['followed_user_id'])
        except User.DoesNotExist:
            return self.not_found(message=[8])

        self.check_user(followed_user)

        try:
            SalesMan.objects.filter(user=followed_user, is_deleted=False).order_by('-created_at')[0]
        except IndexError:
            return self.bad_request(message=[29])

        try:
            Following.objects.get(user=self.user, followed_user=data['followed_user_id'])
            return self.bad_request(message=[30])
        except Following.DoesNotExist:
            Following.objects.create(user=self.user, followed_user=followed_user, created_by=self.user.id).save()

        return self.success(message=[31])

    @MetaApiViewClass.generic_decor(user_by_id=True, user_id_in_params=True)
    @JsonValidation.validate
    def delete(self, request):
        data = self.request.query_params

        try:
            following = Following.objects.get(
                user=self.user, followed_user=data['followed_user_id'], created_by=self.user.id
            )
        except Following.DoesNotExist:
            return self.bad_request(message=[32])

        following.delete()

        return self.success(message=[33])
