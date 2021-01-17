from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as stat


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


class MetaApiViewClass(APIView, CustomResponse):

    @classmethod
    def generic_decor(cls, func):
        def inner(*args, **kwargs):
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
