# Generated by Django 3.2.7 on 2021-10-07 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userpreferences', '0003_alter_userpreference_currency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpreference',
            name='currency',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
