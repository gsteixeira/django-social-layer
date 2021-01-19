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

from django.conf.urls import url, include
from django.urls import path
from django.conf import settings
#from django.conf.urls.static import static


import social_layer

#from social_layer.views.comments import *

from social_layer.views.profile import *
from social_layer.views.comments import *
from social_layer.views.notifications import *

app_name = 'social_layer'

urlpatterns = [
    ##############
        # profile
        path('profile/', 
             social_layer.views.profile.setup_profile, name='setup_profile'),
        path('profile/<int:pk>/',
             social_layer.views.profile.view_profile, name='view_profile'),
        path('community/',
             social_layer.views.profile.list_profiles, name='list_profiles'),
        path('social-login/',
             social_layer.views.profile.social_login, name='social_login'),
        # comments
        path('comments/',
             social_layer.views.comments.comment_section, name='comment_section'),
        path('comments/<int:pk>/',
             social_layer.views.comments.comment_section, name='comment_section'),
        path('reply-comment/<int:pk>/',
             social_layer.views.comments.reply_comment, name='reply_comment'),
        path('del-comment/<int:pk>/',
             social_layer.views.comments.delete_comment, name='delete_comment'),
        # likes
        path('like-comment/<int:pk>/<slug:didlike>/',
             social_layer.views.comments.like_comment, name='like_comment'),
        # notifications
        path('notifications/',
             social_layer.views.notifications.view_notifications, name='view_notifications'),
        path('notifications/adm-send/<int:pk>/',
             social_layer.views.notifications.admin_send_notification, name='admin_send_notification'),

        ]

