# Generated by Django 2.2.5 on 2019-11-20 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gis_app', '0016_auto_20191120_2041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicleexport',
            name='file_path',
            field=models.FilePathField(blank=True, match='.*\\.pdf$', max_length=255, path='/workspace/gis_project/gis_project/pdf_exports'),
        ),
    ]
