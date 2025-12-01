current_user_context = {"user_name": "guest_user", "full_name": "Guest", "role": "guest"}


def set_current_user(user_name: str | None, full_name: str | None = None, role: str | None = None):
    current_user_context["user_name"] = user_name or "guest_user"
    current_user_context["full_name"] = full_name or user_name or "Guest"
    current_user_context["role"] = role or current_user_context.get("role") or "guest"


def identify_user() -> dict:
    """Return current user info (username, full name, role) from in-memory context.

    DB refresh is handled upstream (see user_context.py) to avoid async-in-sync issues.
    """
    return {
        "status": "success",
        "user_name": current_user_context.get("user_name", "guest_user"),
        "full_name": current_user_context.get("full_name", "Guest"),
        "role": current_user_context.get("role", "guest"),
    }
