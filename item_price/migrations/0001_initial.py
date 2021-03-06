# Generated by Django 3.1.2 on 2020-10-23 21:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Наименование')),
                ('price', models.IntegerField(verbose_name='Цена')),
                ('date_start', models.DateField(default=datetime.date.today, verbose_name='Дата с')),
                ('date_finish', models.DateField(blank=True, verbose_name='Дата по')),
            ],
        ),
    ]
