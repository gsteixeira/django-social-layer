from django import forms
from django.utils.translation import gettext as _

from social_layer.mediautils.utils import handle_upload_file
from social_layer.profiles.models import SocialProfile, SocialProfilePhoto


class SocialProfileForm(forms.ModelForm):
    nick = forms.CharField(label=_("Nick name"))
    phrase = forms.CharField(
        required=False,
        label=_("Bio"),
        widget=forms.Textarea(attrs={"class": "comment-textarea", "rows": 4}),
    )
    picture = forms.FileField(required=False, label=_("Select a picture"))

    class Meta:
        model = SocialProfile
        fields = [
            "nick",
            "phrase",
            "picture",
        ]

    def save(self, commit=True):
        """Save profile and if media file is sent along, save it as a media obj"""
        instance = super().save(commit=False)
        if commit:
            instance.save()
            if self.cleaned_data["picture"]:
                handle_upload_file(
                    file_post=self.cleaned_data["picture"],
                    quality=1,
                    Model=SocialProfilePhoto,
                    extra_args={"profile": self.instance},
                )
                # TODO should delete old photos

        return instance

        # if foto:
        # oldies = SocialProfilePhoto.objects.exclude(pk=foto.pk).filter(
        # profile=sprofile
        # )
        # oldies.delete()
