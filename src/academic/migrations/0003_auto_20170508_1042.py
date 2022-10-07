# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-08 16:42
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('academic', '0002_auto_20170505_0050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='procedure',
            name='description',
            field=models.TextField(verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='procedure',
            name='title',
            field=models.CharField(max_length=500, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='procedureobservations',
            name='description',
            field=models.TextField(verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='procedurerequiredobject',
            name='object',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='laboratory.Object', verbose_name='Object'),
        ),
        migrations.AlterField(
            model_name='procedurestep',
            name='description',
            field=models.TextField(null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='procedurestep',
            name='title',
            field=models.CharField(max_length=500, null=True, verbose_name='Title'),
        ),
    ]
