from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class OwnedByUser(LoginRequiredMixin):
    """Ensure that object belongs to the logged user"""

    def get_object(self):
        instance = super().get_object()
        if instance.owner.user != self.request.user:
            raise PermissionDenied()
        return instance
