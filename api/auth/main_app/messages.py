from rest_framework import status

class Messages:
    SUCCESS = [
        {'message': 'OK'},
        status.HTTP_200_OK
    ]

    BAD_REQUEST = [
        {'message': 'NO_VALID_DATA'},
        status.HTTP_400_BAD_REQUEST
    ]

    NOT_FOUND = [
        {'message': 'NOT_FOUND'},
        status.HTTP_404_NOT_FOUND
    ]

    SYSTEM_ERROR = [
        {'message': 'SYSTEM_ERROR'},
        {
            500: status.HTTP_500_INTERNAL_SERVER_ERROR,
            501: status.HTTP_501_NOT_IMPLEMENTED,
            502: status.HTTP_502_BAD_GATEWAY,
            503: status.HTTP_503_SERVICE_UNAVAILABLE,
            504: status.HTTP_504_GATEWAY_TIMEOUT,
            505: status.HTTP_505_HTTP_VERSION_NOT_SUPPORTED,
            506: status.HTTP_506_VARIANT_ALSO_NEGOTIATES,
            507: status.HTTP_507_INSUFFICIENT_STORAGE,
            508: status.HTTP_508_LOOP_DETECTED,
            509: status.HTTP_509_BANDWIDTH_LIMIT_EXCEEDED

        }

    ]

    @classmethod
    def sys_error(cls, code):
        try:
            return cls.SYSTEM_ERROR[1][code]
        except KeyError:
            return cls.SYSTEM_ERROR[1][500]
