# Generated by Django 5.1.2 on 2024-10-26 22:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_department_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='code',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]