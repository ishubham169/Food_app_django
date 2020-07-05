from rest_framework import serializers
from .models import Users, Restaurant


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Users
        fields = ('email_id', 'phone_number', 'user_type', 'updated_at', 'user_name', 'is_veg', 'restaurant_id')


class RestaurantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Restaurant
        fields = ('restaurant_name', 'restaurant_location')


def filter_restaurant_details(payload):
    return {key: value for key, value in payload.items() if key in RestaurantSerializer.Meta.fields}


def filter_user_details(payload):
    return {key: value for key, value in payload.items() if key in UserSerializer.Meta.fields}