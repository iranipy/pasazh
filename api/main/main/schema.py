schema = {
    'login': {
        'POST': {
            'type': 'object',
            'properties': {
                'mobile': {'type': 'string', 'pattern': r'^09\d{9}$'},
                'insert': {'type': 'boolean'},
            },
            'additionalProperties': False,
            'required': ['mobile'],
        },
    },
    'confirm-code': {
        'POST': {
            'type': 'object',
            'properties': {
                'mobile': {'type': 'string', 'pattern': r'^09\d{9}$'},
                'confirm_code': {'type': 'string', 'minLength': 1},
            },
            'additionalProperties': False,
            'required': ['mobile', 'confirm_code'],
        },
    },
    'update-profile': {
        'PUT': {
            'type': 'object',
            'properties': {
                'nick_name': {'type': 'string', 'minLength': 3, 'maxLength': 50},
                'email': {'type': 'string', 'format': 'email'},
                'picture': {'type': 'string'},
            },
            'additionalProperties': False,
            'required': ['nick_name'],
        },
    },
    'salesman-profile': {
        'POST': {
            'type': 'object',
            'properties': {
                'store_name': {'type': 'string', 'minLength': 5, 'maxLength': 50},
                'city_id': {'type': 'integer'},
                'job_category_id': {'type': 'integer'},
                'job_category_description': {'type:': 'string', 'minLength': 5, 'maxLength': 50},
                'address': {'type': 'string', 'minLength': 20, 'maxLength': 200},
                'open_time': {'type': 'string', 'format': 'date-time'},
                'close_time': {'type': 'string', 'format': 'date-time'},
                'working_days': {'type': 'string', 'minLength': 3, 'maxLength': 27},
                'activity_type': {'type': 'string', 'minLength': 2, 'maxLength': 3, 'enum': ['ON', 'OFF', 'ALL']},
                'is_private': {'type': 'boolean'},
                'username': {'type': 'string', 'minLength': 5, 'maxLength': 20},
                'full_name': {'type': 'string', 'minLength': 5, 'maxLength': 50},
                'telephone': {'type': 'string', 'minLength': 8, 'maxLength': 20},
            },
            'additionalProperties': False,
            'required': [
                'store_name', 'job_category_id', 'city_id', 'address',
                'open_time', 'close_time', 'activity_type', 'working_days'
            ],
        },
        'PUT': {
            'type': 'object',
            'properties': {
                'store_name': {'type': 'string', 'maxLength': 50},
                'job_category_id': {'type': 'integer'},
                'job_category_description': {'type:': 'string', 'maxLength': 50},
                'username': {'type': 'string', 'minLength': 5, 'maxLength': 20},
                'full_name': {'type': 'string', 'maxLength': 50},
                'telephone': {'type': 'string', 'maxLength': 20},
                'address': {'type': 'string', 'maxLength': 200},
                'city_id': {'type': 'integer'},
                'open_time': {'type': 'string', 'format': 'date-time'},
                'close_time': {'type': 'string', 'format': 'date-time'},
                'working_days': {'type': 'string', 'maxLength': 27},
                'activity_type': {'type': 'string', 'maxLength': 3, 'enum': ['ON', 'OFF', 'ALL']},
            },
            'additionalProperties': False,
        },
    },
    'follow-user': {
        'POST': {
            'type': 'object',
            'properties': {
                'followed_user_id': {'type': 'integer'},
            },
            'additionalProperties': False,
            'required': ['followed_user_id'],
        },
        'DELETE': {
            'type': 'object',
            'properties': {
                'followed_user_id': {'type': 'integer'},
            },
            'additionalProperties': False,
            'required': ['followed_user_id'],
        },
    },
    'follow-user': {
        'POST': {
            'type': 'object',
            'properties': {
                'banned_user_id': {'type': 'integer'},
            },
            'additionalProperties': False,
            'required': ['banned_user_id'],
        },
        'DELETE': {
            'type': 'object',
            'properties': {
                'banned_user_id': {'type': 'integer'},
            },
            'additionalProperties': False,
            'required': ['banned_user_id'],
        },
    },
    'category': {
        'POST': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string', 'minLength': 5, 'maxLength': 50},
                'parent_id': {'type': 'integer'},
            },
            'additionalProperties': False,
            'required': ['name'],
        },
        'PUT': {
            'type': 'object',
            'properties': {
                'category_id': {'type': 'integer'},
                'name': {'type': 'string', 'minLength': 5, 'maxLength': 50},
                'parent_id': {'type': 'integer'},
            },
            'additionalProperties': False,
            'required': ['category_id'],
        },
        'DELETE': {
            'type': 'object',
            'properties': {
                'category_id': {'type': 'integer'},
            },
            'additionalProperties': False,
            'required': ['category_id'],
        },
    },
    'product': {
        'GET': {
            'type': 'object',
            'properties': {
                'category_id': {'type': 'integer'},
            },
            'additionalProperties': False,
            'required': ['category_id'],
        },
        'POST': {
            'type': 'object',
            'properties': {
                'category_id': {'type': 'integer'},
                'name': {'type': 'string', 'minLength': 5, 'maxLength': 80},
                'quantity': {'type': 'integer', 'minLength': 1},
                'description': {'type': 'string', 'minLength': 5, 'maxLength': 1000},
                'price': {'type': 'integer', 'minimum': 0},
            },
            'additionalProperties': False,
            'required': ['category_id', 'name', 'quantity', 'description', 'price'],
        },
        'PUT': {
            'type': 'object',
            'properties': {
                'product_id': {'type': 'integer'},
                'name': {'type': 'string', 'minLength': 5, 'maxLength': 80},
                'quantity': {'type': 'integer', 'minLength': 1},
                'description': {'type': 'string', 'minLength': 5, 'maxLength': 1000},
                'price': {'type': 'integer', 'minimum': 0},
                'category_id': {'type': 'integer'},
            },
            'additionalProperties': False,
            'required': ['product_id'],
        },
        'DELETE': {
            'type': 'object',
            'properties': {
                'product_id': {'type': 'integer'},
            },
            'additionalProperties': False,
            'required': ['category_id'],
        },
    },
}
