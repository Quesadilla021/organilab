# Generated by Django 2.2.12 on 2020-05-26 01:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_auto_20180630_1835'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='feedbackentry',
            options={'verbose_name': 'Feedback entry', 'verbose_name_plural': 'Feedback entries'},
        ),
    ]
