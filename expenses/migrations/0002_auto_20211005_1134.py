# Generated by Django 3.2.7 on 2021-10-05 11:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterField(
            model_name='expense',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
