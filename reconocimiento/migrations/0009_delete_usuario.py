# Generated by Django 5.2.3 on 2025-06-26 14:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reconocimiento', '0008_usuario_usuario_padre_alter_usuario_rol'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Usuario',
        ),
    ]
