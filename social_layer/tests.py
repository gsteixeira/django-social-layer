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

from django.test import TestCase, Client
## Create your tests here.
from uuid import uuid4
import random
import shutil
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.utils import override_settings
##
from social_layer.models import (CommentSection, Comment, SocialProfile,
                                 Notification, LikeComment)

random_stuff = uuid4().hex

@override_settings(MEDIA_ROOT='/tmp/media_teste{}/'.format(random_stuff))
class SocialLayerTestCase(TestCase):
    """ Test Cases for the Social Media application.
    currently covering around 80% of the code.
    """
    def setUp(self):
        """ create two users and a comment section """
        super(SocialLayerTestCase, self).setUp()
        self.bob = User.objects.create(username='Bob')
        self.alice = User.objects.create(username='Alice')
        # log once to create social_profile
        self.bob_sprofile = SocialProfile.objects.create(user=self.bob)
        self.alice_sprofile = SocialProfile.objects.create(user=self.alice)
        
        self.comment_section = CommentSection.objects.create(
                                                    owner=self.alice_sprofile)

    def tearDown(self):
        """ removes created files """
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_write_comment(self):
        """ Bob writes a comment at Alice's page. """
        client = Client()
        client.force_login(self.bob)
        section = CommentSection.objects.create(owner=self.alice_sprofile)
        response = client.get(section.get_url())
        self.assertIn(self.alice.username, str(response.content))
        post_data = {
            'text': uuid4().hex,
            }
        response = client.post(section.get_url(), post_data, follow=True)
        self.assertIn(self.bob_sprofile.nick, str(response.content))
        self.assertIn(post_data['text'], str(response.content))
        notif = Notification.objects.get(to=self.alice)
        self.assertFalse(notif.read)
        
    def test_comments_and_replies(self):
        """ Bob and Alice comments at each other's comments. """
        section = CommentSection.objects.create(owner=self.alice_sprofile)
        messages = []
        for user in [self.bob, self.alice]:
            client = Client()
            client.force_login(user)
            for i in range(5):
                post_data = {'text': uuid4().hex,}
                response = client.post(section.get_url(), post_data, follow=True)
                self.assertIn(post_data['text'], str(response.content))
                messages.append(post_data['text'])
        for user in [self.bob, self.alice]:
            client = Client()
            client.force_login(user)
            for i in range(10):
                post_data = {'text': uuid4().hex,}
                a_comment = random.choice(Comment.objects.all())
                url = reverse('social_layer:reply_comment',
                              kwargs={'pk': a_comment.pk})
                response = client.post(url, post_data, follow=True)
                self.assertIn(post_data['text'], str(response.content))
                messages.append(post_data['text'])
        response = client.get(section.get_url()+'?show-comments')
        for msg in messages:
            self.assertIn(msg, str(response.content))

    def test_repeat_comment(self):
        """ Ensures that a comment can't be made twice """
        client = Client()
        client.force_login(self.bob)
        section = CommentSection.objects.create(owner=self.alice_sprofile)
        response = client.get(section.get_url())
        self.assertIn(self.alice.username, str(response.content))
        post_data = {
            'text': uuid4().hex,
            }
        for i in range(0,3):
            response = client.post(section.get_url(), post_data, follow=True)
        self.assertIn(self.bob_sprofile.nick, str(response.content))
        self.assertIn(post_data['text'], str(response.content))
        comments = Comment.objects.filter(comment_section=section)
        self.assertEqual(comments.count(), 1)
        notifs = Notification.objects.filter(to=self.alice)
        self.assertEqual(notifs.count(), 1)
        self.assertFalse(notifs[0].read)

    def test_community(self):
        """ test the list profiles view """
        client = Client()
        client.force_login(self.bob)
        response = client.get(reverse('social_layer:list_profiles'))
        self.assertIn(self.bob_sprofile.nick, str(response.content))
        self.assertEqual(response.status_code, 200)
        
    def test_view_profile(self):
        """ test the profile page """
        client = Client()
        client.force_login(self.bob)
        response = client.get(self.alice_sprofile.get_url())
        self.assertIn(self.alice_sprofile.nick, str(response.content))
        self.assertEqual(response.status_code, 200)
        
       
    def test_setup_profile(self):
        """ check the profile setup page """
        client = Client()
        client.force_login(self.bob)
        url = reverse('social_layer:setup_profile')
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        post_data = {
            'nick': 'Bob Tester',
            'phrase': 'Testing this',
            'receive_email': 'on',
            }
        response = client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.bob_sprofile.refresh_from_db()
        self.assertEqual(self.bob_sprofile.nick, post_data['nick'])
        self.assertEqual(self.bob_sprofile.phrase, post_data['phrase'])

    def test_setup_profile_not_optin(self):
        """ test user consent to receive emails """
        client = Client()
        client.force_login(self.bob)
        url = reverse('social_layer:setup_profile')
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        post_data = {
            'nick': 'Bob Tester',
            'phrase': 'Testing this',
            'receive_email': '',
            }
        response = client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.bob_sprofile.refresh_from_db()
        self.assertEqual(self.bob_sprofile.nick, post_data['nick'])
        self.assertEqual(self.bob_sprofile.phrase, post_data['phrase'])
        
    def test_social_login(self):
        """ test the login page defined in SOCIAL_VISITOR_LOGIN """
        client = Client()
        response = client.get(reverse('social_layer:social_login'), follow=True)
        self.assertEqual('/'+settings.SOCIAL_VISITOR_LOGIN, response.redirect_chain[0][0])
        
    def test_see_notifications(self):
        """ test the notifications page """
        self.test_write_comment()
        client = Client()
        client.force_login(self.alice)
        response = client.get(reverse('social_layer:view_notifications'))
        self.assertIn('Bob', str(response.content))
        self.assertEqual(response.status_code, 200)
        notif = Notification.objects.get(to=self.alice)
        self.assertTrue(notif.read)

    def test_like_comment(self):
        """ Hit the like button """
        self.test_write_comment()
        client = Client()
        client.force_login(self.alice)
        comment = Comment.objects.all()[0]
        response = client.get(reverse('social_layer:like_comment',
                                      kwargs={'pk': comment.pk,
                                              'didlike': 'like'}))
        self.assertEqual(response.status_code, 302)
        like = LikeComment.objects.get(user=self.alice)
        self.assertTrue(like.like)
        comment.refresh_from_db()
        self.assertEqual(comment.count_likes, 1)
        self.assertEqual(comment.count_dislikes, 0)
        

    def test_dislike_comment(self):
        """ Hit the dislike button """
        self.test_write_comment()
        client = Client()
        client.force_login(self.alice)
        comment = Comment.objects.all()[0]
        response = client.get(reverse('social_layer:like_comment',
                                      kwargs={'pk': comment.pk,
                                              'didlike': 'dislike'}))
        self.assertEqual(response.status_code, 302)
        like = LikeComment.objects.get(user=self.alice)
        self.assertFalse(like.like)
        comment.refresh_from_db()
        self.assertEqual(comment.count_likes, 0)
        self.assertEqual(comment.count_dislikes, 1)
        





    
