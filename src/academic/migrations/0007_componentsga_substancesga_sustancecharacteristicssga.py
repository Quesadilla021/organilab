# Generated by Django 3.2 on 2022-09-01 15:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import laboratory.catalog
import tagging.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sga', '0011_auto_20220901_0957'),
        ('laboratory', '0045_alter_sustancecharacteristics_bioaccumulable'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('academic', '0006_auto_20200525_1916'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComponentSGA',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, verbose_name='Name')),
                ('cas_number', models.CharField(max_length=150, verbose_name='CAS number')),
            ],
            options={
                'verbose_name': 'ComponentSGA',
                'verbose_name_plural': 'ComponentsSGA',
            },
        ),
        migrations.CreateModel(
            name='SubstanceSGA',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comercial_name', models.CharField(max_length=250, verbose_name='Comercial name')),
                ('synonymous', tagging.fields.TagField(blank=True, max_length=255, verbose_name='Synonymous')),
                ('uipa_name', models.CharField(blank=True, max_length=250, verbose_name='UIPA name')),
                ('agrochemical', models.BooleanField(default=False, verbose_name='Agrochemical')),
                ('is_public', models.BooleanField(default=True, verbose_name='Share with others')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('is_approved', models.BooleanField(blank=True, default=False)),
                ('components', models.ManyToManyField(to='academic.ComponentSGA', verbose_name='Components')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'SustanceSGA',
                'verbose_name_plural': 'SustancesSGA',
            },
        ),
        migrations.CreateModel(
            name='SustanceCharacteristicsSGA',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bioaccumulable', models.BooleanField(null=True)),
                ('molecular_formula', models.CharField(blank=True, max_length=255, null=True, verbose_name='Molecular formula')),
                ('cas_id_number', models.CharField(blank=True, max_length=255, null=True, verbose_name='Cas ID Number')),
                ('security_sheet', models.FileField(blank=True, null=True, upload_to='security_sheets/', verbose_name='Security sheet')),
                ('is_precursor', models.BooleanField(default=False, verbose_name='Is precursor')),
                ('valid_molecular_formula', models.BooleanField(default=False)),
                ('seveso_list', models.BooleanField(default=False, verbose_name='Is Seveso list III?')),
                ('h_code', models.ManyToManyField(blank=True, to='sga.DangerIndication', verbose_name='Danger Indication')),
                ('iarc', laboratory.catalog.GTForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='gt_iarcrelsga', to='laboratory.catalog')),
                ('imdg', laboratory.catalog.GTForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='gt_imdgsga', to='laboratory.catalog')),
                ('nfpa', laboratory.catalog.GTManyToManyField(blank=True, related_name='gt_nfpasga', to='laboratory.Catalog', verbose_name='NFPA codes')),
                ('precursor_type', laboratory.catalog.GTForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='gt_precursorsga', to='laboratory.catalog')),
                ('storage_class', laboratory.catalog.GTManyToManyField(blank=True, related_name='gt_storage_classsga', to='laboratory.Catalog', verbose_name='Storage class')),
                ('substance', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='academic.substancesga')),
                ('ue_code', laboratory.catalog.GTManyToManyField(blank=True, related_name='gt_uesga', to='laboratory.Catalog', verbose_name='UE codes')),
                ('white_organ', laboratory.catalog.GTManyToManyField(blank=True, related_name='gt_white_organsga', to='laboratory.Catalog')),
            ],
            options={
                'verbose_name': 'Sustance characteristicSGA',
                'verbose_name_plural': 'Sustance characteristicsSGA',
            },
        ),
    ]