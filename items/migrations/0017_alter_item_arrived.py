# Generated by Django 3.2.3 on 2021-09-19 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0016_alter_item_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='arrived',
            field=models.BooleanField(default=False, null=True),
        ),
    ]