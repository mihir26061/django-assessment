import redis

r = redis.Redis()
RATE_LIMIT = 200


def allow_request():
    key = "email_tokens"

    tokens = r.get(key)

    if tokens is None:
        r.set(key, RATE_LIMIT, ex=60)
        return True

    if int(tokens) > 0:
        r.decr(key)
        return True

    return False