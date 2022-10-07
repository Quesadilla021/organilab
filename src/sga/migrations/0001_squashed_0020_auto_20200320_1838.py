# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-03-25 07:48

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields
import tagging.fields


# Functions from the following migrations need manual copying.
# Move them and any dependencies into this file, then update the
# RunPython operations to refer to the local versions:
# sga.migrations.0002_pictograms
from ._migration_creation_objects import create_pictograms


class Migration(migrations.Migration):

    replaces = [('sga', '0001_initial'), ('sga', '0002_pictograms'), ('sga', '0003_auto_20180822_0934'), ('sga', '0004_dangerindication_prudence_advice'), ('sga', '0005_auto_20180822_1048'), ('sga', '0006_auto_20180822_1718'), ('sga', '0007_auto_20180822_2007'), ('sga', '0008_auto_20180822_2026'), ('sga', '0009_auto_20180822_2152'), ('sga', '0010_auto_20180822_2319'), ('sga', '0011_dangerindication_warning_category'), ('sga', '0012_auto_20180823_2215'), ('sga', '0013_auto_20180827_1138'), ('sga', '0014_sustance_agrochemical'), ('sga', '0015_auto_20180914_1449'), ('sga', '0016_auto_20181223_2325'), ('sga', '0017_templatesga'), ('sga', '0018_auto_20190423_1611'), ('sga', '0019_auto_20200118_0034'), ('sga', '0020_auto_20200320_1838')]

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BuilderInformation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('phone', models.TextField(max_length=15)),
                ('address', models.TextField(max_length=100)),
            ],
            options={
                'verbose_name_plural': 'Information of Builders',
                'permissions': (('view_builderinformation', 'Can see available Builder Information'),),
                'verbose_name': 'Builder Information',
            },
        ),
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
            ],
            options={
                'verbose_name_plural': 'Components',
                'permissions': (('view_component', 'Can see available Component'),),
                'verbose_name': 'Component',
            },
        ),
        migrations.CreateModel(
            name='DangerIndication',
            fields=[
                ('code', models.CharField(max_length=150, primary_key=True, serialize=False)),
                ('description', models.TextField()),
            ],
            options={
                'verbose_name_plural': 'Indication of Danger',
                'permissions': (('view_dangerindication', 'Can see available indication of danger'),),
                'verbose_name': 'Danger Indication',
            },
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.SmallIntegerField(choices=[(0, 'default')])),
                ('builderInformation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sga.BuilderInformation')),
            ],
            options={
                'verbose_name_plural': 'Labels',
                'permissions': (('view_label', 'Can see available labels'),),
                'verbose_name': 'Label',
            },
        ),
        migrations.CreateModel(
            name='Pictogram',
            fields=[
                ('name', models.CharField(max_length=150, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name_plural': 'Pictograms',
                'permissions': (('view_pictogram', 'Can see available pictograms'),),
                'verbose_name': 'Pictogram',
            },
        ),
        migrations.CreateModel(
            name='Substance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comercial_name', models.CharField(max_length=250)),
                ('cas_number', models.CharField(max_length=150)),
                ('components', models.ManyToManyField(to='sga.Component')),
                ('danger_indications', models.ManyToManyField(to='sga.DangerIndication')),
            ],
            options={
                'verbose_name_plural': 'Substances',
                'permissions': (('view_substance', 'Can see available Sustance'),),
                'verbose_name': 'Substance',
            },
        ),
        migrations.CreateModel(
            name='WarningClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('category', models.SmallIntegerField(choices=[(0, 'Physic warning'), (1, 'Healty warning'), (2, 'Environment warning')])),
            ],
            options={
                'verbose_name_plural': 'Warning Classes',
                'permissions': (('view_warningclass', 'Can see available Warning Classes'),),
                'verbose_name': 'Warning Class',
            },
        ),
        migrations.CreateModel(
            name='WarningWord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('weigth', models.SmallIntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'Warning Words',
                'permissions': (('view_warningword', 'Can see available Warning Words'),),
                'verbose_name': 'Warning Word',
            },
        ),
        migrations.AddField(
            model_name='label',
            name='sustance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sga.Substance'),
        ),
        migrations.AddField(
            model_name='dangerindication',
            name='pictograms',
            field=models.ManyToManyField(to='sga.Pictogram'),
        ),
        migrations.AddField(
            model_name='dangerindication',
            name='warning_class',
            field=models.ManyToManyField(to='sga.WarningClass'),
        ),
        migrations.AddField(
            model_name='dangerindication',
            name='warning_words',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sga.WarningWord'),
        ),
        migrations.RemoveField(
            model_name='substance',
            name='cas_number',
        ),
        migrations.RemoveField(
            model_name='warningclass',
            name='category',
        ),
        migrations.AddField(
            model_name='component',
            name='cas_number',
            field=models.CharField(default='0000', max_length=150, verbose_name='CAS number'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='substance',
            name='synonymous',
            field=tagging.fields.TagField(blank=True, max_length=255, verbose_name='Synonymous'),
        ),
        migrations.AlterField(
            model_name='builderinformation',
            name='address',
            field=models.TextField(max_length=100, verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='builderinformation',
            name='name',
            field=models.CharField(max_length=150, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='builderinformation',
            name='phone',
            field=models.TextField(max_length=15, verbose_name='Phone'),
        ),
        migrations.AlterField(
            model_name='component',
            name='name',
            field=models.CharField(max_length=250, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='dangerindication',
            name='code',
            field=models.CharField(max_length=150, primary_key=True, serialize=False, verbose_name='Code'),
        ),
        migrations.AlterField(
            model_name='dangerindication',
            name='description',
            field=models.TextField(verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='dangerindication',
            name='pictograms',
            field=models.ManyToManyField(to='sga.Pictogram', verbose_name='Pictograms'),
        ),
        migrations.AlterField(
            model_name='dangerindication',
            name='warning_class',
            field=models.ManyToManyField(to='sga.WarningClass', verbose_name='Warning class'),
        ),
        migrations.AlterField(
            model_name='dangerindication',
            name='warning_words',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sga.WarningWord', verbose_name='Warning words'),
        ),
        migrations.AlterField(
            model_name='label',
            name='builderInformation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sga.BuilderInformation', verbose_name='Builder Information'),
        ),
        migrations.AlterField(
            model_name='label',
            name='size',
            field=models.SmallIntegerField(choices=[(0, 'default')], verbose_name='Size'),
        ),
        migrations.AlterField(
            model_name='label',
            name='sustance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sga.Substance', verbose_name='Substance'),
        ),
        migrations.AlterField(
            model_name='pictogram',
            name='name',
            field=models.CharField(max_length=150, primary_key=True, serialize=False, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='substance',
            name='comercial_name',
            field=models.CharField(max_length=250, verbose_name='Comercial name'),
        ),
        migrations.AlterField(
            model_name='substance',
            name='components',
            field=models.ManyToManyField(to='sga.Component', verbose_name='Components'),
        ),
        migrations.AlterField(
            model_name='substance',
            name='danger_indications',
            field=models.ManyToManyField(to='sga.DangerIndication', verbose_name='Danger indications'),
        ),
        migrations.AlterField(
            model_name='warningclass',
            name='name',
            field=models.CharField(max_length=150, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='warningword',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='warningword',
            name='weigth',
            field=models.SmallIntegerField(default=0, verbose_name='Weigth'),
        ),
        migrations.AddField(
            model_name='warningclass',
            name='level',
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AddField(
            model_name='warningclass',
            name='lft',
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AddField(
            model_name='warningclass',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='sga.WarningClass'),
        ),
        migrations.AddField(
            model_name='warningclass',
            name='rght',
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AddField(
            model_name='warningclass',
            name='tree_id',
            field=models.PositiveIntegerField(db_index=True, default=1, editable=False),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='PrudenceAdvice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500, verbose_name='Name')),
                ('code', models.CharField(default='', max_length=150, verbose_name='Code')),
                ('prudence_advice_help', models.TextField(blank=True, null=True, verbose_name='Help for prudence advice')),
            ],
            options={
                'permissions': (('view_prudenceadvice', 'Can see available prudence advice'),),
                'verbose_name': 'Prudence Advice',
                'verbose_name_plural': 'Prudence Advices',
            },
        ),
        migrations.AlterField(
            model_name='dangerindication',
            name='warning_words',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='sga.WarningWord', verbose_name='Warning words'),
        ),
        migrations.AddField(
            model_name='dangerindication',
            name='prudence_advice',
            field=models.ManyToManyField(to='sga.PrudenceAdvice', verbose_name='Prudence advice'),
        ),
        migrations.AddField(
            model_name='warningclass',
            name='danger_type',
            field=models.CharField(choices=[('typeofdanger', 'Type of danger'), ('class', 'Danger class'), ('category', 'Danger Category')], default='category', max_length=25, verbose_name='Danger type'),
        ),
        migrations.CreateModel(
            name='RecipientSize',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Name')),
                ('height', models.FloatField(default=10, verbose_name='Height')),
                ('height_unit', models.CharField(choices=[('mm', 'Milimeters'), ('cm', 'Centimeters'), ('inch', 'inch')], default='cm', max_length=5, verbose_name='Height Unit')),
                ('width', models.FloatField(default=10, verbose_name='Width')),
                ('width_unit', models.CharField(choices=[('mm', 'Milimeters'), ('cm', 'Centimeters'), ('inch', 'inch')], default='cm', max_length=5, verbose_name='Width Unit')),
            ],
            options={
                'verbose_name': 'Recipient Size',
                'permissions': (('view_recipientsize', 'Can see available Recipient Size'),),
                'verbose_name_plural': 'Size of recipients',
            },
        ),
        migrations.AddField(
            model_name='label',
            name='commercial_information',
            field=models.TextField(blank=True, null=True, verbose_name='Commercial Information'),
        ),
        migrations.AlterField(
            model_name='label',
            name='size',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sga.RecipientSize', verbose_name='Recipient Size'),
        ),
        migrations.AddField(
            model_name='dangerindication',
            name='warning_category',
            field=models.ManyToManyField(related_name='warningcategory', to='sga.WarningClass', verbose_name='Warning category'),
        ),
        migrations.AddField(
            model_name='substance',
            name='agrochemical',
            field=models.BooleanField(default=False, verbose_name='Agrochemical'),
        ),

        migrations.CreateModel(
            name='TemplateSGA',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Name')),
                ('json_representation', models.TextField()),
                ('community_share', models.BooleanField(default=True, verbose_name='Share with community')),
                ('preview', models.TextField(help_text='B64 preview image')),
                ('recipient_size', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sga.RecipientSize', verbose_name='Recipient Size')),
            ],
            options={
                'permissions': (('view_label', 'Can see available labels'),),
                'verbose_name': 'Template SGA',
                'verbose_name_plural': 'Templates SGA',
            },
        ),
        migrations.AddField(
            model_name='pictogram',
            name='warning_word',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='sga.WarningWord'),
            preserve_default=False,
        ),
        migrations.RunPython(create_pictograms ),
    ]
