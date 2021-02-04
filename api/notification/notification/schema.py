schema = {
    'mail/send-mail/': {
        'POST': {
            'type': 'object',
            'properties': {
                'recipient': {'type': 'string', 'format': 'email', 'minLength': 5, 'maxLength': 100},
                'subject': {'type': 'string', 'minLength': 5, 'maxLength': 100},
                'message': {'type': 'string', 'minLength': 5, 'maxLength': 1000},
            },
            'additionalProperties': False,
            'required': ['recipient', 'subject', 'message'],
        },
    },
    'sms/send-sms/': {
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
    'mail/send-mass-mail/': {
        'POST': {
            'type': 'object',
            'properties': {
                'recipients': {
                    'type': 'array', 'items': {'type': 'string', 'format': 'email'},
                    'minItems': 2, 'uniqueItems': True
                },
                'subject': {'type': 'string', 'minLength': 5, 'maxLength': 100},
                'message': {'type': 'string', 'minLength': 5, 'maxLength': 1000},
            },
            'additionalProperties': False,
            'required': ['recipients', 'subject', 'message'],
        },
    },
}
