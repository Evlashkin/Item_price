"""
Необходимо реализовать 2 REST контроллера.
1. Контроллер продукта. Содержит 3 метода:
    • Создание продукта (название и цена);
    • Удаление продукта (по идентификатору);
    • Получение списка всех продуктов с ценами на определённую дату.
2. Контроллер цен на продукты. Содержит один метод:
    • Установка цены на продукт (принимает идентификатор продукта, цену и период действия цены)
Продукт может иметь разную цену в разные промежутки времени. Например, с 01.01.2019 по 31.01.2019 цена 15у.е.,
с 01.02.2019 по 28.02.2019 цена 17у.е., а с 01.03.2018 по настоящее время цена 19у.е.

При получении списка продуктов с ценами, можно указать на какую дату мы хотим получить цены.
Если не указываем, дата считается сегодняшней.

При назначении цены можно указать открытый сверху или снизу интервал.

Можно указать цену за период, который пересекает или находится внутри существующего (указанного ранее) периода.
В таком случае новый период должен сдвинуть старый или разбить его на части.
"""

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from datetime import date, timedelta, datetime
import json

from item_price.models import Item, ItemPrice
from item_price.my_functions import add_price_function


@csrf_exempt
def create_delete_show(request):
    # Создание продукта
    if request.method == 'POST':
        body = request.body
        params = json.loads(body)
        create_item = ItemPrice.objects.create(item=Item.objects.create(name=params['name']), price=params['price'])
        item = Item.objects.get(name=params['name'])
        return HttpResponse("Продукт '%s' успешно создан" % item)

    # Удаление продукта
    elif request.method == 'DELETE':
        body = request.body
        params = json.loads(body)
        item = Item.objects.get(pk=params['pk'])
        item.delete()
        return HttpResponse("Продукт '%s' успешно удален" % item)

    # Просмотр всех продуктов и цен на текущую дата
    else:
        params = request.GET
        print(len(params))
        if len(params) != 0:
            print(params)
            all_items = ItemPrice.objects.filter((Q(date_start__lte=params['date']) | Q(date_start=None)) &
                                                 (Q(date_finish__gte=params['date']) | Q(date_finish=None)))
            my_items = []
            for item in all_items:
                my_items.append(item.item.name)
            return HttpResponse(', '.join(set(my_items)))
        else:
            all_items = ItemPrice.objects.filter((Q(date_start__lte=date.today()) | Q(date_start=None)) &
                                                 (Q(date_finish__gte=date.today()) | Q(date_finish=None)))
            my_items = []
            for item in all_items:
                my_items.append(item.item.name)
            return HttpResponse(', '.join(set(my_items)))


@csrf_exempt
def add_price(request):
    if request.method == "POST":
        body = request.body
        params = json.loads(body)
        all_items = ItemPrice.objects.filter(item=Item.objects.get(pk=params['pk']))
        my_list = all_items.order_by('date_finish')
        if 'date_finish' in params and 'date_start' in params:
            new_price = add_price_function(item=Item.objects.get(pk=params['pk']), price=params['price'],
                                           date_start=params['date_start'], date_finish=params['date_finish'])
        elif 'date_start' in params:
            new_price = add_price_function(item=Item.objects.get(pk=params['pk']), price=params['price'],
                                           date_start=params['date_start'])
        elif 'date_finish' in params:
            new_price = add_price_function(item=Item.objects.get(pk=params['pk']), price=params['price'],
                                           date_finish=params['date_finish'])
        else:
            new_price = add_price_function(item=Item.objects.get(pk=params['pk']), price=params['price'])
        product = Item.objects.get(pk=params['pk'])

        new_s, new_f = (None, None)
        # Новая дата начала действия цены
        if new_price.date_start:
            new_s = datetime.strptime(new_price.date_start, "%Y-%m-%d").date()
        # Новая дата окончания действия цены
        if new_price.date_finish:
            new_f = datetime.strptime(new_price.date_finish, "%Y-%m-%d").date()

        print(new_s, new_f)

        if new_s is None or new_f is None or new_s <= new_f:

            for i in my_list:
                # Старая дата начала действия цены
                old_s = i.date_start
                # Старая дата окончания действия цены
                old_f = i.date_finish
                print(old_s, old_f)

                # 1 Интервал начинается в существующем, а заканчивается позже
                if old_f is not None and new_s is not None and (old_s is None or new_s > old_s) and (new_f is None or
                                                                                                     new_f >= old_f):
                    print("Пришел в 1")
                    item = ItemPrice.objects.get(item=Item.objects.get(pk=params['pk']), date_start=old_s,
                                                 date_finish=old_f)
                    item.date_finish = new_s - timedelta(days=1)
                    item.save()
                    new_price.save()
                    # return HttpResponse('Добавлена новая цена и период ее действия для продукта "%s". <br/> '
                    #                     'Окончание действия цены в предыдущем интервале изменено.' % product)

                # 2 Интервал начинается раньше, а заканчивается в существующем
                elif old_s is not None and (new_s is None or new_s <= old_s) and new_f is not None and (old_f is None or
                                                                                                        new_f < old_f):
                    print("Пришел в 2")
                    item = ItemPrice.objects.get(item=Item.objects.get(pk=params['pk']), date_start=old_s,
                                                 date_finish=old_f)
                    item.date_start = new_f + timedelta(days=1)
                    item.save()
                    new_price.save()
                    # return HttpResponse('Добавлена новая цена и период ее действия для продукта "%s". <br/> '
                    #                     'Начало действия цены в предыдущем интервале изменено.' % product)

                # 3 Интервал поглащает существующий
                elif (new_s is None or (old_s is not None and new_s <= old_s)) \
                        and (new_f is None or (old_f is not None and new_f >= old_f)):
                    print('Пришел в 3')
                    qs_item = ItemPrice.objects.filter(item=Item.objects.get(pk=params['pk']), date_start=old_s,
                                                       date_finish=old_f)
                    for item in qs_item:
                        if item.pk != new_price.pk:
                            item.delete()
                            print('удачно удален')
                    new_price.save()

                # 4 Интервал входит в существующий
                elif old_s is None or old_f is None or new_s is not None and new_f is not None and new_s > old_s and new_f < old_f:
                    print('Пришел в 4')
                    item = ItemPrice.objects.get(item=Item.objects.get(pk=params['pk']), date_start=old_s,
                                                 date_finish=old_f)
                    item.date_finish = new_s - timedelta(days=1)
                    item.save()
                    new_date_start = new_f + timedelta(days=1)
                    new = ItemPrice.objects.create(item=Item.objects.get(pk=params['pk']), price=item.price,
                                                   date_start=new_date_start, date_finish=old_f)
                    new.save()
                    new_price.save()
                else:
                    print('я тут 5 (else)')
        else:
            return HttpResponse('Дата окончания действия цены не может быть меньше даты начала')
    return HttpResponse('Добавлена новая цена и период ее действия для продукта "%s"' % product)
