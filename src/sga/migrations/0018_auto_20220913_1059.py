# Generated by Django 3.2 on 2022-09-13 16:59

from django.db import migrations, models
import django.db.models.deletion
import laboratory.catalog


class Migration(migrations.Migration):

    dependencies = [
        ('laboratory', '0045_alter_sustancecharacteristics_bioaccumulable'),
        ('sga', '0017_auto_20220912_1144'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubstanceCharacteristics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bioaccumulable', models.BooleanField(null=True)),
                ('molecular_formula', models.CharField(blank=True, max_length=255, null=True, verbose_name='Molecular formula')),
                ('cas_id_number', models.CharField(blank=True, max_length=255, null=True, verbose_name='Cas ID Number')),
                ('security_sheet', models.FileField(blank=True, null=True, upload_to='security_sheets/', verbose_name='Security sheet')),
                ('is_precursor', models.BooleanField(default=False, verbose_name='Is precursor')),
                ('valid_molecular_formula', models.BooleanField(default=False)),
                ('seveso_list', models.BooleanField(default=False, verbose_name='Is Seveso list III?')),
                ('h_code', models.ManyToManyField(blank=True, related_name='sga_h_code', to='sga.DangerIndication', verbose_name='Danger Indication')),
                ('iarc', laboratory.catalog.GTForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='gt_iarcrel_sga', to='laboratory.catalog')),
                ('imdg', laboratory.catalog.GTForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='gt_imdg_sga', to='laboratory.catalog')),
                ('nfpa', laboratory.catalog.GTManyToManyField(blank=True, related_name='gt_nfpa_sga', to='laboratory.Catalog', verbose_name='NFPA codes')),
                ('precursor_type', laboratory.catalog.GTForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='gt_precursor_sga', to='laboratory.catalog')),
                ('storage_class', laboratory.catalog.GTManyToManyField(blank=True, related_name='gt_storage_class_sga', to='laboratory.Catalog', verbose_name='Storage class')),
            ],
            options={
                'verbose_name': 'Substance characteristic SGA',
                'verbose_name_plural': 'Substance characteristics SGA',
            },
        ),
        migrations.AlterModelOptions(
            name='substance',
            options={'verbose_name': 'Substance', 'verbose_name_plural': 'Substances'},
        ),
        migrations.RemoveField(
            model_name='label',
            name='sustance',
        ),
        migrations.AddField(
            model_name='label',
            name='substance',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sga.substance', verbose_name='Substance'),
        ),
        migrations.DeleteModel(
            name='SustanceCharacteristics',
        ),
        migrations.AddField(
            model_name='substancecharacteristics',
            name='substance',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='sga.substance'),
        ),
        migrations.AddField(
            model_name='substancecharacteristics',
            name='ue_code',
            field=laboratory.catalog.GTManyToManyField(blank=True, related_name='gt_ue_sga', to='laboratory.Catalog', verbose_name='UE codes'),
        ),
        migrations.AddField(
            model_name='substancecharacteristics',
            name='white_organ',
            field=laboratory.catalog.GTManyToManyField(blank=True, related_name='gt_white_organ_sga', to='laboratory.Catalog'),
        ),
    ]