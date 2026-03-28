import base64
import hashlib
import hmac
import json
import os
import time
import uuid

import requests

API_BASE = "https://api.switch-bot.com"

SWITCHBOT_TOKEN = os.environ["SWITCHBOT_TOKEN"]
SWITCHBOT_SECRET = os.environ["SWITCHBOT_SECRET"]
LINK_SIGNING_SECRET = os.environ["LINK_SIGNING_SECRET"]
DEVICE_ID = os.environ.get("DEVICE_ID", "CE2A80866523")
LINK_TTL_SECONDS = int(os.environ.get("LINK_TTL_SECONDS", "900"))


def make_switchbot_headers(token: str, secret: str) -> dict:
    nonce = str(uuid.uuid4())
    t = str(int(time.time() * 1000))
    message = f"{token}{t}{nonce}".encode("utf-8")
    sign = base64.b64encode(
        hmac.new(secret.encode("utf-8"), message, hashlib.sha256).digest()
    ).decode("utf-8")

    return {
        "Authorization": token,
        "sign": sign,
        "nonce": nonce,
        "t": t,
        "Content-Type": "application/json",
        "charset": "utf8",
    }


def verify_link(exp: str, sig: str) -> bool:
    if not exp or not sig:
        return False

    try:
        exp_int = int(exp)
    except ValueError:
        return False

    if int(time.time()) > exp_int:
        return False

    expected = hmac.new(
        LINK_SIGNING_SECRET.encode("utf-8"),
        exp.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, sig)


def press_bot() -> dict:
    url = f"{API_BASE}/v1.1/devices/{DEVICE_ID}/commands"
    headers = make_switchbot_headers(SWITCHBOT_TOKEN, SWITCHBOT_SECRET)
    payload = {
        "command": "press",
        "parameter": "default",
        "commandType": "command",
    }

    response = requests.post(url, headers=headers, json=payload, timeout=15)
    response.raise_for_status()
    return response.json()


def html(status_code: int, body: str) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "text/html; charset=utf-8"},
        "body": body,
    }


def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    exp = params.get("exp")
    sig = params.get("sig")

    if not verify_link(exp, sig):
      return html(403, "<h1>Link invalid or expired</h1>")

    try:
        result = press_bot()
        if result.get("statusCode") == 100:
            return html(
                200,
                "<h1>Door signal sent</h1><p>You can close this page.</p>",
            )
        return html(
            502,
            f"<h1>SwitchBot error</h1><pre>{json.dumps(result, indent=2)}</pre>",
        )
    except Exception as e:
        return html(500, f"<h1>Error</h1><pre>{str(e)}</pre>")