# Generated by Django 3.1.7 on 2022-02-07 18:41

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Structure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=255)),
                ('index', models.CharField(max_length=255)),
                ('url', models.CharField(max_length=255)),
                ('bulk_size_request', models.IntegerField(default=1000)),
                ('structure', models.JSONField(encoder=django.core.serializers.json.DjangoJSONEncoder)),
            ],
            options={
                'ordering': ['url', 'identifier'],
            },
        ),
    ]
