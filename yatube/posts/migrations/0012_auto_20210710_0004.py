# Generated by Django 2.2.6 on 2021-07-09 21:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_auto_20210709_1644'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='pub_date',
            new_name='created',
        ),
    ]
