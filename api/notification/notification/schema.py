schema = {
    'send-mail': {
        'POST': {
            'type': 'object',
            'properties': {
                'recipient': {'type': 'string', 'minLength': 5, 'maxLength': 100},
                'subject': {'type': 'string', 'minLength': 5, 'maxLength': 100},
                'message': {'type': 'string', 'minLength': 5, 'maxLength': 1000},
            },
            'additionalProperties': False,
            'required': ['to', 'subject', 'body'],
        },
    },
    'send-sms': {
        'POST': {
            'type': 'object',
            'properties': {
                'receptor': {'type': 'string', 'pattern': r'^09\d{9}$'},
                'message': {'type': 'string', 'minLength': 5, 'maxLength': 200},
            },
            'additionalProperties': False,
            'required': ['receptor', 'message'],
        },
    },
}
