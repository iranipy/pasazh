from os import getenv

from main.utils import MetaApiViewClass, JsonValidation


class Login(MetaApiViewClass):

    __login_attempt_limit_hour = getenv('LOGIN_ATTEMPT_LIMIT_HOUR')
    __confirm_code_expire_minutes = getenv('CONFIRM_CODE_EXPIRE_MINUTES')
    __otp_code_length = getenv('OTP_CODE_LENGTH')
    __deleted_account_limit_hours = getenv('DELETED_ACCOUNT_LIMIT_HOURS')

    @JsonValidation.validate
    def post(self, request):
        data = self.request.data

        user = self.auth_req.get('/find-user-by-mobile', params={
            'mobile': data['mobile'], 'insert': True,
            'deleted_account_limit_hours': self.__deleted_account_limit_hours
        }, return_data=True)

        self.auth_req.post('/create-otp', json={
            'user_id': int(user['id']),
            'login_attempt_limit_hour': int(self.__login_attempt_limit_hour),
            'confirm_code_expire_minutes': int(self.__confirm_code_expire_minutes),
            'otp_code_length': int(self.__otp_code_length)
        })

        return self.success()


class ConfirmCode(MetaApiViewClass):

    __confirm_code_try_count_limit = getenv('CONFIRM_CODE_TRY_COUNT_LIMIT')
    __deleted_account_limit_hours = getenv('DELETED_ACCOUNT_LIMIT_HOURS')

    @JsonValidation.validate
    def post(self, request):
        data = self.request.data

        user = self.auth_req.get('/find-user-by-mobile', params={
            'mobile': data['mobile'],
            'deleted_account_limit_hours': self.__deleted_account_limit_hours
        }, return_data=True)

        self.auth_req.post('/confirm-code', json={
            'confirm_code': data['confirm_code'],
            'user_id': int(user['id']),
            'confirm_code_try_count_limit': int(self.__confirm_code_try_count_limit)
        })


class Verify(MetaApiViewClass):

    @MetaApiViewClass.verify_token(check_user=True)
    def get(self, request):

        return self.success(data={'user': self.user})
