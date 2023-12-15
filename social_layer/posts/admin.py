from django.contrib import admin

from social_layer.posts.models import Post, PostMedia

admin.site.register(Post)
admin.site.register(PostMedia)
