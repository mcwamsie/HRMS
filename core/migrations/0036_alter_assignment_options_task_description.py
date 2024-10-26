# Generated by Django 5.1.2 on 2024-10-24 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_alter_employee_nationalidno_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assignment',
            options={'ordering': ['-status', 'due_date'], 'verbose_name': 'Assignment', 'verbose_name_plural': 'Assignments'},
        ),
        migrations.AddField(
            model_name='task',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Task Description'),
        ),
    ]
