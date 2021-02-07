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
    'sms/send-mass-sms/': {
        'POST': {
            'type': 'object',
            'properties': {
                'recipients': {
                    'type': 'array', 'items': {'type': 'string', 'pattern': '#phoneNumRe'},  # replace
                    'minItems': 2, 'uniqueItems': True
                },
                'sender': {'type': 'array', 'items': {'type': 'integer', 'minItems': 2}},
                'message': {'type': 'string', 'minLength': 5, 'maxLength': 1000},
            },
            'additionalProperties': False,
            'required': ['recipients', 'sender', 'message'],
        },
    },
    'sms/sms-status/': {
        'GET': {
            'type': 'object',
            'properties': {
                'messageid': {'type': 'integer'},
                'localid': {'type': 'integer'}
            },
            'additionalProperties': False,
            'required': ['messageid']
        },
    },
    'sms/select-sms/': {
        'GET': {
            'type': 'object',
            'properties': {
                'messageid': {'type': 'integer'},
                'page_size': {'type': 'integer'},
                'sender': {'type': 'integer'}
            },
            'additionalProperties': False,
            'required': ['page_size'],
        },
    },
    'sms/cancel-sms/': {
        'DELETE': {
            'type': 'object',
            'properties': {
                'messageid': {'type': 'integer'},
            },
            'additionalProperties': False,
            'required': ['messageid'],
        },
    },
    'sms/select-outbox/': {
        'GET': {
            'type': 'object',
            'properties': {
                'startdate': {'type': '#UnixTime'},  # replace
                'enddate': {'type': '#UnixTime'},  # replace
                'sender': {'type': 'integer'},
            },
            'additionalProperties': False,
            'required': ['startdate'],
        },
    },
    'sms/count-outbox/': {
        'GET': {
            'type': 'object',
            'properties': {
                'startdate': {'type': '#UnixTime'},  # replace
                'enddate': {'type': '#UnixTime'},  # replace
                'sender': {'type': 'integer'},
            },
            'additionalProperties': False,
            'required': ['startdate'],
        },
    },
    'sms/count-inbox/': {
        'GET': {
            'type': 'object',
            'properties': {
                'startdate': {'type': '#UnixTime'},  # replace
                'enddate': {'type': '#UnixTime'},  # replace
                'linenumber': {'type': 'integer'},
                'isread': {'type': 'number', 'minimum': 0, 'maximum': 1}
            },
            'additionalProperties': False,
            'required': ['startdate'],
        },
    },
    'sms/read-inbox/': {
        'GET': {
            'type': 'object',
            'properties': {
                'linenumber': {'type': 'integer'},
                'isread': {'type': 'number', 'minimum': 0, 'maximum': 1}
            },
            'additionalProperties': False,
            'required': ['linenumber', 'isread'],
        },
    },
}
