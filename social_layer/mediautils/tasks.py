import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def crop_video_task(file_path: str):
    """crop a video in a celery task"""
    from social_layer.mediautils.utils import cropa_video

    cropa_video(file_path)
