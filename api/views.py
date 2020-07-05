from .models import Users, Restaurant, Food, Orders
from .serializers import filter_user_details, filter_restaurant_details
from rest_framework.decorators import api_view
import json
import datetime
from.utils import UserType, password_hash, generate_auth_token, decorate_response, query
from .constant import UserAuthKey, RestaurantAuthKey
from django.db import connection

with open('./config.json') as config_file:
    config = json.load(config_file)


@api_view(['POST'])
@decorate_response
def sign_up(request):
    payload = request.data
    user_type = payload['user_type']
    email = payload['email_id']
    is_user_exist = Users.objects.filter(email_id=email)
    restaurant_details = {}
    if is_user_exist:
        raise Exception("User already exist with this email")
    if user_type == UserType.Restaurant.value:
        restaurant_details = filter_restaurant_details(payload)
        restaurant_obj = Restaurant(**restaurant_details)
        restaurant_obj.save()
        payload['restaurant_id'] = restaurant_obj
    password = payload.pop('password')
    user_details = filter_user_details(payload)
    user_details['password_hash'] = password_hash(password)
    user_details['updated_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if 'restaurant_id' in payload:
        payload.pop('restaurant_id')
    user_obj = Users(**user_details)
    user_obj.save()
    user_details.update(restaurant_details)
    if user_type == UserType.Restaurant.value:
        user_auth = {key: value for key, value in user_details.items() if key in (RestaurantAuthKey.keys)}
    else:
        user_auth = {key: value for key, value in user_details.items() if key in (UserAuthKey.keys)}
    auth_token_payload = filter_auth_token_fields(user_auth)
    auth_token = generate_auth_token(auth_token_payload)
    return {"auth_token": auth_token}


@api_view(['POST'])
@decorate_response
def login(request):
    payload = request.data
    email = payload['email_id']
    password = password_hash(payload['password'])
    user_type = payload['user_type']
    user = Users.objects.filter(email_id=email, password_hash=password, user_type=user_type)
    if user:
        user = list(user)[0]
        restaurant = {}
        current_time = (datetime.datetime.now() - datetime.timedelta(minutes=config['SESSION_LOGOUT_MINUTES'])).strftime("%Y-%m-%d %H:%M:%S")
        user_obj = Users.objects.get(id=user.id)
        last_login = user_obj.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        is_logout = is_login_timeout(last_login, current_time)
        if is_logout:
            user_obj.updated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_obj.save()

        user_dict = user_obj.__dict__
        if user_dict['user_type'] == '1':
            restaurant_details = Restaurant.objects.get(id=user.restaurant_id.id)
            restaurant = restaurant_details.__dict__
        user_dict.update(restaurant)
        user_dict['updated_at'] = last_login
        if user_type == UserType.Restaurant.value:
            user_auth = {key: value for key, value in user_dict.items() if key in (RestaurantAuthKey.keys)}
        else:
            user_auth = {key: value for key, value in user_dict.items() if key in (UserAuthKey.keys)}
        auth_token_payload = filter_auth_token_fields(user_auth)
        auth_token = generate_auth_token(auth_token_payload)
        return {"auth_token": auth_token}
    raise Exception("Invalid username or password")


@api_view(['POST'])
@decorate_response
def add_item(request):
    payload = request.data
    email = payload.pop('email_id')
    user = Users.objects.filter(email_id=email, user_type=UserType.Restaurant.value)
    if user:
        user = list(user)[0]
        restaurant_obj = Restaurant.objects.filter(id=user.restaurant_id.id)
        payload['restaurant_id'] = restaurant_obj[0]
        food_obj = Food(**payload)
        food_obj.save()
        food_details = food_obj.__dict__
        return {"food_details": {"food_name": food_details['food_name'], "food_type": food_details['food_type']}}
    raise Exception("Unauthorised")


@api_view(['GET'])
@decorate_response
def menu(request):
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    restaurant_data = {}

    for row in rows:
        key = row[0] + '_' + row[1] + '_' + str(row[4])
        if key in restaurant_data:
            restaurant_data[key].append([row[2], row[3], row[5]])
        else:
            restaurant_data[key] = [[row[2], row[3], row[5]]]
    restaurants = []
    for key, value in restaurant_data.items():
        temp = key.split('_')
        res_name, res_loc, res_id = temp[0], temp[1], temp[2]
        res = {"restaurant_name": res_name, "restaurant_location": res_loc, "restaurant_id": res_id}
        food_items = []
        for food in value:
            temp = {"food_name": food[0], "food_type": food[1], "food_id": food[2]}
            food_items.append(temp)
        res["food_items"] = food_items
        restaurants.append(res)
    return {"restaurants": restaurants}


@api_view(['POST'])
@decorate_response
def place_order(request):
    payload = request.data
    restaurant_id = payload['restaurant_id']
    email = payload['email']
    food_items = payload['food_items']
    user = Users.objects.get(email_id=email)
    restaurant = Restaurant.objects.get(id=restaurant_id)
    food_list = []
    for food_item in food_items:
        food = Food.objects.get(id=food_item['food_id'])
        food_list.append(food)
    food_details = []
    for food in food_list:
        food_details.append({"food_name": food.food_name, "food_type": food.food_type})
    order_details = {"order_details": food_details}
    order_obj = Orders(user_id=user, restaurant_id=restaurant, order_details=json.dumps(order_details))
    order_obj.save()
    return order_details


@api_view(['GET'])
@decorate_response
def order_history(request):
    email = request.GET['email_id']
    user = Users.objects.filter(email_id=email)[0]
    orders = Orders.objects.filter(restaurant_id=user.restaurant_id_id)
    order_history = []
    if orders:
        for order in orders:
            customer = Users.objects.get(id=order.user_id_id)
            customer_details = {"username": customer.user_name, "email": customer.email_id, "phone_number": customer.phone_number}
            if type(order.order_details) != dict:
                order_details = json.loads(order.order_details)
            else:
                food_details = order.order_details
            order_history.append({"customer_details": customer_details, "food_details": food_details})
    return {"order_history": order_history}


def filter_auth_token_fields(payload):
    return {key: value for key,value in payload.items() if key not in ['password_hash', 'created_at']}


def is_login_timeout(last_login_time, current_time):
    return current_time > last_login_time
