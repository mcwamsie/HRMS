# Generated by Django 5.1.2 on 2024-10-26 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0050_surveyheading_alter_surveyfield_cssclass_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='surveyheading',
            options={'ordering': ['ordinal'], 'verbose_name': 'Survey Heading', 'verbose_name_plural': 'Survey Headings'},
        ),
        migrations.AddField(
            model_name='surveyheading',
            name='ordinal',
            field=models.IntegerField(default=1),
        ),
    ]
