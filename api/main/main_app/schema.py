import fastjsonschema
from functools import wraps


class JsonValidation:
    VALIDATOR = {
        "login": {
            "type": "object",
            "properties": {
                "mobile": {"type": "string", "maxLength": 10},
            },
            "additionalProperties": False,
            "required": ["mobile"]
        },
        "confirm-code": {
            "type": "object",
            "properties": {
                "mobile": {"type": "string", "maxLength": 10},
                "confirm_code": {"type": "string", "maxLength": 6},
            },
            "additionalProperties": False,
            "required": ["mobile"]
        },
        "update-profile": {
            "type": "object",
            "properties": {
                "nick_name": {"type": "string", "minLength": 1, "maxLength": 50},
                "email": {"type": "integer", "format": "email"},
                "picture": {"type": "string"}
            },
            "additionalProperties": False
        },
        "create-salesman": {
            "type": "object",
            "properties": {
                "store_name": {"type": "string", "maxLength": 50},
                "city_id": {"type": "integer"},
                "job_category_id": {"type": "integer"},
                "address": {"type": "string", "maxLength": 200},
                "open_time": {"type": "string", "format": "date-time"},
                "close_time": {"type": "string", "format": "date-time"},
                "working_days": {"type": "string", "maxLength": 27},
                "activity_type": {"type": "string", "maxLength": 3, "enum": ["ON", "OFF", "ALL"]},
                "is_private": {"type": "boolean"},
                "username": {"type": "string", "minLength": 5, "maxLength": 20},
                "full_name": {"type": "string", "maxLength": 50},
                "telephone": {"type": "string", "maxLength": 20},
            },
            "additionalProperties": False,
            "required": ["city_id", "address", "open_time", "close_time", "activity_type"]
        },
        "update-sales-man": {
            "type": "object",
            "properties": {
                "store_name": {"type": "string", "maxLength": 50},
                "username": {"type": "string", "minLength": 5, "maxLength": 20},
                "full_name": {"type": "string", "maxLength": 50},
                "telephone": {"type": "string", "maxLength": 20},
                "address": {"type": "string", "maxLength": 200},
                "city_id": {"type": "integer"},
                "open_time": {"type": "string", "format": "date-time"},
                "close_time": {"type": "string", "format": "date-time"},
                "working_days": {"type": "string", "maxLength": 27},
                "activity_type": {"type": "string", "maxLength": 3, "enum": ["ON", "OFF", "ALL"]},
            },
            "additionalProperties": False
        }

    }

    @classmethod
    def proper_schema(cls, url):
        return cls.VALIDATOR.get(url)

    @classmethod
    def validate(cls, f):
        wraps(f)

        def decorator(*args, **kwargs):
            request = args[1]
            schema = cls.proper_schema(request.path_info.replace('/', ''))
            validate = fastjsonschema.compile(schema)
            if validate(request.data):
                pass
            return f(*args, **kwargs)

        return decorator
