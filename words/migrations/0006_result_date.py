# Generated by Django 4.0.5 on 2022-07-10 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('words', '0005_alter_result_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]