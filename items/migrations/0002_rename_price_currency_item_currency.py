# Generated by Django 3.2.3 on 2021-06-11 03:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item',
            old_name='price_currency',
            new_name='currency',
        ),
    ]
