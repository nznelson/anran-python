# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Move',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField()),
                ('taken', models.IntegerField()),
                ('game', models.ForeignKey(to='server.Game')),
            ],
        ),
        migrations.CreateModel(
            name='Pile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField()),
                ('count', models.IntegerField()),
                ('game', models.ForeignKey(to='server.Game')),
            ],
        ),
        migrations.AddField(
            model_name='move',
            name='pile',
            field=models.ForeignKey(to='server.Pile'),
        ),
    ]
