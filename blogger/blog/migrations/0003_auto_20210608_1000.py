# Generated by Django 3.2.3 on 2021-06-08 04:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20210607_1915'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blog',
            name='pic2',
        ),
        migrations.AlterField(
            model_name='blog',
            name='slug',
            field=models.SlugField(default='djangodbmodelsfieldscharfield'),
        ),
        migrations.AlterField(
            model_name='blogger',
            name='slug',
            field=models.SlugField(default='djangodbmodelsfieldsrelatedonetoonefield'),
        ),
        migrations.AlterField(
            model_name='categories',
            name='slug',
            field=models.SlugField(default='djangodbmodelsfieldscharfield'),
        ),
    ]