import secrets
from types import FunctionType
from main_app.messages import Messages
from rest_framework.response import Response


def hex_generator():
    return secrets.token_hex(4)


# class MetaClass(type):
#     def __new__(cls, name, bases, dct: dict):
#         for key, value in dct.items():
#             if isinstance(value, FunctionType):
#                 dct[key] = staticmethod(value)
#         return super().__new__(cls, name, bases, dct)


class CustomResponse:
    def bad_request(self):
        return Response(Messages.BAD_REQUEST[0], status=Messages.BAD_REQUEST[1])

    def not_found(self):
        return Response(Messages.NOT_FOUND[0], status=Messages.NOT_FOUND[1])

    def success(self, **kwargs):

        for key, value in kwargs.items():
            if key == 'message':
                raise KeyError
            Messages.SUCCESS[0][key] = value
        return Response(Messages.SUCCESS[0], status=Messages.SUCCESS[1])

    def system_error(self, code=None):
        if not code:
            return Response(Messages.SYSTEM_ERROR[0], Messages.sys_error(500))

        return Response(Messages.SYSTEM_ERROR[0], status=Messages.sys_error(code))
    @staticmethod
    def reset_message():
        Messages.SUCCESS[0] = {'message': 'OK'}






