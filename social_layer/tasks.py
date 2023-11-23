from social_layer.mediautils.tasks import formata_all_media
from social_layer.posts.models import PostMedia
from social_layer.profiles.models import SocialProfilePhoto


def format_medias():
    formata_all_media(SocialProfilePhoto)
    formata_all_media(PostMedia)
