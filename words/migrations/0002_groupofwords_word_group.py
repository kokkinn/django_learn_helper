# Generated by Django 4.0.5 on 2022-06-24 11:01

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('words', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupOfWords',
            fields=[
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=200)),
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='word',
            name='group',
            field=models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='words', to='words.groupofwords'),
        ),
    ]
