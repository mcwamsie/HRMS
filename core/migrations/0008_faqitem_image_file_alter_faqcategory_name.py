# Generated by Django 5.1.2 on 2024-10-29 20:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_faqcategory_options_alter_faqitem_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='faqitem',
            name='image_file',
            field=models.FileField(blank=True, null=True, upload_to='faq/images/', validators=[django.core.validators.FileExtensionValidator(['mp4', 'avi', 'mkv'])], verbose_name='Image File'),
        ),
        migrations.AlterField(
            model_name='faqcategory',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
