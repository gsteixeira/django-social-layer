from django.shortcuts import render
from social_layer.models import CommentSection
# Create your views here.

def home_page(request):
    """ a sample homepage with comment section """
    comments, new = CommentSection.objects.get_or_create(url=request.path)
    return render(request,
                  'example/home_page.html',
                  {'comment_section': comments,})


def second_page(request):
    """ a sample secondary page with comment section """
    comments, new = CommentSection.objects.get_or_create(url=request.path)
    return render(request,
                  'example/second_page.html',
                  {'comment_section': comments,})
