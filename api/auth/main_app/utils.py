import time
import jwt
import datetime
import main_app.models as models
from os import getenv
from random import randint
from math import pow
from secrets import token_hex
from rest_framework.response import Response
from rest_framework import status as stat
from rest_framework.views import APIView
from django.forms.models import model_to_dict
from functools import wraps
a = 2

class Security:
    __secret = getenv("SECRET_KEY")

    @staticmethod
    def hex_generator():
        return token_hex(4)

    @staticmethod
    def otp_generator(length):
        _min = int(pow(10, length - 1))
        _max = int(pow(10, length) - 1)
        return str(randint(_min, _max))

    @classmethod
    def jwt_token_generator(cls, **kwargs):
        kwargs['exp'] = datetime.datetime.utcnow() + datetime.timedelta(weeks=100)
        return jwt.encode(kwargs, cls.__secret)

    @classmethod
    def jwt_token_decoder(cls, token):
        try:
            decoded_token = jwt.decode(token, cls.__secret)
        except jwt.exceptions.ExpiredSignatureError:
            return False
        return decoded_token


class CustomResponse:

    @staticmethod
    def __get_status(state):
        return {
            'success': {'stat': stat.HTTP_200_OK, 'message': ['OK']},
            'not_found': {'stat': stat.HTTP_404_NOT_FOUND, 'message': ['NOT_FOUND']},
            'bad_request': {'stat': stat.HTTP_400_BAD_REQUEST, 'message': ['BAD_REQUEST']},
            'internal_error': {'stat': stat.HTTP_500_INTERNAL_SERVER_ERROR, 'message': ['INTERNAL_ERROR']}
        }[state]

    @classmethod
    def __generate_response(cls, state='success', message=None, data=None):
        status = cls.__get_status(state)
        if message is None:
            message = status['message']
        result = {
            'message': [m for m in message if isinstance(m, str)],
            'status': status['stat'],
            'data': data
        }
        return Response(data=result, status=status['stat'])

    @classmethod
    def success(cls, **kwargs):
        return cls.__generate_response(state='success', **kwargs)

    @classmethod
    def not_found(cls, **kwargs):
        return cls.__generate_response(state='not_found', **kwargs)

    @classmethod
    def bad_request(cls, **kwargs):
        return cls.__generate_response(state='bad_request', **kwargs)

    @classmethod
    def internal_error(cls, **kwargs):
        return cls.__generate_response(state='internal_error', **kwargs)


class MetaApiViewClass(APIView):
    success = CustomResponse.success
    not_found = CustomResponse.not_found
    bad_request = CustomResponse.bad_request
    internal_error = CustomResponse.internal_error
    user = None
    user_info = None

    class NotFound(Exception):
        def __init__(self, message):
            self.message = message

    class BadRequest(Exception):
        def __init__(self, message):
            self.message = message

    @classmethod
    def get_params(self, obj_to_check, params_key):
        params = {}
        for p in params_key:
            params[p] = obj_to_check.get(p)
            if params[p] is None:
                raise self.BadRequest([f'{p.upper()}_PARAMETER_IS_REQUIRED'])
        return params

    @classmethod
    def generic_decor(cls, func):
        def inner(self, request):
            try:
                return func(self, request)
            except cls.NotFound as e:
                return cls.not_found(message=e.message)
            except cls.BadRequest as e:
                return cls.bad_request(message=e.message)
            except Exception as e:
                return cls.internal_error(message=[str(e)])

        return inner

    @classmethod
    def check_token(cls, serialize: bool):
        def decorator(f):
            wraps(f)

            def wrapper(*args, **kwargs):
                params_key = ['authorization']
                params = cls.get_params(args[1].headers, params_key)
                token = Security.jwt_token_decoder(params['authorization'])
                if not token:
                    return MetaApiViewClass.bad_request(message=['INVALID_TOKEN'])
                cls.user = models.User.objects.get(id=token['user_id'])
                if UserResponse.check(cls.user):
                    return cls.bad_request(message=['DELETED/BANNED_ACCOUNT'])
                if serialize:
                    cls.user_info = UserResponse.serialize(cls.user)
                return f(*args, **kwargs)

            return wrapper
        return decorator


class OTPRecord:

    @staticmethod
    def create_fields():
        return {
            'expire': int(round(time.time()) * 1000) + (1000 * 60 * int(getenv("CONFIRM_CODE_EXPIRE_MINUTES"))),
            'code': Security.otp_generator(6)
        }

    @staticmethod
    def current_time():
        return int(round(time.time()) * 1000)


class UserResponse:

    @staticmethod
    def serialize(instance):
        return model_to_dict(instance)

    @staticmethod
    def check(instance):
        return instance.is_deleted or not instance.is_active
