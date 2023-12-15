from django import forms
from django.utils.translation import gettext as _

from social_layer.comments.models import Comment
from social_layer.comments.utils import notify_parties
from social_layer.utils import get_social_profile


class CommentForm(forms.ModelForm):
    text = forms.CharField(
        required=False,
        label=_("Leave a comment"),
        widget=forms.Textarea(attrs={"class": "comment-textarea", "rows": 4}),
    )
    reply_to = None

    class Meta:
        model = Comment
        fields = [
            "text",
        ]

    def __init__(self, request, comment_section, reply_to=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.comment_section = comment_section
        self.request = request
        self.reply_to = reply_to

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.author = get_social_profile(self.request)
        instance.comment_section = self.comment_section
        instance.reply_to = self.reply_to
        if commit:
            instance.save()
            self.dispatch_notifications(instance)
        return instance

    def dispatch_notifications(self, comment):
        parties = []
        if self.comment_section.owner:
            parties.append(self.comment_section.owner.user)

        if self.reply_to:
            jump_to = self.reply_to.pk
            parties.append(self.reply_to.author.user)
        else:
            jump_to = comment.pk
            parties.append(comment.author.user)

        if jump_to is not None:
            comment_url = (
                f"{self.comment_section.get_url()}?show-comments#comment_{jump_to}"
            )
            message_list = [
                comment.author.nick,
                '<a href="{}" class="alink">'.format(comment_url),
                _("wrote a comment"),
                "</a>",
            ]
            notif_text = " ".join(message_list)
            notify_parties(parties, notif_text, do_not=[self.request.user])
