from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, FormView
from django.views.generic.list import ListView
from infscroll.utils import get_pagination
from infscroll.views import more_items

from social_layer.comments.models import CommentSection, LikePost
from social_layer.comments.views import like_action
from social_layer.posts.forms import PostForm
from social_layer.posts.mixins import OwnedByUser
from social_layer.posts.models import Post


class PostView(LoginRequiredMixin, CreateView, FormView):
    """manages the creation of new user generated content"""

    template_name = "social_layer/posts/new_post.html"
    form_class = PostForm

    def form_valid(self, form):
        form.instance.owner = getattr(self.request.user, "socialprofile", None)
        return super().form_valid(form)


class PostDetailView(DetailView):
    template_name = "social_layer/posts/view_post.html"
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["commentsection"] = self.get_object().comments
        return context


class DeletePost(OwnedByUser, DeleteView):
    model = Post
    success_url = reverse_lazy("social_layer:posts:posts_feed")


class PostsFeedView(ListView, FormView):
    template_name = "social_layer/posts/posts_feed.html"
    model = Post
    form_class = PostForm
    ordering = ['-date_time']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["more_posts_url"] = reverse("social_layer:posts:more_posts")
        paginated_data = get_pagination(self.request, context["object_list"])
        context.update(paginated_data)
        return context


def more_posts(request):
    """dynamic load posts using the django-infinite-scroll module."""
    post_list = Post.objects.all().order_by("-id")
    return more_items(request, post_list, template="social_layer/posts/more_posts.html")


@login_required
def like_post(request, pk, didlike):
    """when someone likes a comment_section (aka a post)"""
    return like_action(request, pk, didlike, CommentSection, LikePost)

