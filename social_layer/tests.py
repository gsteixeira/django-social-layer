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


from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse


class SocialLayerTestCase(TestCase):
    """Test Cases for the Social Media application.
    There are more tests for each app inside each one.
    """

    def test_social_login(self):
        """test the login page defined in SOCIAL_VISITOR_LOGIN"""
        client = Client()
        response = client.get(reverse("social_layer:social_login"), follow=True)
        self.assertEqual(
            "/" + settings.SOCIAL_VISITOR_LOGIN, response.redirect_chain[0][0]
        )
