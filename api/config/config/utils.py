import datetime
import fastjsonschema

from functools import wraps
from django.db import models
from django.urls import re_path
from django.forms.models import model_to_dict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as stat

from .messages import messages
from .schema import schema


class AbstractModel(models.Model):
    created_at = models.DateTimeField(default=datetime.datetime.utcnow)
    modified_at = models.DateTimeField(default=datetime.datetime.utcnow)
    created_by = models.BigIntegerField(default=-1)
    modified_by = models.BigIntegerField(default=-1)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = datetime.datetime.utcnow()
            self.modified_by = self.created_by

        self.modified_at = datetime.datetime.utcnow()

        return super().save(*args, **kwargs)


class Helpers:

    __general_exclude = ['created_by', 'created_at', 'modified_by', 'modified_at']

    @classmethod
    def serialize(cls, instance, fields=None, exclude=None, general_exclude=False) -> dict:
        if general_exclude:
            exclude = (exclude or []) + cls.__general_exclude

        return model_to_dict(instance, fields, exclude)

    @classmethod
    def serialize_list(cls, arr: list, fields=None, exclude=None, default_exclude=False) -> list:
        return list(map(
            lambda instance: cls.serialize(instance, fields, exclude, default_exclude),
            arr
        ))

    @staticmethod
    def generate_url_item(url, view):
        url = f'^{url}/?$'
        return re_path(url, view.as_view(), name=url)


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

    @classmethod
    def generic_decor(cls):
        def decorator(func):
            def wrapper(*args, **kwargs):
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

            curr_schema = cls.find_schema(request.path_info[1:], request.method)
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
