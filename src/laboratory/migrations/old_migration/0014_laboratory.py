# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-12 22:42
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('laboratory', '0013_merge_20161212_1640'),
    ]

    operations = [
        migrations.CreateModel(
            name='Laboratory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Laboratory name')),
                ('rooms', models.ManyToManyField(blank=True, to='laboratory.LaboratoryRoom')),
            ],
            options={
                'verbose_name_plural': 'Laboratories',
                'verbose_name': 'Laboratory',
            },
        ),
    ]
