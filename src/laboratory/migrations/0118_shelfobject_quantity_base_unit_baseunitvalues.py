# Generated by Django 4.1.9 on 2023-06-21 15:21

from django.db import migrations, models
import django.db.models.deletion
import laboratory.catalog


class Migration(migrations.Migration):

    dependencies = [
        ('laboratory', '0117_alter_shelfobject_container'),
    ]

    operations = [
        migrations.AddField(
            model_name='shelfobject',
            name='quantity_base_unit',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.CreateModel(
            name='BaseUnitValues',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('si_value', models.FloatField(default=1, null=True)),
                ('measurement_unit', laboratory.catalog.GTForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='baseunit', to='laboratory.catalog', verbose_name='Base unit')),
            ],
        ),
    ]