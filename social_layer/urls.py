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

from django.conf.urls import include
from django.urls import path

from social_layer.profiles.views import social_login

app_name = "social_layer"

urlpatterns = [
    path(
        "",
        include(
            ("social_layer.profiles.urls", "profilesprofiles"), namespace="profiles"
        ),
    ),
    path("", include(("social_layer.comments.urls", "comments"), namespace="comments")),
    path(
        "",
        include(
            ("social_layer.notifications.urls", "notifications"),
            namespace="notifications",
        ),
    ),
    path("", include(("social_layer.posts.urls", "posts"), namespace="posts")),
    path("social-login/", social_login, name="social_login"),
]
