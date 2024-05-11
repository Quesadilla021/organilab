# Generated by Django 4.1.10 on 2024-05-11 21:37

from django.db import migrations

def create_menu(apps, schema_editor):
    MenuItem = apps.get_model("djgentelella", "MenuItem")
    item = MenuItem.objects.create(
        parent = None,
        title = '',
        url_name ='auth_and_perms.djgentelellaimportorwidget.ImpostorWidget', #path to the widget file
        category = 'sidebarfooter', # the only place in which this widget can be place
        is_reversed = False,
        reversed_kwargs = None,
        reversed_args = None,
        is_widget = True, # must be set to true as exist other kind of element
        icon = 'fa fa-user-secret', # you can use fontawesome icons
        only_icon = True # this flag must be True
    )

class Migration(migrations.Migration):

    dependencies = [
        ('auth_and_perms', '0013_impostorlog'),
    ]

    operations = [
        migrations.RunPython(create_menu, reverse_code=migrations.RunPython.noop),
    ]
