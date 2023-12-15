# This file is part of django-social-layer
#
#    django-social-layer is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    django-social-layer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with django-social-layer. If not, see <http://www.gnu.org/licenses/>.

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

from social_layer.comments.models import CommentSection
from social_layer.mediautils.tests import small_image, small_video
from social_layer.profiles.models import SocialProfile


@override_settings(MEDIA_ROOT="/tmp/media_test_{}/".format(uuid4().hex))
class ProfilesTestCase(TestCase):
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

    def test_community(self):
        """test the list profiles view"""
        client = Client()
        client.force_login(self.bob)
        response = client.get(reverse("social_layer:profiles:list_profiles"))
        self.assertIn(self.bob_sprofile.nick, str(response.content))
        self.assertEqual(response.status_code, 200)

    def test_view_profile(self):
        """test the profile page"""
        client = Client()
        client.force_login(self.bob)
        response = client.get(self.alice_sprofile.get_url())
        self.assertIn(self.alice_sprofile.nick, str(response.content))
        self.assertEqual(response.status_code, 200)

    def test_setup_profile(self):
        """check the profile setup page"""
        client = Client()
        client.force_login(self.bob)
        url = reverse("social_layer:profiles:setup_profile")
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        post_data = {
            "nick": "Bob Tester",
            "phrase": "Testing this",
            "receive_email": "on",
        }
        response = client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.bob_sprofile.refresh_from_db()
        self.assertEqual(self.bob_sprofile.nick, post_data["nick"])
        self.assertEqual(self.bob_sprofile.phrase, post_data["phrase"])

    def test_setup_profile_not_optin(self):
        """test user consent to receive emails"""
        client = Client()
        client.force_login(self.bob)
        url = reverse("social_layer:profiles:setup_profile")
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        post_data = {
            "nick": "Bob Tester",
            "phrase": "Testing this",
            "receive_email": "",
        }
        response = client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.bob_sprofile.refresh_from_db()
        self.assertEqual(self.bob_sprofile.nick, post_data["nick"])
        self.assertEqual(self.bob_sprofile.phrase, post_data["phrase"])

    def test_set_profile_photo(self):
        """test setting up a profile picture"""
        client = Client()
        client.force_login(self.bob)
        post_data = {
            "nick": "Bob Tester",
            "phrase": "Testing this",
            "receive_email": "on",
            "picture": SimpleUploadedFile(
                "image.png", b64decode(small_image), content_type="image/png"
            ),
        }
        url = reverse("social_layer:profiles:setup_profile")
        response = client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.bob_sprofile.refresh_from_db()
        self.assertEqual(self.bob_sprofile.nick, post_data["nick"])
        self.assertEqual(self.bob_sprofile.phrase, post_data["phrase"])
        self.assertIsNotNone(self.bob_sprofile.picture())
        self.assertTrue(os.path.isfile(self.bob_sprofile.picture().media_file.path))
        self.assertTrue(
            os.path.isfile(self.bob_sprofile.picture().media_thumbnail.path)
        )
        self.assertEqual(self.bob_sprofile.picture().content_type, "image/png")

    def test_delete_profile_photo(self):
        self.test_set_profile_photo()
        client = Client()
        client.force_login(self.bob)
        self.bob_sprofile.refresh_from_db()
        pic = self.bob_sprofile.picture()
        url = reverse("social_layer:profiles:delete_profile_photo")
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        response = client.post(url)
        self.bob_sprofile._cached_profoto = None  # force refresh
        self.bob_sprofile.refresh_from_db()
        self.assertIsNone(self.bob_sprofile.picture())
        self.assertFalse(os.path.isfile(pic.media_file.path))
        self.assertFalse(os.path.isfile(pic.media_thumbnail.path))

    def test_set_video_as_photo(self):
        """test setting up a profile picture"""
        client = Client()
        client.force_login(self.bob)
        post_data = {
            "nick": "Bob Tester",
            "phrase": "Testing this",
            "receive_email": "on",
            "picture": SimpleUploadedFile(
                "video.mp4", b64decode(small_video), content_type="video/mp4"
            ),
        }
        url = reverse("social_layer:profiles:setup_profile")
        response = client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.bob_sprofile.refresh_from_db()
        self.assertEqual(self.bob_sprofile.nick, post_data["nick"])
        self.assertEqual(self.bob_sprofile.phrase, post_data["phrase"])
        self.assertIsNotNone(self.bob_sprofile.picture())
        self.assertTrue(os.path.isfile(self.bob_sprofile.picture().media_file.path))
        self.assertTrue(
            os.path.isfile(self.bob_sprofile.picture().media_thumbnail.path)
        )
        self.assertEqual(self.bob_sprofile.picture().content_type, "video/mp4")
