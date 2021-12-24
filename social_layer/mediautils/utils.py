# -*- coding: utf-8 -*-
import json
from uuid import uuid4
import mimetypes
import cv2
import os
import sys
import shutil
import random
from PIL import Image, ImageDraw, ImageFont

from django.conf import settings
import logging
import hashlib
import traceback

from django.core.files.base import ContentFile
from django.core.files import File
from social_layer.mediautils.models import Media

TEMP_FILE_DIR = '/tmp/'
logger = logging.getLogger(__name__)

def cropa_imagem(img_file, larger=480, smaller=360, quality=1):#3x4 # 
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

def cropa_video(video_file, larger=320, smaller=240, quality=1):
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

# 65536
def md5sum(filename, blocksize=65536):
    """ Get md5sum from file """
    hashe = hashlib.md5()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            hashe.update(block)
        f.close()
    return hashe.hexdigest()


def convert_tojpeg(arquivo_temp):
    """ convert image to jpeg """
    try:
        img = Image.open(arquivo_temp)
        img = img.convert('RGBA')
        background = Image.new("RGBA", img.size, "WHITE")
        background.paste(img, (0, 0), img) 
        img = background.convert('RGB')
        img.save(arquivo_temp, "JPEG", optimize=True, quality=80)
    except Exception as e:
        print('ERROR: convert_tojpeg', e)
        logger.error(e)

def convert_towebp(arquivo_temp):
    """ convert image to webp
    requires libwebp-dev
    """
    try:
        img = Image.open(arquivo_temp)
        img = img.convert('RGBA')
        background = Image.new("RGBA", img.size, "WHITE")
        background.paste(img, (0, 0), img) 
        img = background.convert('RGB')
        img.save(arquivo_temp, "WEBP")
    except Exception as e:
        logger.error(e)

def handle_upload_file(file_post=None,
                     Model=None,
                     #description=None,
                     #title=None,
                     extra_args={},
                     #thread=None,
                     #postage_type=None,
                     quality=1):
    """ handle a file upload """
    retorno = None
    # creates a temp file
    try:
        random_hex = uuid4().hex
    except: #python2
        random_hex = uuid4().get_hex()
    # Save temp file in /tmp/
    arquivo_temp = TEMP_FILE_DIR + random_hex
    with open(arquivo_temp, 'wb') as temp_file:
        for chunk in file_post.chunks():
            temp_file.write(chunk)
        temp_file.close()
    extension = mimetypes.guess_extension(file_post.content_type, strict=True)
    if extension == 'jpe':
        # guess_extension eh bugado
        extension = 'jpg'
    if not extension:
        extension = ''
    # get a md5 from the file, and this will be it's new name
    md5_hash = md5sum(arquivo_temp)
    filename = ''.join([md5_hash, extension])
    # rename temp with extension
    arquivo_temp_ext = ''.join([arquivo_temp, extension])
    os.rename(arquivo_temp, arquivo_temp_ext)
    arquivo_temp = arquivo_temp_ext
    # Here we have a file in /tmp/ with name md5.extension
    mime_type = file_post.content_type
    if not mime_type:
        mime_type = []
    retorno = handle_generic_file(arquivo_temp,
                                file_post,
                                filename,
                                quality=quality,
                                Model=Model,
                                extra_args=extra_args,
                                md5_hash=md5_hash)
    return retorno

def handle_generic_file(arquivo_temp,
                        file_post,
                        filename,
                        quality=1,
                        Model=Media,
                        extra_args={},
                        md5_hash=None):
    """ handle a generic file uplod and format it accordint to it's needs """
    media = Model(**extra_args)
    mime_type = file_post.content_type
    if 'image/gif' in mime_type:
        tipo = 'gif'
    elif 'image' in mime_type:
        tipo = 'image'
    elif 'video' in mime_type:
        tipo = 'video'
    elif 'audio' in mime_type:
        tipo = 'audio'
    elif 'application/octet-stream' in mime_type:
        tipo = 'gif'
    else:
        tipo = 'file'
    tipos_extensions = {
        'image': ['.jpg', '.webp'],
        'gif': ['.gif', '.webp'],
        }
    if tipo in tipos_extensions.keys():
        mainext, thumbext = tipos_extensions.get(tipo, ['.jpg', '.webp'])
        fname_spl = filename.split('.')
        if len(fname_spl) > 0:
            first_name = fname_spl[0]
            filename = first_name+mainext
            thumbname = first_name+thumbext
        else:
            filename = filename+mainext
            thumbname = filename+thumbext
    else:
        thumbname = filename
    # convert to jpe
    media.md5_hash = md5_hash
    media.content_type = mime_type
    if (('image/gif' in mime_type) or
        ('application/octet-stream' in mime_type)):
        arruma_gif(arquivo_temp, mime_type)
    elif 'image' in mime_type:
        convert_tojpeg(arquivo_temp)
    foto_file = open(arquivo_temp, 'rb')
    media.media_file.save(filename, File(foto_file))
    foto_file.close()
    # extract a thumbnail depending on filetype
    if tipo == 'image': # , 'gif' # we will treat gifs differently
        thumb_file = open(arquivo_temp, 'rb')
        media.media_thumbnail.save(thumbname, File(thumb_file))
        thumb_file.close()
        # Crop the imagem of thumbnail
        cropa_imagem(media.media_thumbnail.path, quality=quality)
        convert_towebp(media.media_thumbnail.path)
    elif tipo == 'gif':
        media.media_thumbnail = media.media_file
    elif tipo == 'video':
        media.save()
        get_thumb_from_video(media)
    media.save()
    # Delete temp file
    os.remove(arquivo_temp)
    return media

def arruma_gif(arquivo_temp, mime_type):
    """ fix gifs that came with mime 'application/octet-stream'
    """
    if ('application/octet-stream' in mime_type):
        # se for octet stream, tem q converter ele pra gif
        os.system('convert '+arquivo_temp+ ' ' + arquivo_temp+'.gif')
        if os.path.isfile(arquivo_temp+'.gif'):
            shutil.move(arquivo_temp+'.gif', arquivo_temp)

def get_thumb_from_video(video):
    """ extract thumbnail from videos.
    requires ffmpeg
    """
    try:
        random_hex = uuid4().hex
    except: #python2
        random_hex = uuid4().get_hex()
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
