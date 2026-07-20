from functools import wraps
from flask_jwt_extended import get_jwt
from flask import current_app as app
import pytz
from datetime import datetime
import redis
import os
import logging

logger = logging.getLogger(__name__)


def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if "role" not in claims or claims["role"] != role:
                return (
                    {"message": "You don't have the required permissions"},
                    403,
                )
            return fn(*args, **kwargs)

        return decorator

    return wrapper


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


def IndianTimeZone():
    IST = pytz.timezone("Asia/Kolkata")
    return datetime.now(IST)


def convert_to_ist(utc_dt):
    if not utc_dt:
        return None

    if utc_dt.tzinfo is None:
        utc_dt = pytz.utc.localize(utc_dt)

    IST = pytz.timezone("Asia/Kolkata")
    return utc_dt.astimezone(IST)


def format_ist_datetime(dt):
    if not dt:
        return None
    return dt.strftime("%Y-%m-%d %H:%M:%S %Z")


class EmailRateLimiter:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=0,
        )
        self.key_prefix = "email_rate_limit"
        self.max_emails = int(os.getenv("MAX_EMAILS_PER_DAY", 100))
        self.window_seconds = 86400

    def can_send_email(self):
        current_count = self.redis_client.get(self.key_prefix)
        if current_count is None:
            return True
        return int(current_count) < self.max_emails

    def increment_count(self):
        current_count = self.redis_client.get(self.key_prefix)
        if current_count is None:
            self.redis_client.setex(self.key_prefix, self.window_seconds, 1)
        else:
            self.redis_client.incr(self.key_prefix)

    def get_remaining_emails(self):
        current_count = self.redis_client.get(self.key_prefix)
        if current_count is None:
            return self.max_emails
        return max(0, self.max_emails - int(current_count))
