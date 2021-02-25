schema = {
    'config': {
        'GET': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string', 'maxLength': 50},
            },
            'additionalProperties': False,
            'required': ['name'],
        },
        'PUT': {
            'type': 'object',
            'properties': {
                'user_id': {'type': 'integer'},
                'name': {'type': 'string', 'maxLength': 50},
                'is_active': {'type': 'boolean'},
                'value': {'type': 'string', 'maxLength': 200},
            },
            'additionalProperties': False,
            'required': ['user_id', 'name', 'is_active', 'value'],
        },
    },
}
