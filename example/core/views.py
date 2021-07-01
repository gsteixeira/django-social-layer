from django.shortcuts import render
from social_layer.models import CommentSection
# Create your views here.

def home_page(request):
    """  """
    comments, new = CommentSection.objects.get_or_create(url=request.path)
    data = {'comment_section': comments,}
    return render(request, 'example/home_page.html', data)


def second_page(request):
    comments, new = CommentSection.objects.get_or_create(url=request.path)
    data = {'comment_section': comments,}
    return render(request, 'example/second_page.html', data)
