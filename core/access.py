from functools import wraps

from django.contrib.auth import logout
from django.shortcuts import redirect


def get_role(user):
    """Return 'employee', 'manager', 'admin', or None if the user has no Employee profile."""
    if not user.is_authenticated:
        return None
    profile = getattr(user, "employee_profile", None)
    return profile.role if profile else None


def role_required(*roles):
    """Only let logged-in users with one of these roles into a page.

    Everyone else is sent back to the page that matches their own role.
    """
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            role = get_role(request.user)
            if role in roles:
                return view(request, *args, **kwargs)
            if not request.user.is_authenticated:
                return redirect("login")
            if role is None:
                logout(request)
                return redirect("login")
            return redirect({"employee": "employee_dashboard",
                             "manager": "manager_dashboard",
                             "admin": "admin_dashboard"}[role])
        return wrapper
    return decorator