from django.conf import settings


SOCIAL_ALT_SETUP_PROFILE = getattr(settings, 'SOCIAL_ALT_SETUP_PROFILE', None)
SOCIAL_ALT_VIEW_PROFILE = getattr(settings, 'SOCIAL_ALT_VIEW_PROFILE', None)
