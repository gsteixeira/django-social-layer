import logging
import shutil
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

##
from social_layer.comments.models import Comment, CommentSection
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

    def test_see_notifications(self):
        """test the notifications page"""
        self.test_write_comment()
        client = Client()
        client.force_login(self.alice)
        response = client.get(reverse("social_layer:notifications:view_notifications"))
        self.assertIn("Bob", str(response.content))
        self.assertEqual(response.status_code, 200)
        notif = Notification.objects.get(to=self.alice)
        self.assertTrue(notif.read)
