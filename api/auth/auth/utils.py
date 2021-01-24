import time
import jwt
import datetime
import isodate
import fastjsonschema

import root.models as root_models

from os import getenv
from random import randint
from math import pow
from secrets import token_hex
from functools import wraps
from rest_framework.response import Response
from rest_framework import status as stat
from rest_framework.views import APIView
from django.forms.models import model_to_dict
from django.db import models
from django.urls import re_path

from .messages import messages
from .schema import schema


class AbstractModel(models.Model):
    created_at = models.DateTimeField(default=datetime.datetime.utcnow)
    modified_at = models.DateTimeField(default=datetime.datetime.utcnow)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()
        return super().save(*args, **kwargs)


class Helpers:

    @staticmethod
    def serialize(instance) -> dict:
        return model_to_dict(instance)

    @staticmethod
    def check_user(user, raise_error=True, check_deletion=True, extra_messages=None) -> bool:
        if extra_messages is None:
            extra_messages = []

        invalid_user = (check_deletion and user.is_deleted) or not user.is_active

        if invalid_user and raise_error:
            message = [7]
            if extra_messages and isinstance(extra_messages, list):
                message += extra_messages

            raise CustomResponse.BadRequest(message=message)

        return invalid_user

    @staticmethod
    def add_lead_zero(string: str, total_length: int) -> str:
        return ('0' * (total_length - len(string))) + string

    @staticmethod
    def parse_iso_date(iso_time, part='date_time') -> datetime:
        dt = isodate.parse_datetime(iso_time)
        if part == 'date':
            dt = dt.date()
        elif part == 'time':
            dt = dt.time()
        return dt

    @staticmethod
    def get_current_time_in_milliseconds() -> int:
        return int(round(time.time()) * 1000)

    @staticmethod
    def get_current_utc_time() -> datetime:
        return datetime.datetime.utcnow()

    @staticmethod
    def generate_rand_decimal(length: int) -> str:
        _min = int(pow(10, length - 1))
        _max = int(pow(10, length) - 1)
        return str(randint(_min, _max))

    @staticmethod
    def generate_url_item(url, view):
        url = f'^{url}/?$'
        return re_path(url, view.as_view(), name=url)

    @staticmethod
    def generate_table_name(prefix: str):
        def inner(name: str):
            return f'{prefix}_{name}'

        return inner


class Security:

    __secret_key = getenv('SECRET_KEY')

    @staticmethod
    def generate_hex(length: int) -> str:
        return token_hex(length)

    @staticmethod
    def generate_otp(length: int) -> str:
        return Helpers.generate_rand_decimal(length)

    @classmethod
    def generate_jwt_token(cls, **kwargs) -> str:
        kwargs['exp'] = datetime.datetime.utcnow() + datetime.timedelta(weeks=100)
        return jwt.encode(kwargs, cls.__secret_key)

    @classmethod
    def decode_jwt_token(cls, token: str):
        try:
            decoded_token = jwt.decode(token, cls.__secret_key)
        except jwt.exceptions.ExpiredSignatureError:
            return
        return decoded_token


class OTPRecord:

    @staticmethod
    def create_otp_fields(confirm_code_expire_minutes: int, otp_code_length: int) -> dict:
        return {
            'expire': int(round(time.time()) * 1000) + (1000 * 60 * int(confirm_code_expire_minutes)),
            'code': Security.generate_otp(otp_code_length)
        }


class CustomResponse:

    class CustomResponseException(Exception):

        def __init__(self, state='internal_error', message=None, data=None):
            if message is None:
                message = [4]
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
            'success': {'stat': stat.HTTP_200_OK, 'message': [1]},
            'not_found': {'stat': stat.HTTP_404_NOT_FOUND, 'message': [2]},
            'bad_request': {'stat': stat.HTTP_400_BAD_REQUEST, 'message': [3]},
            'internal_error': {'stat': stat.HTTP_500_INTERNAL_SERVER_ERROR, 'message': [4]},
        }[state]

    @classmethod
    def __generate_response(cls, state='success', message=None, data=None):
        status = cls.__get_status(state)
        if message is None:
            message = status['message']

        str_message = list(filter(lambda m: isinstance(m, str), message))

        result = {
            'message': [messages[m] for m in message if isinstance(m, int)],
            'state': state,
            'data': data,
        }

        if len(result['message']) != len(message) and len(str_message) > 0:
            result['message'] += str_message

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


class MetaApiViewClass(APIView, CustomResponse, Helpers):

    user = None

    @classmethod
    def generic_decor(cls, user_by_id=False, user_id_in_params=False, serialize=False):
        def decorator(func):
            def wrapper(*args, **kwargs):
                request = args[1]
                user_id = request.data.get('user_id')

                if user_id_in_params:
                    user_id = request.query_params.get('user_id')

                if user_by_id and user_id:
                    try:
                        user = root_models.User.objects.get(id=user_id)
                    except root_models.User.DoesNotExist:
                        return cls.not_found(message=[8])

                    cls.check_user(user)

                    cls.user = user
                    if serialize:
                        cls.user = cls.serialize(user)

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

            return wrapper

        return decorator


class JsonValidation:

    @staticmethod
    def find_schema(url, method):
        url_validator = schema.get(url)
        if not url_validator:
            return
        return url_validator.get(method)

    @classmethod
    def validate(cls, f):
        wraps(f)

        def decorator(*args, **kwargs):
            request = args[1]
            obj_to_validate = request.data

            curr_schema = cls.find_schema(request.path_info.replace('/', ''), request.method)
            if not curr_schema:
                return f(*args, **kwargs)

            if request.method in ['GET', 'DELETE']:
                obj_to_validate = {}
                for key in request.query_params:
                    obj_to_validate[key] = request.query_params.get(key)

            validate_schema = fastjsonschema.compile(curr_schema)
            validate_schema(obj_to_validate)

            return f(*args, **kwargs)

        return decorator
