# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-05-08 18:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_auto_20200430_1608'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='call',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bill_call', to='api.Call', unique=True),
        ),
    ]