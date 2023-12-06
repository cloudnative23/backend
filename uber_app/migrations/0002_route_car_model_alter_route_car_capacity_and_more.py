# Generated by Django 4.2.7 on 2023-12-05 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uber_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='route',
            name='Car_Model',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='route',
            name='Car_Capacity',
            field=models.IntegerField(default=''),
        ),
        migrations.AlterField(
            model_name='route',
            name='Car_Color',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='route',
            name='LicensePlateNumber',
            field=models.TextField(default=''),
        ),
    ]