# Generated by Django 5.0.6 on 2024-06-27 12:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0001_initial'),
        ('profile_app', '0002_remove_postcount_post_delete_post_delete_postcount'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='username',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='likepost',
            old_name='liker',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='post',
            old_name='username',
            new_name='user',
        ),
        migrations.AddField(
            model_name='post',
            name='profile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='profile_app.profile'),
        ),
        migrations.AlterUniqueTogether(
            name='likepost',
            unique_together={('post', 'user')},
        ),
    ]
