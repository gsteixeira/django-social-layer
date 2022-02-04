# -*- coding: utf-8 -*-
"""
Social Layer media utils module.

This was extracted from the my decades old django-mediautils module.
This is *very old* but running code, yet to be optimized.
Sorry for the mess.
"""

import cv2
import json
import hashlib
import logging
import mimetypes
import os
import random
import shutil
import sys
import traceback
from uuid import uuid4
from PIL import (Image, ImageDraw, ImageFont,
                 ImageSequence, UnidentifiedImageError)
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files import File
#
from social_layer.mediautils.models import Media
from social_layer.mediautils.tasks import crop_video_task

logger = logging.getLogger(__name__)

TEMP_FILE_DIR = '/tmp'

DEFAULT_IMG_WIDTH=480
DEFAULT_IMG_HEIGHT=360
DEFAULT_VIDEO_WIDTH=320
DEFAULT_VIDEO_HEIGHT=240
DEFAULT_EXTENSION=getattr(settings, "SOCIAL_LAYER_DEFAULT_EXT", "jpg")


def crop_image(img_file:str,
                 larger:int=DEFAULT_IMG_WIDTH,
                 smaller:int=DEFAULT_IMG_HEIGHT,
                 quality:int=1):
    """ reduce image size """
    larger *= quality
    smaller *= quality
    cropamap = {
        'landscape': (int(larger), int(smaller)),
        'portrait':  (int(smaller), int(larger)),
        }
    try:
        orient = get_img_orientation(img_file)
        # convert to jpg
        img = Image.open(img_file)
        img = img.convert('RGBA')
        background = Image.new("RGBA", img.size, "WHITE")
        background.paste(img, (0, 0), img) 
        img = background.convert('RGB')
        img.save(img_file, "JPEG", optimize=True, quality=80)

        fd_img = open(img_file, 'rb')
        img = Image.open(fd_img)
        img.thumbnail(cropamap[orient], Image.ANTIALIAS)
        img.save(img_file, "JPEG", optimize=True, quality=80)
        fd_img.close()
        ret = cropamap[orient]
    except Exception as e:
        ret = 'landscape'
        logger.error(e)
    return ret


def crop_video(video_file,
                larger=DEFAULT_VIDEO_WIDTH,
                smaller=DEFAULT_VIDEO_HEIGHT,
                quality=1):
    """ reduce video size """
    larger *= quality
    smaller *= quality
    file_temp = f"/tmp/{uuid4().hex}.mp4"
    try:
        #+ ' -s '+str(larger) +'x'+ str(smaller)+' '
        #+ ' -c:v libx264 -preset slow -an -b:v 370K '
        #+ ' -c:a aac -movflags +faststart '
        #+ ''' -vf "scale='min('''+str(larger) +''',iw)':'min('''+str(smaller) +''',ih)'" '''
        cmd = ' '.join(['/usr/bin/ffmpeg -hide_banner -loglevel error -i',
                        video_file,
                        f"-vf scale={larger}:-2",
                        file_temp])
        os.system(cmd)
        if os.path.isfile(file_temp):
            shutil.move(file_temp, video_file)
            return True
    except Exception as e:
        logger.error(e)
    return False


def rotate_image(img_file, direct='left'):
    """ rotate image """
    if direct=='left':
        angle = 90
    else:
        angle = -90
    fd_img = open(img_file, 'rb')
    img = Image.open(fd_img)
    rot = img.rotate(angle, expand=1, resample=Image.BICUBIC)
    fd_img.close()
    rot.save(img_file)
    
    
def get_img_orientation(img_file):
    """ Get the orientation of image """
    try:
        img = cv2.imread(img_file)
        height, width, channels = img.shape
        h, w = img.shape[:2]
        if h > w:
            return 'portrait'
        else:
            return 'landscape'
    except Exception as e:
        logger.error(e)
        return 'portrait'


def md5sum(filename, blocksize=65536):
    """ Get md5sum from file """
    hashe = hashlib.md5()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            hashe.update(block)
        f.close()
    return hashe.hexdigest()


def get_md5(content_file):
    """ return a md5 hash for a InMemoryFile """
    hash_sum = hashlib.md5()
    for chunk in content_file.chunks():
        hash_sum.update(chunk)
    return hash_sum.hexdigest()


def convert_tojpeg(tempo_file):
    """ convert image to jpeg """
    try:
        img = Image.open(tempo_file)
        img = img.convert('RGBA')
        background = Image.new("RGBA", img.size, "WHITE")
        background.paste(img, (0, 0), img) 
        img = background.convert('RGB')
        img.save(tempo_file, "JPEG", optimize=True, quality=80)
    except Exception as err:
        logger.error(f"ERROR: convert_tojpeg {err}")


def convert_towebp(tempo_file):
    """ convert image to webp
    requires libwebp-dev
    """
    try:
        img = Image.open(tempo_file)
        img = img.convert('RGBA')
        background = Image.new("RGBA", img.size, "WHITE")
        background.paste(img, (0, 0), img) 
        img = background.convert('RGB')
        img.save(tempo_file, "WEBP")
    except Exception as e:
        logger.error(e)


