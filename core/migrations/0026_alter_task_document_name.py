# Generated by Django 5.1.2 on 2024-10-23 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_alter_assignment_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='document_name',
            field=models.FileField(blank=True, max_length=255, null=True, upload_to='tasks/documents'),
        ),
    ]
