import logging
import os
import shutil
from base64 import b64decode
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

from social_layer.comments.models import CommentSection, LikePost
from social_layer.mediautils.tests import small_image
from social_layer.posts.models import Post, PostMedia
from social_layer.profiles.models import SocialProfile


@override_settings(MEDIA_ROOT="/tmp/media_test_{}/".format(uuid4().hex))
class PostsTestCase(TestCase):
    """Test Cases for the Social Media application.
    currently covering around 80% of the code.
    """

    def setUp(self):
        """create users and a comment section"""
        super().setUp()
        self.bob = User.objects.create(username="Bob")
        self.bob_sprofile = SocialProfile.objects.create(user=self.bob)
        logging.disable(logging.INFO)
        self.alice = User.objects.create(username="Alice")
        self.alice_sprofile = SocialProfile.objects.create(user=self.alice)
        self.comment_section = CommentSection.objects.create(owner=self.alice_sprofile)

    def tearDown(self):
        """removes created files"""
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    # Posts
    def test_write_post(self):
        """write a simple text post"""
        client = Client()
        client.force_login(self.bob)
        post_data = {
            "text": "gonna have a sandwich",
        }
        url = reverse("social_layer:posts:new_post")
        response = client.post(url, post_data, follow=True)
        post = Post.objects.all().last()
        self.assertEqual(post.text, post_data["text"])
        self.assertIn(post_data["text"], str(response.content))

        response = client.get(post.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertIn(post_data["text"], str(response.content))

        response = client.get(post.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertIn(post_data["text"], str(response.content))
        return post

    def test_delete_post(self):
        """ """
        post = self.test_write_post()
        client = Client()
        client.force_login(self.bob)
        client = Client()
        client.force_login(self.bob)
        url = reverse("social_layer:posts:delete_post", kwargs={"pk": post.pk})
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        response = client.post(url)
        self.assertIsNone(Post.objects.filter(pk=post.pk).last())

    @override_settings(SOCIAL_ALLOW_MEDIA_POSTS=True)
    def test_write_post_with_file(self):
        """write a post with media file"""
        from social_layer.posts.forms import PostForm

        PostForm.allow_media = True  # monkey_patch
        client = Client()
        client.force_login(self.bob)
        post_data = {
            "text": "this is my cat",
            "media": SimpleUploadedFile(
                "cat.png", b64decode(small_image), content_type="image/png"
            ),
        }
        url = reverse("social_layer:posts:new_post")
        response = client.post(url, post_data, follow=True)
        post = Post.objects.all().last()
        self.assertEqual(post.text, post_data["text"])
        self.assertIn(post_data["text"], str(response.content))
        self.assertIsNotNone(post.postmedia)

        post_media = post.postmedia
        self.assertIn(post.postmedia.media_thumbnail.url, str(response.content))
        self.assertIn(".jpg", post.postmedia.media_thumbnail.url)
        self.assertTrue(os.path.isfile(post.postmedia.media_thumbnail.path))
        # delete_post
        url = reverse("social_layer:posts:delete_post", kwargs={"pk": post.pk})
        response = client.get(url)
        response = client.post(url)
        self.assertIsNone(Post.objects.filter(pk=post.pk).last())
        self.assertIsNone(PostMedia.objects.filter(pk=post_media.pk).last())
        self.assertFalse(os.path.isfile(post.postmedia.media_file.path))
        self.assertFalse(os.path.isfile(post.postmedia.media_thumbnail.path))

    @override_settings(SOCIAL_ALLOW_MEDIA_POSTS=False)
    def test_write_post_with_file_denied(self):
        """write a post with media file, but its not allowed :("""
        from social_layer.posts.forms import PostForm

        PostForm.allow_media = False  # monkey_patch
        client = Client()
        client.force_login(self.bob)
        post_data = {
            "text": "this is my cat",
            "media": SimpleUploadedFile(
                "cat.png", b64decode(small_image), content_type="image/png"
            ),
        }
        url = reverse("social_layer:posts:new_post")
        self.assertIsNone(Post.objects.all().last())
        client.post(url, post_data, follow=True)
        post = Post.objects.all().last()
        self.assertIsNotNone(post)

    def test_write_post_empty(self):
        """write a empty post. not allowed :("""
        client = Client()
        client.force_login(self.bob)
        client.post(reverse("social_layer:posts:new_post"), {"text": ""}, follow=True)
        post = Post.objects.all().last()
        self.assertIsNone(post)

    def test_posts_feed_view(self):
        """test the view more_posts, used by infscroll module"""
        post = self.test_write_post()
        client = Client()
        url = reverse("social_layer:posts:posts_feed")
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(post.text, str(response.content))

    def test_posts_feed_scroll(self):
        """test the view more_posts, used by infscroll module"""
        post = self.test_write_post()
        client = Client()
        url = reverse("social_layer:posts:more_posts")
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(post.text, str(response.content))

    def test_like_post(self):
        """Hit the like button on a post"""
        client = Client()
        client.force_login(self.bob)

        url = reverse(
            "social_layer:posts:like_post",
            kwargs={"pk": self.comment_section.pk, "didlike": "like"},
        )
        client.get(url)

        like = LikePost.objects.get(user=self.bob)
        self.assertTrue(like.like)
        self.comment_section.refresh_from_db()
        self.assertEqual(self.comment_section.count_likes, 1)
        self.assertEqual(self.comment_section.count_dislikes, 0)

    def test_dislike_post(self):
        """Hit the dislike button on a post"""
        client = Client()
        client.force_login(self.bob)

        url = reverse(
            "social_layer:posts:like_post",
            kwargs={"pk": self.comment_section.pk, "didlike": "dislike"},
        )
        client.get(url)

        like = LikePost.objects.get(user=self.bob)
        self.assertFalse(like.like)
        self.comment_section.refresh_from_db()
        self.assertEqual(self.comment_section.count_likes, 0)
        self.assertEqual(self.comment_section.count_dislikes, 1)
