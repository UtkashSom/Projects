import os
import json
import redis
from flask import current_app

_client = None
REDIS_URL = "redis://localhost:6379/0"

def get_client():
    global _client
    if _client is not None:
        return _client
    url = None
    try:
        app = current_app
        url = app.config.get("REDIS_URL")
    except Exception:
        pass
    if not url:
        url = os.getenv("REDIS_URL")
    if not url:
        url = "redis://localhost:6379/0"
    print("Redis URL used:", url, flush=True)
    _client = redis.Redis.from_url(url, decode_responses=True)
    try:
        pong = _client.ping()
        print("Redis ping:", pong, flush=True)
    except Exception as e:
        print("Redis ping failed:", e, flush=True)
    return _client


def pull_cache(key):
    try:
        r = get_client()
        raw = r.get(key)
        print("Redis GET", key, "->", raw, flush=True)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as e:
        print("Redis pull_cache error:", e, flush=True)
        return None

def store_cache(key, value, ttl=60):
    try:
        r = get_client()
        data = json.dumps(value)
        r.setex(key, ttl, data)
        print("Redis SETEX", key, "ttl", ttl, flush=True)
    except Exception as e:
        print("Redis store_cache error:", e, flush=True)

def reset_lot_cache():
    try:
        r = get_client()
        for pattern in ["user:available_lots", "admin:lots:*"]:
            for k in r.scan_iter(pattern):
                r.delete(k)
                print("Redis DEL", k, flush=True)
    except Exception as e:
        print("Redis reset_lot_cache error:", e, flush=True)
