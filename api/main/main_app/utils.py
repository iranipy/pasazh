import requests

from os import getenv
from rest_framework.response import Response
from rest_framework import status as stat
from rest_framework.views import APIView
from django.forms import model_to_dict
from random import randint


class ResponseUtils:

    @staticmethod
    def serialize(instance):
        return model_to_dict(instance)

    @staticmethod
    def rand_digit(length: int):
        _min = int(pow(10, length - 1))
        _max = int(pow(10, length) - 1)
        return str(randint(_min, _max))


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
            super().__init__("not_found", message, data)

    class BadRequest(CustomResponseException):
        def __init__(self, message, data=None):
            super().__init__("bad_request", message, data)

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


class CustomRequest:

    __base_url = f"http://{getenv('HOST')}:{getenv('AUTH_PORT')}"

    @classmethod
    def __generate_url(cls, url):
        return f"{cls.__base_url}{url}"

    @staticmethod
    def __handle_request(response, return_data):
        response_json = response.json()
        data = response_json.get('data')
        if return_data and data:
            return data
        raise CustomResponse.CustomResponseException(**response_json)

    @classmethod
    def get_req(cls, url, params=None, return_data=False, **kwargs):
        if params is None:
            params = {}
        response = requests.get(cls.__generate_url(url), params, **kwargs)
        return cls.__handle_request(response, return_data)

    @classmethod
    def post_req(cls, url, data=None, return_data=False, json="", **kwargs):
        if data is None:
            data = {}
        response = requests.post(cls.__generate_url(url), data, json, **kwargs)
        return cls.__handle_request(response, return_data)

    @classmethod
    def put_req(cls, url, data=None, return_data=False, json="", **kwargs):
        if data is None:
            data = {}
        response = requests.put(cls.__generate_url(url), data, json, **kwargs)
        return cls.__handle_request(response, return_data)

    @classmethod
    def del_req(cls, url, params=None, return_data=False, **kwargs):
        if params is None:
            params = {}
        response = requests.delete(cls.__generate_url(url), params=params, **kwargs)
        return cls.__handle_request(response, return_data)


class MetaApiViewClass(APIView, CustomResponse, CustomRequest, ResponseUtils):

    __auth_token_key = getenv("AUTH_TOKEN_KEY")

    token_info = None
    user = None

    @classmethod
    def get_params(cls, obj_to_check: dict, params_key: list, required=True):
        params = {}
        for p in params_key:
            params[p] = obj_to_check.get(p)
            if params[p] is None and required:
                raise cls.BadRequest([f'{p.upper()}_PARAMETER_IS_REQUIRED'])
        return params

    @classmethod
    def generic_decor(cls, protected=False):
        def decorator(func):
            def wrapper(*args, **kwargs):
                if protected:
                    request = args[1]
                    auth_token_key = cls.__auth_token_key
                    params_key = [auth_token_key]
                    params = cls.get_params(request.headers, params_key)

                    auth_response = cls.get_req(
                        '/find-user-by-token/', params=None, return_data=True,
                        headers={auth_token_key: params[auth_token_key]}
                    )

                    cls.token_info = auth_response['token_info']
                    cls.user = auth_response['user']

                    if cls.user is None:
                        return cls.not_found()

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
