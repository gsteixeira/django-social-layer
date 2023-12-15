# This file is part of django-social-layer
#
#    django-social-layer is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    django-social-layer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with django-social-layer. If not, see <http://www.gnu.org/licenses/>.


from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, FormView

from social_layer.comments.forms import CommentForm
from social_layer.comments.models import Comment, CommentSection, LikeComment
from social_layer.utils import get_social_profile


class CommentSectionView(DetailView, CreateView, FormView):
    """renders a full comment section
    and also stores a new comment
    """

    model = CommentSection
    form_class = CommentForm
    template_name = "social_layer/comments/comments_view.html"

    def get_success_url(self):
        return f"{self.object.get_absolute_url()}?show-comments"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["comment_section"] = self.get_object()
        kwargs["request"] = self.request
        return kwargs


class ReplyCommentView(FormView, CreateView):
    model = Comment
    form_class = CommentForm
    http_method_names = ["post"]

    def get_success_url(self):
        return f"{self.object.comment_section.get_absolute_url()}?show-comments#comment_{self.object.pk}"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        reply_to = self.get_object()
        kwargs["request"] = self.request
        kwargs["reply_to"] = reply_to
        kwargs["comment_section"] = reply_to.comment_section
        return kwargs


class DeleteCommentView(DeleteView):
    model = Comment

    def get_success_url(self):
        return self.object.comment_section.get_url()

    def get_object(self):
        instance = super().get_object()
        sprofile = get_social_profile(self.request)
        section = instance.comment_section
        if not (
            sprofile == instance.author
            or section.owner_can_delete
            and sprofile == section.owner
            or self.request.user.is_superuser
        ):
            raise PermissionDenied()

        return instance


@login_required
def like_comment(request, pk, didlike):
    """when someone likes a comment"""
    return like_action(request, pk, didlike, Comment, LikeComment)


@login_required
def like_action(request, pk, didlike, Model, LikeModel):
    """when someone likes a comment"""
    instance = get_object_or_404(Model, pk=pk)
    is_comment_section = Model == CommentSection
    lookup = "comment_section" if is_comment_section else "comment"

    liked, new = LikeModel.objects.get_or_create(
        user=request.user, **{lookup: instance}
    )
    liked.like = bool(didlike == "like")
    liked.save()
    instance.updt_counters()
    instance.refresh_from_db()

    if is_comment_section:
        section = instance
    else:
        section = instance.comment_section

    if "ajx" in request.GET.keys():
        if liked.like:
            count = instance.count_likes
        else:
            count = instance.count_dislikes
        return HttpResponse(count, content_type="text/txt")
    else:
        return redirect(section.get_url())
