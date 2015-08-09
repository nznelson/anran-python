# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0003_auto_20150808_2136'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pile',
            old_name='count',
            new_name='amount',
        ),
    ]
