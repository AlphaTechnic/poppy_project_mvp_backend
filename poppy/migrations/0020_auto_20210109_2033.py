# Generated by Django 3.0.8 on 2021-01-09 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poppy', '0019_auto_20210109_1942'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='application',
            name='pet_name',
        ),
        migrations.AlterField(
            model_name='application',
            name='pet_breed',
            field=models.CharField(max_length=100),
        ),
    ]
