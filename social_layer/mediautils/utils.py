# -*- coding: utf-8 -*-
import json
from uuid import uuid4
import mimetypes
import cv2
import os
import sys
import shutil
import random
from PIL import (Image, ImageDraw, ImageFont,
                 ImageSequence, UnidentifiedImageError)

from django.conf import settings
import logging
import hashlib
import traceback

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files import File
from social_layer.mediautils.models import Media
from social_layer.mediautils.tasks import crop_video_task

logger = logging.getLogger(__name__)

TEMP_FILE_DIR = '/tmp'

DEFAULT_IMG_WIDTH=480
DEFAULT_IMG_HEIGHT=360
DEFAULT_VIDEO_WIDTH=320
DEFAULT_VIDEO_HEIGHT=240

def cropa_imagem(img_file,
                 larger=DEFAULT_IMG_WIDTH,
                 smaller=DEFAULT_IMG_HEIGHT,
                 quality=1):
    """ reduce image size """
    larger *= quality
    smaller *= quality
    cropamap = {
        'landscape': [larger, smaller],
        'portrait':  [smaller, larger],
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

def cropa_video(video_file,
                larger=DEFAULT_VIDEO_WIDTH,
                smaller=DEFAULT_VIDEO_HEIGHT,
                quality=1):
    """ reduce video size """
    larger *= quality
    smaller *= quality
    try:
        random_hex = uuid4().hex
    except: #python2
        random_hex = uuid4().get_hex()
    file_temp = '/tmp/'+random_hex+'.mp4'
    try:
        #+ ' -s '+str(larger) +'x'+ str(smaller)+' '
        #+ ' -c:v libx264 -preset slow -an -b:v 370K '
        #+ ' -c:a aac -movflags +faststart '
        #+ ''' -vf "scale='min('''+str(larger) +''',iw)':'min('''+str(smaller) +''',ih)'" '''
        cmd = ('/usr/bin/ffmpeg -hide_banner -loglevel error -i '
                    + video_file
                    + ' -vf scale='+str(larger)+':-2 '
                    + file_temp)
        #print(cmd)
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


def convert_tojpeg(tempo_file):
    """ convert image to jpeg """
    try:
        img = Image.open(tempo_file)
        img = img.convert('RGBA')
        background = Image.new("RGBA", img.size, "WHITE")
        background.paste(img, (0, 0), img) 
        img = background.convert('RGB')
        img.save(tempo_file, "JPEG", optimize=True, quality=80)
    except Exception as e:
        print('ERROR: convert_tojpeg', e)
        logger.error(e)

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
    retorno = None
    # creates a temp file
    random_hex = uuid4().hex
    tempo_file = f"{TEMP_FILE_DIR}/{random_hex}"
    # Save uploaded file to temporary
    with open(tempo_file, 'wb') as temp_file:
        for chunk in file_post.chunks():
            temp_file.write(chunk)
        temp_file.close()
    extension = mimetypes.guess_extension(file_post.content_type, strict=True)
    if extension == 'jpe':
        extension = 'jpg'
    elif extension is None:
        extension = ''
    # get a md5 from the file, and this will be it's new name
    md5_hash = md5sum(tempo_file)
    filename = f"{md5_hash}{extension}"
    # rename temp with extension
    tempo_file_ext = f"{tempo_file}{extension}"
    os.rename(tempo_file, tempo_file_ext)
    tempo_file = tempo_file_ext
    # Here we have a file in /tmp/ with name md5.extension
    mime_type = file_post.content_type
    if not mime_type:
        mime_type = []

    media = Model(**extra_args)
    mime_type = file_post.content_type
    if 'image/gif' in mime_type:
        tipe = 'gif'
    elif 'image' in mime_type:
        tipe = 'image'
    elif 'video' in mime_type:
        tipe = 'video'
    elif 'audio' in mime_type:
        tipe = 'audio'
    elif 'application/octet-stream' in mime_type:
        tipe = ('gif' if check_if_img(tempo_file) else 'file')
    else:
        tipe = 'file'
    tipes_extensions = {
        'image': ['.jpg', '.jpg'],
        'gif': ['.gif', '.jpg'],
        }
    if tipe in tipes_extensions.keys():
        mainext, thumbext = tipes_extensions.get(tipe, ['.jpg', '.jpg'])
        fname_spl = filename.split('.')
        if len(fname_spl) > 0:
            first_name = fname_spl[0]
        filename = f"{first_name}{mainext}"
        thumbname = f"{first_name}{thumbext}"
    else:
        thumbname = filename
    # convert to jpe
    media.md5_hash = md5_hash
    media.content_type = mime_type
    if (('image/gif' in mime_type) or
        ('application/octet-stream' in mime_type)):
        arruma_gif(tempo_file, mime_type)
    elif 'image' in mime_type:
        convert_tojpeg(tempo_file)
    foto_file = open(tempo_file, 'rb')
    media.media_file.save(filename, File(foto_file))
    foto_file.close()
    # extract a thumbnail depending on filetype
    if tipe == 'image': # , 'gif' # we will treat gifs differently
        thumb_file = open(tempo_file, 'rb')
        media.media_thumbnail.save(thumbname, File(thumb_file))
        thumb_file.close()
        # Crop the imagem of thumbnail
        cropa_imagem(media.media_file.path, quality=2)
        cropa_imagem(media.media_thumbnail.path, quality=quality)
        convert_tojpeg(media.media_thumbnail.path)
        media.formated = True
    elif tipe == 'gif':
        media.media_thumbnail = media.media_file
        cropa_imagem(media.media_thumbnail.path, quality=1)
        convert_tojpeg(media.media_thumbnail.path)
        media.formated = True
    elif tipe == 'video':
        media.save()
        get_thumb_from_video(media)
        # Crop video in a celery task
        if hasattr(settings, 'CELERY_BROKER_URL'):
            try:
                crop_video_task.delay(media.media_file.path)
            except ConnectionRefusedError:
                logger.error("Could not connect to CELERY_BROKER_URL")
        media.formated = True
    media.save()
    # Delete temp file
    os.remove(tempo_file)
    return media

def arruma_gif(tempo_file, mime_type):
    """ fix gifs that came with mime 'application/octet-stream'
    """
    if ('application/octet-stream' in mime_type):
        # se for octet stream, tem q converter ele pra gif
        os.system('convert '+tempo_file+ ' ' + tempo_file+'.gif')
        if os.path.isfile(tempo_file+'.gif'):
            shutil.move(tempo_file+'.gif', tempo_file)

def get_thumb_from_video(video):
    """ extract thumbnail from videos.
    requires ffmpeg
    """
    random_hex = uuid4().hex
    thumbnail_temp = '/tmp/'+random_hex+'.jpg'
    cmd = ('/usr/bin/ffmpeg -hide_banner -loglevel panic -y -ss 0 -i '
                + video.media_file.path
                + ' -frames:v 1 -s 400x300 '
                + thumbnail_temp)
    os.system(cmd)
    if os.path.isfile(thumbnail_temp):
        #thumbnail
        thumb_file = open(thumbnail_temp, 'rb')
        video.media_thumbnail.save(os.path.basename(video.media_file.name), File(thumb_file))
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


def format_media(post):
    """ Format media files. 
    Resize images, extract thumbnails, and shrink videos.

    :param post: the media object to be formated.
    :type post: social_layer.mediautils.models.Media
    """
    if post.content_type:
        if 'video/' in post.content_type:
            post.formated = cropa_video(post.media_file.path,
                                        larger=wsize, smaller=hsize)
            # reconnect because we probably have a timeout
            connection.connection.close()
            connection.connection = None
            get_thumb_from_video(post)
            if post.media_thumbnail:
                convert_tojpeg(post.media_thumbnail.path)
        elif 'image/gif' in post.content_type:
            cropa_imagem(post.media_thumbnail.path, quality=1)
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
            cropa_imagem(post.media_file.path, quality=2)
            cropa_imagem(post.media_thumbnail.path, quality=1)
            convert_tojpeg(post.media_thumbnail.path)
    post.formated = True
    post.save()
