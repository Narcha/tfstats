# Generated by Django 3.0.4 on 2020-04-28 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('steam_api', '0007_auto_20200424_2107'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='playtime_440_2weeks',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='player',
            name='playtime_440_total',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
