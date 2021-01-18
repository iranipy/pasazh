import json

from unidecode import unidecode
from django.http import QueryDict


def fix_dict_encode(obj=None, return_json=False):
    if obj is None:
        obj = {}

    for key, value in obj.items():
        val = value
        if isinstance(val, list) and len(val) > 0:
            val = val[0]

        if isinstance(val, str):
            val = val.strip()

            if val.isdigit():
                obj[key] = unidecode(val)
                continue

            try:
                obj[key] = json.loads(val)
            except json.JSONDecodeError:
                obj[key] = val

    if return_json:
        return json.dumps(obj, indent=2).encode('utf-8')

    return obj


class FixRequestParams:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        body = getattr(request, '_body', request.body)
        if body:
            request._body = fix_dict_encode(obj=json.loads(body), return_json=True)

        query_dict = QueryDict('', mutable=True)
        query_dict.update(fix_dict_encode(obj=dict(request.GET)))
        request.GET = query_dict

        return self.get_response(request)
