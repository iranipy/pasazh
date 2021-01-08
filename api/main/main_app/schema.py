import fastjsonschema
import json

from functools import wraps


class JsonValidation:
    VALIDATOR = {
        "login": {
            "POST": {
                "type": "object",
                "properties": {
                    "mobile": {"type": "string", "pattern": r"^09\d{9}$"},
                    "insert": {"type": "boolean"}
                },
                "additionalProperties": False,
                "required": ["mobile"]
            }
        },
        "confirm-code": {
            "POST": {
                "type": "object",
                "properties": {
                    "mobile": {"type": "string", "pattern": r"^09\d{9}$"},
                    "confirm_code": {"type": "string", "minLength": 6, "maxLength": 6},
                },
                "additionalProperties": False,
                "required": ["mobile", "confirm_code"]
            }
        },
        "update-profile": {
            "PUT": {
                "type": "object",
                "properties": {
                    "nick_name": {"type": "string", "minLength": 5, "maxLength": 50},
                    "email": {"type": "string", "format": "email"},
                    "picture": {"type": "string"}
                },
                "additionalProperties": False
            }
        },
        "salesman-profile": {
            'POST': {
                "type": "object",
                "properties": {
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
                "required": ["store_name", "job_category_id", "city_id", "address",
                             "open_time", "close_time", "activity_type", "working_days"]
            },
            "PUT": {
                "type": "object",
                "properties": {
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
                "additionalProperties": False
            }
        },
        "category": {
            "GET": {
                "type": "object",
                "properties": {
                    "category_id": {"type": "integer"}
                },
                "additionalProperties": False,
                "required": ["category_id"]
            },
            "POST": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "minLength": 5, "maxLength": 50},
                    "is_public": {"type": "boolean"}
                },
                "additionalProperties": False,
                "required": ["name"]
            },
            "PUT": {
                "type": "object",
                "properties": {
                    "category_id": {"type": "integer"},
                    "name": {"type": "string", "minLength": 5, "maxLength": 50},
                    "is_public": {"type": "boolean"}
                },
                "additionalProperties": False,
                "required": ["category_id"]
            },
            "DELETE": {
                "type": "object",
                "properties": {
                    "category_id": {"type": "integer"}
                },
                "additionalProperties": False,
                "required": ["category_id"]
            }

        },
        "product": {
            "GET": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer"}
                },
                "additionalProperties": False,
                "required": ["category_id"]
            },
            "POST": {
                "type": "object",
                "properties": {
                    "category_id": {"type": "integer"},
                    "name": {"type": "string", "minLength": 5, "maxLength": 80},
                    "quantity": {"type": "integer", "minLength": 1},
                    "description": {"type": "string", "minLength": 5, "maxLength": 1000},
                    "price": {"type": "integer", "minimum": 0},
                },
                "additionalProperties": False,
                "required": ["category_id", "name", "quantity", "description", "price"]
            },
            "PUT": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer"},
                    "name": {"type": "string", "minLength": 5, "maxLength": 80},
                    "quantity": {"type": "integer", "minLength": 1},
                    "description": {"type": "string", "minLength": 5, "maxLength": 1000},
                    "price": {"type": "integer", "minimum": 0},
                    "category_id": {"type": "integer"}
                },
                "additionalProperties": False,
                "required": ["product_id"]
            },
            "DELETE": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer"}
                },
                "additionalProperties": False,
                "required": ["category_id"]
            },
        },
        "follow-user": {
            "GET": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"}
                },
                "additionalProperties": False,
                "required": ["user_id"]
            },
            "POST": {
                "type": "object",
                "properties": {
                    "followed_user_id": {"type": "integer"}
                },
                "additionalProperties": False,
                "required": ["followed_user_id"]
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
            obj_to_validate = request.data

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

            validate(obj_to_validate)

            return f(*args, **kwargs)

        return decorator
