# Generated by Django 3.2.10 on 2021-12-22 14:08

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import social_layer.mediautils.models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("social_layer", "0003_likecomment"),
    ]

    operations = [
        migrations.CreateModel(
            name="Post",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.TextField(blank=True, null=True)),
                (
                    "date_time",
                    models.DateTimeField(default=django.utils.timezone.localtime),
                ),
            ],
        ),
        migrations.AlterField(
            model_name="commentsection",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="comment_section_owner",
                to="social_layer.socialprofile",
            ),
        ),
        migrations.AlterField(
            model_name="likecomment",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="likecomment_user_likecomments",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name="PostMedia",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "media_file",
                    models.FileField(
                        max_length=10485760,
                        upload_to=social_layer.mediautils.models.choose_upload_media_to,
                    ),
                ),
                (
                    "media_thumbnail",
                    models.FileField(
                        blank=True,
                        max_length=10485760,
                        null=True,
                        upload_to=social_layer.mediautils.models.choose_upload_media_thumb_to,
                    ),
                ),
                (
                    "content_type",
                    models.CharField(blank=True, max_length=127, null=True),
                ),
                ("orientation", models.CharField(default="portrait", max_length=10)),
                ("format_tries", models.IntegerField(default=0)),
                ("formated", models.BooleanField(default=False)),
                ("md5_hash", models.CharField(blank=True, max_length=32, null=True)),
                (
                    "post",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="social_layer.post",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="post",
            name="comments",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="post_commentsection",
                to="social_layer.commentsection",
            ),
        ),
        migrations.AddField(
            model_name="post",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="post_commentsection_owner",
                to="social_layer.socialprofile",
            ),
        ),
        migrations.CreateModel(
            name="LikePost",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("like", models.BooleanField(default=True)),
                (
                    "date_time",
                    models.DateTimeField(default=django.utils.timezone.localtime),
                ),
                (
                    "comment_section",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="like_commentsection",
                        to="social_layer.commentsection",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="likecomment_user_likeposts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
