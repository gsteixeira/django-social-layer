from django.conf import settings


SOCIAL_ALT_SETUP_PROFILE = getattr(settings, 'SOCIAL_ALT_SETUP_PROFILE', None)
SOCIAL_ALT_VIEW_PROFILE = getattr(settings, 'SOCIAL_ALT_VIEW_PROFILE', None)
MAX_FEATURED_COMMENTS = getattr(settings, 'SOCIAL_MAX_FEATURED_COMMENTS', 3)
