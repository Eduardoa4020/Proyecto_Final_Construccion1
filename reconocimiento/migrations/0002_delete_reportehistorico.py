from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reconocimiento', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ReporteHistorico',
        ),
    ]