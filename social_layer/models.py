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

from django.db import models

# Create your models here.
import uuid
from django.db import models
from django.utils import timezone
from django.urls import reverse
from mediautils.models import Media

#### Social Profile
class SocialProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    nick = models.CharField(max_length=64, null=True, blank=True)
    phrase = models.CharField(max_length=256, null=True, blank=True)

    date_time = models.DateTimeField(default=timezone.localtime)
    last_actv = models.DateTimeField(default=timezone.localtime)
    ip = models.CharField(max_length=46, null=True, blank=True)

    comment_section = models.OneToOneField('social_layer.CommentSection',
                                           related_name='sprofile_comment_section',
                                           on_delete=models.SET_NULL,
                                           null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.nick:
            if '@' in self.user.username:
                self.nick = self.user.username.split('@')[0]
            else:
                self.nick = self.user.username
        if self.nick:
            self.nick = self.nick[0:64]
        if self.phrase:
            self.phrase = self.phrase[0:256]
        super(SocialProfile, self).save(*args, **kwargs)

    def picture(self):
        if not hasattr(self, 'cached_profoto'):
            self.cached_profoto = SocialProfilePhoto.objects.filter(
                                                    profile=self).last()
        return self.cached_profoto

    def get_url(self):
        return reverse('social_layer:view_profile', kwargs={'pk':self.pk})
    
class SocialProfilePhoto(Media):
    profile = models.ForeignKey(SocialProfile, on_delete=models.CASCADE)

#### Comments
class CommentSection(models.Model):
    owner = models.ForeignKey('social_layer.SocialProfile',
                              related_name='comment_section_owner',
                              null=True, blank=True,
                              on_delete=models.CASCADE)
    url = models.TextField(null=True, blank=True)
   
    comments_enabled = models.BooleanField(default=True)
    owner_can_delete = models.BooleanField(default=False)
    anyone_can_reply = models.BooleanField(default=True)
    is_flat = models.BooleanField(default=True)
    
    count_replies = models.PositiveIntegerField(default=0)
    count_likes = models.PositiveIntegerField(default=0)
    count_dislikes = models.PositiveIntegerField(default=0)

    cached_featured = models.TextField(blank=True, default="")
    
    def get_url(self):
        if self.url:
            return self.url
        else:
            return reverse('social_layer:comment_section',
                           kwargs={'pk':self.pk})

    def get_comments(self):
        featured = getattr(self, 'featured', False)
        comment_list = Comment.objects.filter(comment_section=self,
                                              reply_to=None)
        if featured:
            MAX_FEATURED_COMMENTS = 3
            return comment_list[0:MAX_FEATURED_COMMENTS]
        else:
            return comment_list
    
    def get_featured_comments(self):
        MAX_FEATURED_COMMENTS = 3
        return self.get_comments()[0:MAX_FEATURED_COMMENTS]


class Comment(models.Model):
    comment_section = models.ForeignKey('social_layer.CommentSection',
                                        related_name='comment_section',
                                        on_delete=models.CASCADE)
    author = models.ForeignKey('social_layer.SocialProfile',
                               related_name='comment_author',
                               on_delete=models.CASCADE)
    text = models.TextField()
    date_time = models.DateTimeField(default=timezone.localtime)
    
    reply_to = models.ForeignKey('social_layer.Comment',
                                related_name='comment_reply_to',
                                on_delete=models.CASCADE,
                                null=True, blank=True)
        
    count_replies = models.PositiveIntegerField(default=0)
    count_likes = models.PositiveIntegerField(default=0)
    count_dislikes = models.PositiveIntegerField(default=0)

    class Meta():    
        ordering = ['-date_time']

    def save(self, *args, **kwargs):
        if self.text:
            self.text = self.text.replace('\n', ' ')[0:512]
            other = Comment.objects.exclude(pk=self.pk
                                  ).filter(author=self.author,
                                           text=self.text,
                                           comment_section=self.comment_section,
                                           reply_to=self.reply_to)
            if not other.exists():
                super(Comment, self).save(*args, **kwargs)

    def get_replies(self):
        """ Return all the replies to this comment """
        if not hasattr(self, 'cached_get_replies'):
            replies = Comment.objects.filter(comment_section=self.comment_section,
                                             reply_to=self)
            self.cached_get_replies = replies
        return self.cached_get_replies

    def updt_counters(self):
        """ Updates the counting """
        self.count_likes = LikeComment.objects.filter(comment=self,
                                                      like=True).count()
        self.count_dislikes = LikeComment.objects.filter(comment=self,
                                                         like=False).count()
        self.count_replies = Comment.objects.filter(reply_to=self).count()
        self.save()

#### Notifications
class Notification(models.Model):
    to = models.ForeignKey('auth.User',
                           related_name='notification_to',
                           on_delete=models.CASCADE)
    text = models.TextField()
    date_time = models.DateTimeField(default=timezone.localtime)
    read = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        other = Notification.objects.exclude(pk=self.pk
                                ).filter(to=self.to,
                                        text=self.text,
                                        date_time__date=self.date_time.date())
        if not other.exists():
            super(Notification, self).save(*args, **kwargs)

#### Likes
class LikeComment(models.Model):
    user = models.ForeignKey('auth.User', related_name='likecomment_user',
                             on_delete=models.CASCADE)
    comment = models.ForeignKey('social_layer.Comment', 
                                related_name='like_comment',
                                on_delete=models.CASCADE)
    like = models.BooleanField(default=True)
    date_time = models.DateTimeField(default=timezone.localtime)

#### Friendships
