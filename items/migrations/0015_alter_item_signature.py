# Generated by Django 3.2.3 on 2021-07-31 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0014_alter_item_delivered'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='signature',
            field=models.ImageField(blank=True, null=True, upload_to='signatures/'),
        ),
    ]
