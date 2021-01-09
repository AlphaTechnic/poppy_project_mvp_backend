# Generated by Django 3.0.8 on 2021-01-09 11:41

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poppy', '0006_auto_20210109_1129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fee',
            name='large',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=[], size=2),
        ),
        migrations.AlterField(
            model_name='fee',
            name='middle',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=[], size=2),
        ),
        migrations.AlterField(
            model_name='fee',
            name='small',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=[], size=2),
        ),
    ]
