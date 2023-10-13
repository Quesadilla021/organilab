# Generated by Django 4.1.11 on 2023-10-04 20:06

from django.db import migrations

def set_is_container_in_materials(apps, schema_editor):
    Object = apps.get_model('laboratory', 'Object')
    Object.objects.filter(type=1).update(is_container=True)

class Migration(migrations.Migration):

    dependencies = [
        ('laboratory', '0130_object_is_container'),
    ]

    operations = [
        migrations.RunPython(set_is_container_in_materials,
                             reverse_code=migrations.RunPython.noop),

    ]