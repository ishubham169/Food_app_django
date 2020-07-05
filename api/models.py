from django.db import models
from django.core.validators import MinLengthValidator
from .utils import UserType
import jsonfield


class Restaurant(models.Model):
    restaurant_name = models.CharField(validators=[MinLengthValidator(5)], max_length=30)
    restaurant_location = models.CharField(validators=[MinLengthValidator(5)], max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)


class Users(models.Model):
    user_name = models.CharField(max_length=20)
    email_id = models.CharField(max_length=50)
    phone_number = models.CharField(validators=[MinLengthValidator(10)], max_length=10)
    password_hash = models.CharField(max_length=200)
    user_type = models.CharField(
        max_length=1,
        choices=UserType.choices(),
        default=UserType.Customer,
    )

    restaurant_id = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True)
    is_veg = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Food(models.Model):
    food_name = models.CharField(max_length=100)
    restaurant_id = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True)
    food_type = models.CharField(max_length=10)


class Orders(models.Model):
    restaurant_id = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE, null=True)
    order_details = jsonfield.JSONField()
    created = models.DateTimeField(auto_now_add=True)