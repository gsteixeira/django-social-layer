from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from social_layer.comments.models import CommentSection

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

def register(request):
    """ register a new user """
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if not User.objects.filter(username__iexact=username).exists():
            user = User.objects.create(username=username)
            user.set_password(password)
            user.save()
            usr = authenticate(username=username, password=password)
            if usr is not None:
                login(request, usr)
                return redirect('/')
            else:
                error = "could not authenticate"
        else:
            error = "user already exists"
    data = {
        'error': error,
        }
    return render(request, 'example/register.html', data)

