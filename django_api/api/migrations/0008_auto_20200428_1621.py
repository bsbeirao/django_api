# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-04-28 19:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20190812_1142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='charges',
            name='status',
            field=models.BooleanField(verbose_name='STATUS'),
        ),
    ]
