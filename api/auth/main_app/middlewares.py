import json

from unidecode import unidecode
from django.http import QueryDict


def fix_dict_encode(obj=None, return_json=False):
    if obj is None:
        obj = {}

    for key, value in obj.items():
        if isinstance(value, str) and value.isdigit():
            obj[key] = unidecode(value.strip())

    if return_json:
        return json.dumps(obj, indent=2).encode('utf-8')

    return obj


class FixRequestParams:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        body = getattr(request, '_body', request.body)
        request._body = fix_dict_encode(obj=json.loads(body), return_json=True)
        request.GET = QueryDict(fix_dict_encode(obj=dict(request.GET)))

        return self.get_response(request)
