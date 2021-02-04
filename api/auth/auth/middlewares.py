import json

from unidecode import unidecode
from django.http import QueryDict
from django.urls import reverse


def is_value_sequence(item_val):
    return isinstance(item_val, list) or isinstance(item_val, tuple)


def fix_str_val(val):
    fixed_val = val

    if fixed_val.isdigit():
        fixed_val = unidecode(fixed_val)

    try:
        fixed_val = json.loads(fixed_val)
    except json.JSONDecodeError:
        pass

    return fixed_val


def fix_list_val(sequence):
    return [
        s if not isinstance(s, str) else fix_str_val(s) for s in sequence
    ]


def fix_dict_encode(obj=None, return_json=False, no_list_in_data=False):
    if obj is None:
        obj = {}

    for key, value in obj.items():
        if no_list_in_data and is_value_sequence(value) and len(value) > 0:
            value = value[0]

        if isinstance(value, str):
            obj[key] = fix_str_val(value.strip())
        elif is_value_sequence(value) and len(value) > 0:
            obj[key] = fix_list_val(value)
        else:
            obj[key] = value

    if return_json:
        return json.dumps(obj, indent=2).encode('utf-8')

    return obj


class FixRequestParams:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        if request.path.startswith(reverse('admin:index')):
            return None

        body = getattr(request, '_body', request.body)
        if body:
            request._body = fix_dict_encode(obj=json.loads(body), return_json=True)

        query_dict = QueryDict('', mutable=True)
        query_dict.update(fix_dict_encode(obj=dict(request.GET), no_list_in_data=True))
        request.GET = query_dict

        return self.get_response(request)
