from django.contrib import admin

from social_layer.profiles.models import SocialProfile, SocialProfilePhoto

admin.site.register(SocialProfile)
admin.site.register(SocialProfilePhoto)
