# Generated by Django 2.2.10 on 2020-11-18 20:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import mediautils.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentSection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.TextField(blank=True, null=True)),
                ('comments_enabled', models.BooleanField(default=True)),
                ('owner_can_delete', models.BooleanField(default=False)),
                ('anyone_can_reply', models.BooleanField(default=True)),
                ('is_flat', models.BooleanField(default=True)),
                ('count_replies', models.PositiveIntegerField(default=0)),
                ('count_likes', models.PositiveIntegerField(default=0)),
                ('count_dislikes', models.PositiveIntegerField(default=0)),
                ('cached_featured', models.TextField(blank=True, default='')),
            ],
        ),
        migrations.CreateModel(
            name='SocialProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nick', models.CharField(blank=True, max_length=64, null=True)),
                ('phrase', models.CharField(blank=True, max_length=256, null=True)),
                ('date_time', models.DateTimeField(default=django.utils.timezone.localtime)),
                ('ip', models.CharField(blank=True, max_length=46, null=True)),
                ('comment_section', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sprofile_comment_section', to='social_layer.CommentSection')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SocialProfilePhoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media_file', models.FileField(max_length=10485760, upload_to=mediautils.models.choose_upload_media_to)),
                ('media_thumbnail', models.FileField(blank=True, max_length=10485760, null=True, upload_to=mediautils.models.choose_upload_media_thumb_to)),
                ('content_type', models.CharField(blank=True, max_length=127, null=True)),
                ('orientation', models.CharField(default='portrait', max_length=10)),
                ('format_tries', models.IntegerField(default=0)),
                ('formated', models.BooleanField(default=False)),
                ('md5_hash', models.CharField(blank=True, max_length=32, null=True)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social_layer.SocialProfile')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('date_time', models.DateTimeField(default=django.utils.timezone.localtime)),
                ('read', models.BooleanField(default=False)),
                ('to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notification_to', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='commentsection',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_section_owner', to='social_layer.SocialProfile'),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('date_time', models.DateTimeField(default=django.utils.timezone.localtime)),
                ('count_replies', models.PositiveIntegerField(default=0)),
                ('count_likes', models.PositiveIntegerField(default=0)),
                ('count_dislikes', models.PositiveIntegerField(default=0)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_author', to='social_layer.SocialProfile')),
                ('comment_section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_section', to='social_layer.CommentSection')),
                ('reply_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment_reply_to', to='social_layer.Comment')),
            ],
            options={
                'ordering': ['-date_time'],
            },
        ),
    ]