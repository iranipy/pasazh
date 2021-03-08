import requests
import fastjsonschema
import datetime

from os import getenv
from functools import wraps
from random import randint
from rest_framework.response import Response
from rest_framework import status as stat
from rest_framework.views import APIView, exception_handler
from django.forms.models import model_to_dict
from django.db import models
from django.urls import re_path

from .messages import messages
from .schema import schema


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, CustomResponse.NotFound):
        return CustomResponse.not_found(message=exc.message, data=exc.data)
    elif isinstance(exc, CustomResponse.BadRequest):
        return CustomResponse.bad_request(message=exc.message, data=exc.data)
    elif isinstance(exc, CustomResponse.CustomResponseException):
        return CustomResponse.general_response(state=exc.state, message=exc.message, data=exc.data)
    elif isinstance(exc, Exception):
        return CustomResponse.internal_error(message=[str(exc)])

    return response


class CustomManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().defer(*Helpers.general_exclude)


class AbstractModel(models.Model):
    created_at = models.DateTimeField(default=datetime.datetime.utcnow)
    modified_at = models.DateTimeField(default=datetime.datetime.utcnow)
    created_by = models.BigIntegerField(default=-1)
    modified_by = models.BigIntegerField(default=-1)
    is_active = models.BooleanField(default=True)
    secure_objects = CustomManager()
    objects = models.Manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = datetime.datetime.utcnow()
            self.modified_by = self.created_by

        self.modified_at = datetime.datetime.utcnow()

        return super().save(*args, **kwargs)


class Helpers:

    general_exclude = ['created_by', 'created_at', 'modified_by', 'modified_at']

    @classmethod
    def serialize(cls, instance, fields=None, exclude=None, general_exclude=False) -> dict:
        if general_exclude:
            exclude = (exclude or []) + cls.general_exclude

        return model_to_dict(instance, fields, exclude)

    @classmethod
    def serialize_list(cls, arr: list, fields=None, exclude=None, default_exclude=False) -> list:
        return list(map(
            lambda instance: cls.serialize(instance, fields, exclude, default_exclude),
            arr
        ))

    @staticmethod
    def generate_rand_decimal(length: int) -> int:
        _min = int(pow(10, length - 1))
        _max = int(pow(10, length) - 1)
        return randint(_min, _max)

    @staticmethod
    def generate_url_item(url, view):
        url = f'^{url}/?$'
        return re_path(url, view.as_view(), name=url)

    @staticmethod
    def generate_table_name(prefix: str):
        def inner(name: str):
            return f'{prefix}_{name}'

        return inner


class CustomRequest:

    __base_url = f'http://{getenv("HOST")}'

    def __init__(self, project_name):
        project_port = {
            'auth': getenv("AUTH_PORT"),
        }[project_name]

        self.__base_url += f':{project_port}'

    @staticmethod
    def __handle_request(response, return_data=False, check_success=False):
        response_json = response.json()

        data = response_json.get('data')
        state = response_json.get('state')

        status = state and CustomResponse.get_status(state)
        if check_success and status:
            return state and status['state'] == stat.HTTP_200_OK

        if return_data and data:
            return data

        raise CustomResponse.CustomResponseException(**response_json)

    def __generate_url(self, url):
        return f'{self.__base_url}{url}'

    def get(self, url, params=None, return_data=False, check_success=False, **kwargs):
        if params is None:
            params = {}
        response = requests.get(self.__generate_url(url), params, **kwargs)
        return self.__handle_request(response, return_data, check_success)

    def post(self, url, data=None, return_data=False, check_success=False, **kwargs):
        if data is None:
            data = {}
        response = requests.post(self.__generate_url(url), data, **kwargs)
        return self.__handle_request(response, return_data, check_success)

    def put(self, url, data=None, return_data=False, check_success=False, **kwargs):
        if data is None:
            data = {}
        response = requests.put(self.__generate_url(url), data, **kwargs)
        return self.__handle_request(response, return_data, check_success)

    def delete(self, url, params=None, return_data=False, check_success=False, **kwargs):
        if params is None:
            params = {}
        response = requests.delete(self.__generate_url(url), params=params, **kwargs)
        return self.__handle_request(response, return_data, check_success)


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
    def get_status(state: str):
        return {
            'success': {'state': stat.HTTP_200_OK, 'message': [1]},
            'not_found': {'state': stat.HTTP_404_NOT_FOUND, 'message': [2]},
            'bad_request': {'state': stat.HTTP_400_BAD_REQUEST, 'message': [3]},
            'internal_error': {'state': stat.HTTP_500_INTERNAL_SERVER_ERROR, 'message': [4]},
        }[state]

    @classmethod
    def __generate_response(cls, state='success', message=None, data=None):
        status = cls.get_status(state)
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

        return Response(data=result, status=status['state'])

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


class MetaApiViewClass(APIView, Helpers, CustomResponse):

    __auth_token_key = getenv('AUTH_TOKEN_KEY')

    token_info = None
    user = None
    auth_req = CustomRequest('auth')

    @classmethod
    def verify_token(cls, return_token_info=False, check_user=False):
        def decorator(func):
            def wrapper(*args, **kwargs):
                request = args[1]
                auth_token_key = cls.__auth_token_key
                token = request.headers.get(auth_token_key)

                params = {
                    "return_token_info": return_token_info,
                    "check_user": check_user,
                }

                res = cls.auth_req.get(
                    '/find-user-by-token/', params=params, return_data=True,
                    headers={auth_token_key: token}
                )

                cls.token_info = res.get('token_info')
                cls.user = res.get('user')

                if check_user and not cls.user:
                    return cls.not_found(message=[19])

                return func(*args, **kwargs)

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
            bool_val = {'true': True, 'false': False}

            curr_schema = cls.find_schema(request.path_info[1:], request.method)
            if not curr_schema:
                return f(*args, **kwargs)

            if request.method in ['GET', 'DELETE'] and request.query_params:
                obj_to_validate = {}
                for key in request.query_params:
                    obj_to_validate[key] = request.query_params.get(key)

            for key in obj_to_validate:
                val = obj_to_validate[key]
                if not isinstance(val, str):
                    continue

                val = bool_val.get(val.lower())
                if isinstance(val, bool):
                    obj_to_validate[key] = val

            validate_schema = fastjsonschema.compile(curr_schema)
            validate_schema(obj_to_validate)

            return f(*args, **kwargs)

        return decorator
