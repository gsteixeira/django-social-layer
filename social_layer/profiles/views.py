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

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, UpdateView
from django.views.generic.list import ListView

from social_layer.comments.models import Comment
from social_layer.profiles.forms import SocialProfileForm
from social_layer.profiles.models import SocialProfile
from social_layer.utils import execute_string, get_social_profile


class SetupProfileView(DetailView, UpdateView):
    template_name = "social_layer/profiles/setup_profile.html"
    delete_redirect_cookie = False
    form_class = SocialProfileForm

    def get_object(self, **kwargs):
        return get_social_profile(self.request)

    @property
    def should_redir_after(self):
        return self.request.COOKIES.get("slogin_next", None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sprofile"] = self.get_object()
        context["redir_after"] = self.should_redir_after
        return context

    def get_success_url(self):
        redir_after = self.should_redir_after
        if redir_after:
            self.delete_redirect_cookie = True
            return redir_after
        else:
            return self.get_object().get_url()

    def dispatch(self, *args, **kwargs):
        """TODO this should be a mixin"""
        alt_setup = getattr(settings, "SOCIAL_ALT_SETUP_PROFILE", None)
        if alt_setup:
            # pass an alternative function if your app needs.
            # this should return None if expects the normal behavior
            response = execute_string(alt_setup, self.request, self.get_object())
            if response:
                return response
        response = super().dispatch(*args, **kwargs)

        if self.delete_redirect_cookie:
            response.delete_cookie("slogin_next")
            self.delete_redirect_cookie = False

        return response


class ProfileView(DetailView):
    template_name = "social_layer/profiles/profile.html"
    model = SocialProfile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sprofile = self.get_object()
        context["sprofile"] = sprofile
        context["comments"] = Comment.objects.filter(author=sprofile)
        if getattr(settings, "SOCIAL_PROFILE_CONTEXT", None):
            extra = execute_string(settings.SOCIAL_PROFILE_CONTEXT, sprofile)
            context.update(extra)
        return context

    def dispatch(self, *args, **kwargs):
        alt_view = getattr(settings, "SOCIAL_ALT_VIEW_PROFILE", None)
        if alt_view:
            # pass an alternative function if your app needs.
            # this should return None if excpets the normal behavior
            response = execute_string(alt_view, self.request, self.get_object())
            if response:
                return response
        return super().dispatch(*args, **kwargs)


def social_login(request):
    """
    The Implementing application MUST take care of authentication.
    Any action that requires a social login must be redirected here.
    It will redirect the user to the 'social' login page.
    This url is defined by: settings.SOCIAL_VISITOR_LOGIN
    """
    next_url = request.GET.get("next", "/")
    resp = redirect("/" + settings.SOCIAL_VISITOR_LOGIN)
    resp.set_cookie("slogin_next", next_url, expires=360)
    return resp


class ListProfilesView(ListView):
    model = SocialProfile
    paginate_by = 20
    template_name = "social_layer/profiles/list_profiles.html"
    ordering = ["-last_actv"]


class DeleteProfilePictureView(DeleteView):
    success_url = reverse_lazy("social_layer:profiles:setup_profile")

    def get_object(self):
        return get_social_profile(self.request).picture()
