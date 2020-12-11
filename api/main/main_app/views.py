from os import getenv
from .utils import MetaApiViewClass


class Login(MetaApiViewClass):

    __login_attempt_limit_hour = getenv("LOGIN_ATTEMPT_LIMIT_HOUR")
    __confirm_code_expire_minutes = getenv("CONFIRM_CODE_EXPIRE_MINUTES")

    @MetaApiViewClass.generic_decor()
    def post(self, request):
        params_key = ['mobile']
        params = self.get_params(self.request.data, params_key)

        user = self.get_req("/find-user-by-mobile/", {
            'mobile': params['mobile'],
            'insert': True
        }, True)

        self.post_req("/create-otp/", {
            'user_id': user['id'],
            'login_attempt_limit_hour': self.__login_attempt_limit_hour,
            'confirm_code_expire_minutes': self.__confirm_code_expire_minutes
        })
