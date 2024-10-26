# Generated by Django 5.1.2 on 2024-10-24 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_assignment_day_after_notification_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='nationalIdNo',
            field=models.CharField(help_text='format:XX-XXXXXX-A-XX', max_length=150, unique=True, verbose_name='Nation ID Number'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='profilePhoto',
            field=models.ImageField(blank=True, null=True, upload_to='users/profile-photos', verbose_name='Profile Photo'),
        ),
    ]
