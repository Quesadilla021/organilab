# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-12 19:20
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('laboratory', '0011_auto_20161212_0945'),
    ]

    operations = [
        migrations.AddField(
            model_name='shelfobject',
            name='limit_quantity',
            field=models.FloatField(default=0.0, verbose_name='Limit material quantity'),
            preserve_default=False,
        ),
    ]
