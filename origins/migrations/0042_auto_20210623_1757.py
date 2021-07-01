# Generated by Django 2.2.24 on 2021-06-23 17:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('origins', '0041_auto_20210605_1708'),
    ]

    operations = [
        migrations.AddField(
            model_name='nomen',
            name='is_objective_synonym',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='nomen',
            name='type_object',
            field=models.ForeignKey(blank=True, help_text='The type specimen fossil, select from choice list', null=True, on_delete=django.db.models.deletion.SET_NULL, to='origins.Fossil'),
        ),
        migrations.AlterField(
            model_name='nomen',
            name='type_specimen',
            field=models.CharField(blank=True, help_text='The catalog number of the type specimen entered as a string, e.g. OH 7', max_length=255, null=True),
        ),
    ]