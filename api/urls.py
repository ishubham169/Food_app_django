from django.urls import path
from .views import sign_up, login, add_item, menu, place_order, order_history


urlpatterns = [
    path('sign_up/', sign_up),
    path('login/', login),
    path('add/item/', add_item),
    path('menu/', menu),
    path('place/order/', place_order),
    path('order/history/', order_history)
]
