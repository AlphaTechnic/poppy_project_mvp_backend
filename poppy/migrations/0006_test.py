# Generated by Django 3.0.8 on 2021-01-15 02:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poppy', '0005_auto_20210114_2225'),
    ]

    operations = [
        migrations.CreateModel(
            name='test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('testfield', models.CharField(max_length=200)),
                ('photo', models.FileField(upload_to='')),
            ],
        ),
    ]
