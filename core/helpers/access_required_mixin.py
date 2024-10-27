from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect

from core.models import Notification


class AccessRequiredMixin(AccessMixin):
    required_roles = []
    """Verify that the current user is authenticated."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            logout(request)
            return redirect("login")

        if request.user.is_superuser or request.user.is_staff:
            messages.error(request, "Root user are not allowed to access the normal user views.")
            return redirect("/admin")

        if self.required_roles and request.user.role not in self.required_roles:
            messages.error(request, "You are not allowed to access this part of the system.")
            return redirect("app_dashboard")

        if notification_id := request.GET.get("from_notification"):
            try:
                notification = Notification.objects.get(id=notification_id)
                notification.unread = False
                notification.save()
            except Notification.DoesNotExist:
                pass
        return super().dispatch(request, *args, **kwargs)
