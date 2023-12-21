from social_layer.notifications.models import Notification


def notify_parties(parties, text, do_not=[]):
    """Creates a notification to people interested on it"""
    for party in set(parties):
        if party and party not in do_not:
            Notification.objects.create(to=party, text=text)
