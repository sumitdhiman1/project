# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-14 04:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pluto', '0002_auto_20170813_0427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermodel',
            name='password',
            field=models.CharField(max_length=40),
        ),
    ]
