# Generated by Django 4.1 on 2022-08-10 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0005_button_phrases_buttons'),
    ]

    operations = [
        migrations.AddField(
            model_name='button',
            name='related_phrases',
            field=models.ManyToManyField(blank=True, to='messenger.phrases'),
        ),
    ]
