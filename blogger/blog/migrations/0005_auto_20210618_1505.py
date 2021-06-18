# Generated by Django 3.2.3 on 2021-06-18 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20210617_1756'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blog',
            old_name='pic1',
            new_name='photo',
        ),
        migrations.AlterField(
            model_name='blogger',
            name='is_blogger',
            field=models.BooleanField(default=False, help_text='Designates whether this user should be treated as blogger on site.a blogger can create new blogs, view them and comment on them'),
        ),
        migrations.AlterField(
            model_name='blogger',
            name='is_staff',
            field=models.BooleanField(default=False, help_text="Designates whether this user should be treated as site staff.a staff user can add categories and update other user's status "),
        ),
        migrations.AlterField(
            model_name='blogger',
            name='is_viewer',
            field=models.BooleanField(default=True, help_text='Designates whether this user should be treated as viewer site.a viewer can view blogs and comment on it'),
        ),
    ]
