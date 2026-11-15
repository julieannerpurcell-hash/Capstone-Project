from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect


class EmployeeProfileMiddleware:
    """Stops logged-in accounts that have no Employee profile from crashing the portal.

    Example: the Django superuser. It can use /admin/, but the portal pages need an
    Employee profile (with a role) to know which dashboard to show.
    """

    EXEMPT_PREFIXES = ("/admin/", "/static/")
    EXEMPT_PATHS = ("/", "/logout/")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if (
            user.is_authenticated
            and request.path not in self.EXEMPT_PATHS
            and not request.path.startswith(self.EXEMPT_PREFIXES)
            and getattr(user, "employee_profile", None) is None
        ):
            if user.is_superuser:
                messages.error(
                    request,
                    "This account has no Employee profile yet. Add one in the admin "
                    "panel (Employees > Add) and give it a role to use the portal pages.",
                )
                return redirect("/admin/")
            logout(request)
            return redirect("login")
        return self.get_response(request)