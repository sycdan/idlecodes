# Generated by Django 3.2.7 on 2021-09-26 01:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20210925_2143'),
    ]

    operations = [
        migrations.AddField(
            model_name='platform',
            name='instance_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
