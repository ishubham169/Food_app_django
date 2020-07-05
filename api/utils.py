from enum import Enum
import base64
import hashlib, binascii
import json
from rest_framework.response import Response
from rest_framework import status
from collections import OrderedDict

with open('./config.json') as config_file:
    config = json.load(config_file)

query = 'select res.restaurant_name as restaurant_name, res.restaurant_location as restaurant_location, foo.food_name' \
        ' as food_name, foo.food_type as food_type , res.id as restaurant_id , foo.id as food_id from api_food foo, ' \
        'api_restaurant res where foo.restaurant_id_id = res.id ;'

class UserType(Enum):
    Customer = '0'
    Restaurant = '1'

    @classmethod
    def choices(cls):
        return [(k.value, k.name) for k in cls]


def generate_auth_token(user_details):
    user_details_dict = OrderedDict(sorted(user_details.items()))
    unique_key = json.dumps(user_details_dict)
    encode = base64.b64encode(unique_key.encode('UTF-8'))
    return encode


def password_hash(password):
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), config['HASH_KEY'].encode(), 100000)
    return binascii.hexlify(dk)


def decorate_response(func):
    def wrapper(*args, **kwargs):
        try:
            data = func(*args, **kwargs)
            return Response({"is_success": True, "data": data})
        except Exception as e:
            return Response({"is_success": False, "data": {}, "error": str(e)},status=status.HTTP_400_BAD_REQUEST)
    return wrapper




