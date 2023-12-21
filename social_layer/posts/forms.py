from django import forms
from django.conf import settings
from django.utils.translation import gettext as _

from social_layer.mediautils.utils import handle_upload_file
from social_layer.posts.models import Post, PostMedia


class PostForm(forms.ModelForm):
    text = forms.CharField(
        required=False,
        label=_("Text"),
        widget=forms.Textarea(attrs={"class": "comment-textarea", "rows": 4}),
    )
    allow_media = getattr(settings, "SOCIAL_ALLOW_MEDIA_POSTS", True)

    class Meta:
        model = Post
        fields = [
            "text",
        ]

    def __init__(self, *args, **kwargs):
        """PostForm __init__ method
        decides if should show "media" field, based on SOCIAL_ALLOW_MEDIA_POSTS
        """
        super(PostForm, self).__init__(*args, **kwargs)
        if self.allow_media:
            self.fields["media"] = forms.FileField(required=False)

    def clean_text(self):
        """if there is no text, we must at least have a file.
        Otherwise is not valid.
        """
        if not self.cleaned_data["text"] and len(self.files) < 1:
            raise forms.ValidationError(_("Say something"))
        return self.cleaned_data["text"]

    def clean_media(self):
        """raise invalid if media is not allowed
        But this will probably not fire up because when so, the field
            will be disabled
        """
        if not self.allow_media:
            raise forms.ValidationError(_("Posting media is not allowed!"))
        return self.cleaned_data["media"]

    def save(self, commit=True):
        """Save post and if media file is sent along, save it as a media obj"""
        instance = super().save(commit=False)
        if commit:
            instance.save()
            if self.allow_media and self.cleaned_data["media"]:
                handle_upload_file(
                    file_post=self.cleaned_data["media"],
                    quality=1,
                    Model=PostMedia,
                    extra_args={"post": self.instance},
                )

        return instance
