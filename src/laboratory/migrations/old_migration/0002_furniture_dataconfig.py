# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-08 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('laboratory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='furniture',
            name='dataconfig',
            field=models.TextField(default='', verbose_name='Data configuration'),
            preserve_default=False,
        ),
    ]