def handle_upload_file(file_post=None,
                     Model=None,
                     extra_args={},
                     quality=1):
    """ handle a file upload """
    media = Model(**extra_args)
    media.media_file = file_post
    media.content_type = file_post.content_type
    media.md5_hash = get_md5(file_post)
    media.save()
    if ("image/" in media.content_type
        or "video/" in media.content_type
        or media.content_type == "application/octet-stream"):
        shrink_and_thumbs(media)


def shrink_and_thumbs(media:Media):
    """ Shrink media files and get thumbnails
    :param media: the Media object
    :type media; Media
    """
    media.formated = True
    if "image/" in media.content_type:
        # Crop the imagem of thumbnail
        with open(media.media_file.path, 'rb') as thumb:
            media.media_thumbnail.save(os.path.basename(media.media_file.name),
                                       File(thumb))
        crop_image(media.media_thumbnail.path, quality=1)
        convert_tojpeg(media.media_thumbnail.path)
        # unless is a gif, crop the image
        if not is_gif(media):
            crop_image(media.media_file.path, quality=2)
            convert_tojpeg(media.media_file.path)
        media = rename_extension(media, extension=DEFAULT_EXTENSION)
    elif "video/" in media.content_type:
        get_thumb_from_video(media)
        # Crop video in a celery task
        if hasattr(settings, 'CELERY_BROKER_URL'):
            try:
                crop_video_task.delay(media.media_file.path)
            except ConnectionRefusedError:
                logger.error("Could not connect to CELERY_BROKER_URL")
    media.save()


def rename_extension(media:Media, extension:str=DEFAULT_EXTENSION)->Media:
    """ rename file in filefield to a new extension """
    for field in ("media_file", "media_thumbnail"):
        old_path = getattr(media, field).path
        old_base = os.path.basename(old_path)
        old_rel_path = os.path.dirname(getattr(media, field).name)
        dir_path_name = os.path.dirname(old_path)
        base, ext = os.path.splitext(old_base)
        # Make a new name.jpg
        new_name = f"{base}.{extension}"
        new_path = f"{dir_path_name}{new_name}"
        new_rel_path = f"{old_rel_path}{new_name}"
        os.rename(getattr(media, field).path, new_path)
        setattr(getattr(media, field), "name", new_rel_path)
        media.save()
    return media


def get_thumb_from_video(video:Media):
    """ extract thumbnail from videos.
    requires ffmpeg
    """
    thumbnail_temp = f"/tmp/{uuid4().hex}.jpg"
    cmd = ' '.join([
                '/usr/bin/ffmpeg -hide_banner -loglevel panic -y -ss 0 -i',
                video.media_file.path,
                ' -frames:v 1 -s 400x300 ',
                thumbnail_temp
            ])
    os.system(cmd)
    if os.path.isfile(thumbnail_temp):
        #thumbnail
        thumb_file = open(thumbnail_temp, 'rb')
        video.media_thumbnail.save(os.path.basename(video.media_file.name),
                                   File(thumb_file))
        thumb_file.close()
        os.remove(thumbnail_temp)


def check_if_img(file_path:str)->bool:
    """ check if file given by path is an actual IMAGE file
    """
    try:
        media_file = Image.open(file_path)
    except (UnidentifiedImageError, FileNotFoundError) as e:
        return False
    return (len(list(ImageSequence.Iterator(media_file))) > 0)


def is_gif(media:Media)->bool:
    """ check if Media object is a gif file
    :return bool:
    """
    return (media.content_type == "image/gif"
            or (media.content_type == "application/octet-stream"
                and check_if_img(media.media_file.path)))


def fix_gif(tempo_file:str, mime_type:str):
    """ fix gifs that came with mime 'application/octet-stream'
    """
    if ('application/octet-stream' in mime_type):
        # se for octet stream, tem q converter ele pra gif
        gif_name = f"{tempo_file}.gif"
        os.system(f"convert {tempo_file} {gif_name}")
        if os.path.isfile(gif_name):
            shutil.move(gif_name, tempo_file)

def format_media(post:Media):
    """ Format media files. 
    Resize images, extract thumbnails, and shrink videos.
    :param post: the media object to be formated.
    :type post: social_layer.mediautils.models.Media
    This is due to be DEPRECATED in a next version.
    """
    if post.content_type:
        if 'video/' in post.content_type:
            post.formated = crop_video(post.media_file.path,
                                        larger=wsize, smaller=hsize)
            # reconnect because we probably have a timeout
            connection.connection.close()
            connection.connection = None
            get_thumb_from_video(post)
            if post.media_thumbnail:
                convert_tojpeg(post.media_thumbnail.path)
        elif 'image/gif' in post.content_type:
            crop_image(post.media_thumbnail.path, quality=1)
            convert_tojpeg(post.media_thumbnail.path)
        elif 'image/' in post.content_type:
            has_media = (post.media_file and os.path.isfile(post.media_file.path))
            has_thumb = (post.media_thumbnail and os.path.isfile(post.media_thumbnail.path))
            if (not has_media and not has_thumb):
                post.delete()
                return
            elif (has_media and not has_thumb):
                post.media_thumbnail = post.media_file
                post.save()
            elif (has_thumb and not has_media):
                post.media_file = post.media_thumbnail
                post.save()
            crop_image(post.media_file.path, quality=2)
            crop_image(post.media_thumbnail.path, quality=1)
            convert_tojpeg(post.media_thumbnail.path)
    post.formated = True
    post.save()
