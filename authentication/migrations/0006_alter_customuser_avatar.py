# Generated by Django 5.0.6 on 2024-07-14 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0005_alter_customuser_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='avatar',
            field=models.ImageField(blank=True, default='images/avatar.jpeg', null=True, upload_to='images/'),
        ),
    ]
