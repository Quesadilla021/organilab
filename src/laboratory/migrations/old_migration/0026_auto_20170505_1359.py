# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-05 19:59
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('laboratory', '0025_clinventory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clinventory',
            name='cas_id_number',
            field=models.CharField(max_length=512, verbose_name='CAS ID number'),
        ),
        migrations.AlterField(
            model_name='clinventory',
            name='name',
            field=models.CharField(max_length=512, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='clinventory',
            name='url',
            field=models.URLField(max_length=512),
        ),
    ]
