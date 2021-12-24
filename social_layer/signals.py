
import os
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from social_layer.posts.models import PostMedia
from social_layer.profiles.models import SocialProfilePhoto

@receiver(post_delete, sender=PostMedia)
@receiver(post_delete, sender=SocialProfilePhoto)
def post_media_post_delete(**kwargs):
    instance = kwargs.get('instance')
    try:
        os.remove(instance.media_file.path)
    except FileNotFoundError:
        pass
    try:
        os.remove(instance.media_thumbnail.path)
    except FileNotFoundError:
        pass

    
