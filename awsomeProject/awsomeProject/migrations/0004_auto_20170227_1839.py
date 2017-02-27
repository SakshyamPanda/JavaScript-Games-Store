# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-27 16:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('awsomeProject', '0003_auto_20170224_1608'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='pid',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='transaction',
            name='status',
            field=models.CharField(choices=[('ongoing', 'ongoing'), ('completed', 'completed'), ('canceled', 'canceled')], default='ongoing', max_length=50),
        ),
    ]
