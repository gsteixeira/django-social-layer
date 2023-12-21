from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse

from social_layer.mediautils.models import Media
from social_layer.mediautils.utils import rotate_image


@login_required
def del_photo(request, pk, MediaModel=Media):
    """deletes an image
    To be used wraped in another view
    """
    try:
        media = MediaModel.objects.get(id=pk, owner__user=request.user)
    except MediaModel.DoesNotExist:
        raise Http404()
    media.delete()
    return redirect(reverse("root"))


@login_required
def mediautils_rotate_photo(request, pk, direct="left", MediaModel=Media):
    """Rotate an image
    To be used wraped in another view
    """
    try:
        media = MediaModel.objects.get(id=pk, owner__user=request.user)
    except MediaModel.DoesNotExist:
        raise Http404()
    for field in ["media_file", "media_thumbnail"]:
        file_field = getattr(media, field, None)
        img_file = file_field.path
        rotate_image(img_file, direct)
    return media
