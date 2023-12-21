from django.contrib import admin

# Register your models here.
from social_layer.comments.models import Comment, CommentSection, LikeComment

admin.site.register(Comment)
admin.site.register(CommentSection)
admin.site.register(LikeComment)
