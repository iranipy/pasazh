import time
import jwt
import datetime
import main_app.models as models
import isodate

from os import getenv
from random import randint
from math import pow
from secrets import token_hex
from rest_framework.response import Response
from rest_framework import status as stat
from rest_framework.views import APIView
from django.forms.models import model_to_dict
from functools import wraps


class Security:

    __secret_key = getenv('SECRET_KEY')

    @staticmethod
    def hex_generator():
        return token_hex(4)

    @staticmethod
    def otp_generator(length: int):
        _min = int(pow(10, length - 1))
        _max = int(pow(10, length) - 1)
        return str(randint(_min, _max))

    @classmethod
    def jwt_token_generator(cls, **kwargs):
        kwargs['exp'] = datetime.datetime.utcnow() + datetime.timedelta(weeks=100)
        return jwt.encode(kwargs, cls.__secret_key)

    @classmethod
    def jwt_token_decoder(cls, token: str):
        try:
            decoded_token = jwt.decode(token, cls.__secret_key)
        except jwt.exceptions.ExpiredSignatureError:
            return False
        return decoded_token


class OTPRecord:

    @classmethod
    def create_fields(cls, confirm_code_expire_minutes):
        return {
            'expire': int(round(time.time()) * 1000) + (1000 * 60 * int(confirm_code_expire_minutes)),
            'code': Security.otp_generator(6)
        }

    @staticmethod
    def current_time():
        return int(round(time.time()) * 1000)


class ResponseUtils:

    @staticmethod
    def serialize(instance):
        return model_to_dict(instance)

    @staticmethod
    def check_user(user):
        invalid_user = user.is_deleted or not user.is_active
        if invalid_user:
            raise CustomResponse.BadRequest(['DELETED/BANNED_ACCOUNT'])

    @staticmethod
    def standard_four_digits(code):
        return ('0' * (4 - len(code))) + code

    @staticmethod
    def iso_date_parser(iso_time, part) -> datetime:
        if part == 'date_time':
            dt = isodate.parse_datetime(iso_time)
        elif part == 'date':
            dt = isodate.parse_datetime(iso_time).date()
        elif part == 'time':
            dt = isodate.parse_datetime(iso_time).time()
        else:
            dt = None
        return dt


class CustomResponse:

    class CustomResponseException(Exception):

        def __init__(self, state='internal_error', message=None, data=None):
            if message is None:
                message = ['INTERNAL_ERROR']
            self.state = state
            self.message = message
            self.data = data

    class NotFound(CustomResponseException):

        def __init__(self, message, data=None):
            super().__init__('not_found', message, data)

    class BadRequest(CustomResponseException):

        def __init__(self, message, data=None):
            super().__init__('bad_request', message, data)

    @staticmethod
    def __get_status(state: str):
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
            'state': state,
            'data': data
        }
        return Response(data=result, status=status['stat'])

    @classmethod
    def general_response(cls, **kwargs):
        return cls.__generate_response(**kwargs)

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


class MetaApiViewClass(APIView, CustomResponse, ResponseUtils):

    __auth_token_key = getenv('AUTH_TOKEN_KEY')

    token_info = None
    user = None
    user_by_id = None

    @classmethod
    def get_params(cls, obj_to_check: dict, params_key: list, required=True):
        params = {}
        for p in params_key:
            params[p] = obj_to_check.get(p)
            if params[p] is None and required:
                raise cls.BadRequest([f'{p.upper()}_PARAMETER_IS_REQUIRED'])
        return params

    @classmethod
    def generic_decor(cls, user_by_id=False, user_id_in_params=True, serialize=False):
        def decorator(func):
            def inner(*args, **kwargs):
                request = args[1]
                user_id = request.data.get('user_id')
                if user_id_in_params:
                    user_id = request.query_params.get('user_id')

                if user_by_id and user_id:
                    try:
                        user = models.User.objects.get(id=user_id)
                    except models.User.DoesNotExist:
                        return cls.not_found(message=['USER_NOT_FOUND'])

                    cls.check_user(user)

                    cls.user_by_id = user
                    if serialize:
                        cls.user_by_id = cls.serialize(user_by_id)

                try:
                    return func(*args, **kwargs)
                except cls.NotFound as e:
                    return cls.not_found(message=e.message, data=e.data)
                except cls.BadRequest as e:
                    return cls.bad_request(message=e.message, data=e.data)
                except cls.CustomResponseException as e:
                    return cls.general_response(state=e.state, message=e.message, data=e.data)
                except Exception as e:
                    return cls.internal_error(message=[str(e)])

            return inner

        return decorator

    @classmethod
    def check_token(cls, serialize: bool):
        def decorator(f):
            wraps(f)

            def wrapper(*args, **kwargs):
                request = args[1]
                auth_token_key = cls.__auth_token_key
                params_key = [auth_token_key]
                params = cls.get_params(request.headers, params_key)
                cls.token_info = Security.jwt_token_decoder(params[auth_token_key])

                if not cls.token_info or not cls.token_info.get('user_id'):
                    return MetaApiViewClass.bad_request(message=['INVALID_TOKEN'])

                cls.user = models.User.objects.get(id=cls.token_info['user_id'])

                if serialize:
                    cls.user = cls.serialize(cls.user)
                    cls.check_user(cls.user)

                return f(*args, **kwargs)

            return wrapper

        return decorator
