# schema = {
#     'mail/send-mail/': {
#         'POST': {
#             'type': 'object',
#             'properties': {
#                 'recipient': {'type': 'string', 'format': 'email', 'minLength': 5, 'maxLength': 100},
#                 'subject': {'type': 'string', 'minLength': 5, 'maxLength': 100},
#                 'message': {'type': 'string', 'minLength': 5, 'maxLength': 1000},
#             },
#             'additionalProperties': False,
#             'required': ['recipient', 'subject', 'message'],
#         },
#     },
#

schema = {
    'config-retrieve': {
        'GET': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string', 'maxLength': 50}
            },
            'additionalProperties': False,
            'required': ['name']
        },
        'PUT': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string', 'maxLength': 50},
                'is_active': {'type': 'boolean'},
                'value': {'type': 'string', 'maxLength': 200},
            },
            'additionalProperties': False,
            'required': ['name', 'is_active', 'value']
        }
    }
}
