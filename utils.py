def is_user_allowed(username):
    from config import ALLOWED_USERS
    return username in ALLOWED_USERS or not ALLOWED_USERS