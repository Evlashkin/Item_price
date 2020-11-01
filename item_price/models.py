from django.db import models
from datetime import date


class Item(models.Model):
    name = models.CharField(max_length=200, verbose_name="Наименование")

    def __str__(self):
        return self.name


class ItemPrice(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name="Наименование")
    price = models.IntegerField(verbose_name="Цена")
    date_start = models.DateField(verbose_name="Дата с", blank=True, null=True)
    date_finish = models.DateField(verbose_name="Дата по", blank=True, null=True)
