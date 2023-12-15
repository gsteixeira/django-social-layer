import logging
import random
import shutil
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

from social_layer.comments.models import Comment, CommentSection, LikeComment
from social_layer.notifications.models import Notification
from social_layer.profiles.models import SocialProfile


@override_settings(MEDIA_ROOT="/tmp/media_test_{}/".format(uuid4().hex))
class SocialLayerTestCase(TestCase):
    """Test Cases for the Social Media application.
    currently covering around 80% of the code.
    """

    def setUp(self):
        """create two users and a comment section"""
        super().setUp()
        self.bob = User.objects.create(username="Bob")
        self.alice = User.objects.create(username="Alice")
        # log once to create social_profile
        self.bob_sprofile = SocialProfile.objects.create(user=self.bob)
        self.alice_sprofile = SocialProfile.objects.create(user=self.alice)

        self.comment_section = CommentSection.objects.create(owner=self.alice_sprofile)
        # disable logging
        logging.disable(logging.INFO)

    def tearDown(self):
        """removes created files"""
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_write_comment(self):
        """Bob writes a comment at Alice's page."""
        client = Client()
        client.force_login(self.bob)
        section = CommentSection.objects.create(owner=self.alice_sprofile)
        response = client.get(section.get_url())
        self.assertNotIn(self.alice.username, str(response.content))
        post_data = {
            "text": uuid4().hex,
        }
        response = client.post(section.get_url(), post_data, follow=True)
        self.assertIn(self.bob_sprofile.nick, str(response.content))
        self.assertIn(post_data["text"], str(response.content))
        notif = Notification.objects.get(to=self.alice)
        self.assertFalse(notif.read)
        comment = Comment.objects.get(text=post_data["text"], author=self.bob_sprofile)
        self.assertIsNotNone(comment)
        return comment

    def test_comments_and_replies(self):
        """Bob and Alice comments at each other's comments."""
        section = CommentSection.objects.create(owner=self.alice_sprofile)
        messages = []
        for user in [self.bob, self.alice]:
            client = Client()
            client.force_login(user)
            for i in range(5):
                post_data = {
                    "text": uuid4().hex,
                }
                response = client.post(section.get_url(), post_data, follow=True)
                self.assertIn(post_data["text"], str(response.content))
                messages.append(post_data["text"])
        for user in [self.bob, self.alice]:
            client = Client()
            client.force_login(user)
            for i in range(10):
                post_data = {
                    "text": uuid4().hex,
                }
                a_comment = random.choice(Comment.objects.all())
                url = reverse(
                    "social_layer:comments:reply_comment", kwargs={"pk": a_comment.pk}
                )
                response = client.post(url, post_data, follow=True)
                self.assertIn(post_data["text"], str(response.content))
                messages.append(post_data["text"])
        response = client.get(section.get_url() + "?show-comments")
        for msg in messages:
            self.assertIn(msg, str(response.content))

    def test_repeat_comment(self):
        """Ensures that a comment can't be made twice"""
        client = Client()
        client.force_login(self.bob)
        section = CommentSection.objects.create(owner=self.alice_sprofile)
        response = client.get(section.get_url())
        self.assertNotIn(self.alice.username, str(response.content))
        post_data = {
            "text": uuid4().hex,
        }
        for i in range(0, 3):
            response = client.post(section.get_url(), post_data, follow=True)
        self.assertIn(self.bob_sprofile.nick, str(response.content))
        self.assertIn(post_data["text"], str(response.content))
        comments = Comment.objects.filter(comment_section=section)
        self.assertEqual(comments.count(), 1)
        notifs = Notification.objects.filter(to=self.alice)
        self.assertEqual(notifs.count(), 1)
        self.assertFalse(notifs[0].read)

    def test_delete_comment(self):
        comment = self.test_write_comment()

        client = Client()
        client.force_login(self.bob)

        url = reverse("social_layer:comments:delete_comment", kwargs={"pk": comment.pk})
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        response = client.post(url)

        comment = Comment.objects.filter(author=self.bob_sprofile).first()
        self.assertIsNone(comment)

    def test_like_comment(self):
        """Hit the like button"""
        self.test_write_comment()
        client = Client()
        client.force_login(self.alice)
        comment = Comment.objects.all()[0]
        response = client.get(
            reverse(
                "social_layer:comments:like_comment",
                kwargs={"pk": comment.pk, "didlike": "like"},
            )
        )
        self.assertEqual(response.status_code, 302)
        like = LikeComment.objects.get(user=self.alice)
        self.assertTrue(like.like)
        comment.refresh_from_db()
        self.assertEqual(comment.count_likes, 1)
        self.assertEqual(comment.count_dislikes, 0)

    def test_dislike_comment(self):
        """Hit the dislike button"""
        self.test_write_comment()
        client = Client()
        client.force_login(self.alice)
        comment = Comment.objects.all()[0]
        response = client.get(
            reverse(
                "social_layer:comments:like_comment",
                kwargs={"pk": comment.pk, "didlike": "dislike"},
            )
        )
        self.assertEqual(response.status_code, 302)
        like = LikeComment.objects.get(user=self.alice)
        self.assertFalse(like.like)
        comment.refresh_from_db()
        self.assertEqual(comment.count_likes, 0)
        self.assertEqual(comment.count_dislikes, 1)
