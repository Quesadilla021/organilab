# Generated by Django 4.1.13 on 2024-09-16 09:41

from django.db import migrations
import django.db.models.deletion
import laboratory.catalog


class Migration(migrations.Migration):

    dependencies = [
        ('laboratory', '0141_alter_precursorreportvalues_bills_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='baseunitvalues',
            name='measurement_unit_base',
            field=laboratory.catalog.GTForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='baseunit', to='laboratory.catalog', verbose_name='Base unit'),
        ),
        migrations.AlterField(
            model_name='baseunitvalues',
            name='measurement_unit',
            field=laboratory.catalog.GTOneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='unit', to='laboratory.catalog', verbose_name='Unit'),
        ),
    ]
