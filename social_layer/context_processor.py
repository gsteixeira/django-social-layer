from social_layer.models import Notification
from social_layer.views.notifications import get_notifications

def social_layer_data(request):
    notifs = get_notifications(request)
    data = {
        'notif_count': notifs.count(),
        }
    return data

