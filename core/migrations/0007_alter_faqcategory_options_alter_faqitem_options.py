# Generated by Django 5.1.2 on 2024-10-29 20:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_faqcategory_options_alter_faqitem_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='faqcategory',
            options={'verbose_name': 'FAQ Category', 'verbose_name_plural': 'FAQ Categories'},
        ),
        migrations.AlterModelOptions(
            name='faqitem',
            options={'verbose_name': 'FAQ Item', 'verbose_name_plural': 'FAQ Items'},
        ),
    ]
