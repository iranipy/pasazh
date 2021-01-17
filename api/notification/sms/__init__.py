import kavenegar

from os import getenv
APIKEY = getenv('API_KEY')

api = kavenegar.KavenegarAPI(apikey=APIKEY)
