# Generated by Django 5.1.2 on 2024-10-22 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_position_keywords'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='keywords',
            field=models.TextField(blank=True, null=True),
        ),
    ]
