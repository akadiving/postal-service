# Generated by Django 3.2.3 on 2021-06-27 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0006_alter_item_manifest_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='manifest',
            name='driver_name',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='manifest',
            name='driver_surname',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
