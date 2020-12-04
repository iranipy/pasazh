from django.test import TestCase

# Create your tests here.
import jwt
import datetime
import time
class test:


    @staticmethod
    def jwt_token(**kwargs):
        secret = 'secret'
        kwargs['exp'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=2)
        return jwt.encode(kwargs, secret)

a = test.jwt_token(id='reza', h='reza3')
time.sleep(3)
print(jwt.decode(a, 'secret'))