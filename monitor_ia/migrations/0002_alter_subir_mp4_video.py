# Generated by Django 5.2.3 on 2025-06-19 04:04

import monitor_ia.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor_ia', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subir_mp4',
            name='video',
            field=models.FileField(blank=True, null=True, storage=monitor_ia.models.ProfilePictureStorage, upload_to='videos/'),
        ),
    ]
