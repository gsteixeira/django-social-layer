import os

import logging
from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task
def crop_video_task(file_path:str):
    """ crop a video in a celery task """
    from social_layer.mediautils.utils import cropa_video
    cropa_video(file_path)


def formata_all_media(Model=None):
    """ Manipulate media files as needed
    Will need to use this if you don't want to use celery
    DEPRECATED This will be deprecated in a future release.
    """
    logger.warning("You are using formata_all_media function which is marked "
                   "as DEPRECATED. Please use Celery instead.")
    from social_layer.mediautils.utils import format_media
    list_media = Model.objects.filter(formated=False)
    for post in list_media:
        logger.info("processing {} {}...".format(str(Model), str(post.pk)))
        format_media(post)
