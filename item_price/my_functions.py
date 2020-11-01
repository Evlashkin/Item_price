from item_price.models import *


def add_price_function(item, price, date_start=None, date_finish=None):
    new_price = ItemPrice(item=item, price=price, date_start=date_start, date_finish=date_finish)
    new_price.save()
    return new_price
