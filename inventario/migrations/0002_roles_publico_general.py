from django.db import migrations


def crear_roles_y_publico(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Cliente = apps.get_model('inventario', 'Cliente')

    for nombre in ('Administrador', 'Almacenista', 'Cajero'):
        Group.objects.get_or_create(name=nombre)
    Cliente.objects.get_or_create(nombre='Público general')


def eliminar_roles_y_publico(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Cliente = apps.get_model('inventario', 'Cliente')
    Group.objects.filter(name__in=('Administrador', 'Almacenista', 'Cajero')).delete()
    Cliente.objects.filter(nombre='Público general').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('inventario', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(crear_roles_y_publico, eliminar_roles_y_publico),
    ]
