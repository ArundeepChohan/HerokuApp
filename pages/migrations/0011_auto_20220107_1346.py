# Generated by Django 3.2.9 on 2022-01-07 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0010_messages_read'),
    ]

    operations = [
        migrations.AddField(
            model_name='messages',
            name='subject',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='messages',
            name='text',
            field=models.CharField(default='', max_length=4096),
        ),
    ]
