# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-11 05:20
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('laboratory', '0005_auto_20160907_1509'),
    ]

    operations = [
        migrations.AddField(
            model_name='shelf',
            name='name',
            field=models.CharField(default='nd', max_length=15),
        ),
    ]
