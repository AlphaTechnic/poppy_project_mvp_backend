# Generated by Django 3.0.8 on 2021-01-09 11:21

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poppy', '0004_auto_20210109_1059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fee',
            name='small',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(default=[1, 2]), size=2),
        ),
    ]
