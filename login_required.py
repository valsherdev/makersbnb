from functools import wraps
from flask import session, redirect


def login_required_decorator(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):  # (arguments, keyword arguments)
        if "user_id" not in session:
            return redirect("/sessions/new")

        result = func(*args, **kwargs)
        return result

    return decorated_func
