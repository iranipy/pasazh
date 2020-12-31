import fastjsonschema
import json
from functools import wraps


class JsonValidation:

    VALIDATOR = {
        "find-user-by-mobile": {
            "GET": {
                "type": "object",
                "properties": {
                    "mobile": {"type": "string", "pattern": r"^09\d{9}$"},
                    "insert": {"type": "boolean"}
                },
                "additionalProperties": False,
                "required": ["mobile"]
            }
        },
        "create-otp": {
            "POST": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"},
                    "login_attempt_limit_hour": {"type": "integer", "minimum": 0},
                    "confirm_code_expire_minutes": {"type": "integer", "minimum": 1}
                },
                "additionalProperties": False,
                "required": ["user_id", "login_attempt_limit_hour", "confirm_code_expire_minutes"]
            }
        },
        "confirm-code": {
            "POST": {
                "type": "object",
                "properties": {
                    "confirm_code": {"type": "string", "minLength": 6, "maxLength": 6},
                    "user_id": {"type": "integer"},
                    "confirm_code_try_count_limit": {"type": "integer", "minimum": 1}
                },
                "additionalProperties": False,
                "required": ["confirm_code", "user_id", "confirm_code_try_count_limit"]
            }
        },
        "user-profile": {
            "PUT": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"},
                    "nick_name": {"minLength": 5, "maxLength": 50},
                    "email": {"type": "string", "format": "email"},
                    "picture": {"type": "string"}
                },
                "additionalProperties": False,
                "required": ["user_id"]
            }
        },
        "delete-account-by-id": {
            "DELETE": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"},
                },
                "additionalProperties": False,
                "required": ["user_id"]
            }
        },
        "salesman-profile": {
            'POST': {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"},
                    "store_name": {"type": "string", "minLength": 5, "maxLength": 50},
                    "city_id": {"type": "integer"},
                    "job_category_id": {"type": "integer"},
                    "job_category_description": {"type:": "string", "minLength": 5, "maxLength": 50},
                    "address": {"type": "string", "minLength": 20, "maxLength": 200},
                    "open_time": {"type": "string", "format": "date-time"},
                    "close_time": {"type": "string", "format": "date-time"},
                    "working_days": {"type": "string", "minLength": 3, "maxLength": 27},
                    "activity_type": {"type": "string", "minLength": 2, "maxLength": 3, "enum": ["ON", "OFF", "ALL"]},
                    "is_private": {"type": "boolean"},
                    "username": {"type": "string", "minLength": 5, "maxLength": 20},
                    "full_name": {"type": "string", "minLength": 5, "maxLength": 50},
                    "telephone": {"type": "string", "minLength": 8, "maxLength": 20},
                },
                "additionalProperties": False,
                "required": ["user_id", "store_name", "job_category_id", "city_id",
                             "address", "open_time", "close_time", "activity_type",
                             "working_days"]
            },
            "PUT": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"},
                    "store_name": {"type": "string", "maxLength": 50},
                    "job_category_id": {"type": "integer"},
                    "job_category_description": {"type:": "string", "maxLength": 50},
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
                "additionalProperties": False,
                "required": ["user_id"]
            }
        },
        "block-user": {
            "GET": {
                "properties": {
                    "user_id": {"type": "integer"},
                },
                "additionalProperties": False,
                "required": ["user_id"]
            },
            "POST": {
                "type": "object",
                "properties": {
                   "user_id": {"type": "integer"},
                   "banned_user_id": {"type": "integer"}
                },
                "additionalProperties": False,
                "required": ["user_id", "banned_user_id"]
            },
            "DELETE": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"},
                    "banned_user_id": {"type": "integer"}
                },
                "additionalProperties": False,
                "required": ["user_id", "banned_user_id"]
            }
        },
        "follow-user": {
            "GET": {
                "properties": {
                    "user_id": {"type": "integer"},
                },
                "additionalProperties": False,
                "required": ["user_id"]
            },
            "POST": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"},
                    "followed_user_id": {"type": "integer"}
                },
                "additionalProperties": False,
                "required": ["user_id", "followed_user_id"]
            },
            "DELETE": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"},
                    "followed_user_id": {"type": "integer"}
                },
                "additionalProperties": False,
                "required": ["user_id", "followed_user_id"]
            }
        }
    }

    @classmethod
    def find_schema(cls, url, method):
        url_validator = cls.VALIDATOR.get(url)
        if not url_validator:
            return
        return url_validator.get(method)

    @classmethod
    def validate(cls, f):
        wraps(f)

        def decorator(*args, **kwargs):
            request = args[1]
            obj_to_validate = None

            schema = cls.find_schema(request.path_info.replace('/', ''), request.method)
            if not schema:
                return f(*args, **kwargs)

            validate = fastjsonschema.compile(schema)

            if request.method in ["GET", "DELETE"]:
                obj_to_validate = dict()
                for key in request.query_params:
                    try:
                        obj_to_validate[key] = json.loads(request.query_params.get(key))
                    except json.JSONDecodeError:
                        obj_to_validate[key] = request.query_params.get(key)
            elif request.method in ["POST", "PUT"]:
                obj_to_validate = request.data

            if validate(obj_to_validate):
                pass

            return f(*args, **kwargs)

        return decorator
