# Generated by Django 2.2.13 on 2020-07-13 00:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('standard', '0009_auto_20200707_1649'),
    ]

    operations = [
        migrations.AddField(
            model_name='termsindexpage',
            name='subtitle',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]