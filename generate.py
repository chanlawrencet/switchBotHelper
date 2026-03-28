import hashlib
import hmac
import os
import time

BASE_URL = os.environ["BASE_URL"]
LINK_SIGNING_SECRET = os.environ["LINK_SIGNING_SECRET"]
TTL_SECONDS = int(os.environ.get("TTL_SECONDS", "900"))

exp = int(time.time()) + TTL_SECONDS
sig = hmac.new(
    LINK_SIGNING_SECRET.encode("utf-8"),
    str(exp).encode("utf-8"),
    hashlib.sha256,
).hexdigest()

print(f"{BASE_URL}?exp={exp}&sig={sig}")