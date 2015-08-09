# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('server', '0002_move_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='players',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='move',
            name='date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
