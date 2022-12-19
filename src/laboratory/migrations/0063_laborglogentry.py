# Generated by Django 4.0.8 on 2022-12-12 21:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('admin', '0003_logentry_add_action_flag_choices'),
        ('laboratory', '0062_remove_organizationusermanagement_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='LabOrgLogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('log_entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin.logentry', verbose_name='Log Entry')),
            ],
        ),
    ]