# Generated by Django 3.2.9 on 2022-01-07 01:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0008_auto_20220107_0050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messages',
            name='time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]