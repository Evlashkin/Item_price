from django.urls import path

from item_price.views import *

urlpatterns = [
    path('', create_delete_show),
    path('add/', add_price)
]
