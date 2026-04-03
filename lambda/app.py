import base64
import datetime
import html as html_lib
import hashlib
import hmac
import json
import os
import time
import uuid
from zoneinfo import ZoneInfo

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


def format_expiration(exp: str | None) -> str:
    if not exp:
        return "Unknown"

    try:
        exp_int = int(exp)
    except ValueError:
        return "Unknown"

    expires_at = datetime.datetime.fromtimestamp(exp_int, tz=datetime.UTC)
    return expires_at.strftime("%Y-%m-%d %H:%M:%S UTC")


def format_expiration_est(exp: str | None) -> str:
    if not exp:
        return "Unknown"

    try:
        exp_int = int(exp)
    except ValueError:
        return "Unknown"

    expires_at = datetime.datetime.fromtimestamp(
        exp_int,
        tz=ZoneInfo("America/New_York"),
    )
    return expires_at.strftime("%Y-%m-%d %I:%M:%S %p %Z")


def success_page(exp: str | None) -> str:
    expires_at_utc = html_lib.escape(format_expiration(exp))
    expires_at_est = html_lib.escape(format_expiration_est(exp))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Tap To Unlock Front Door</title>
  <style>
    :root {{
      color-scheme: light;
      --bg-start: #f3efe5;
      --bg-end: #dfe7f2;
      --panel: rgba(255, 255, 255, 0.82);
      --text: #172033;
      --muted: #5a6577;
      --accent: #1e7a5f;
      --accent-soft: rgba(30, 122, 95, 0.12);
      --border: rgba(23, 32, 51, 0.08);
      --shadow: 0 24px 60px rgba(23, 32, 51, 0.16);
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 24px;
      font-family: "Avenir Next", Avenir, "Segoe UI", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(255, 255, 255, 0.72), transparent 32%),
        linear-gradient(135deg, var(--bg-start), var(--bg-end));
    }}

    main {{
      width: min(100%, 560px);
      padding: 36px 32px;
      border: 1px solid var(--border);
      border-radius: 28px;
      background: var(--panel);
      box-shadow: var(--shadow);
      backdrop-filter: blur(14px);
    }}

    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 8px 14px;
      border-radius: 999px;
      font-size: 14px;
      font-weight: 600;
      color: var(--accent);
      background: var(--accent-soft);
    }}

    .dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--accent);
      box-shadow: 0 0 0 6px rgba(30, 122, 95, 0.12);
    }}

    h1 {{
      margin: 22px 0 12px;
      font-size: clamp(32px, 6vw, 44px);
      line-height: 1.02;
      letter-spacing: -0.04em;
    }}

    p {{
      margin: 0;
      font-size: 18px;
      line-height: 1.6;
      color: var(--muted);
    }}

    .meta {{
      margin-top: 26px;
      padding: 18px 20px;
      border-radius: 20px;
      background: rgba(255, 255, 255, 0.72);
      border: 1px solid rgba(23, 32, 51, 0.06);
    }}

    .meta strong {{
      display: block;
      margin-bottom: 6px;
      font-size: 12px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
    }}

    .meta span {{
      font-size: 17px;
      font-weight: 600;
      color: var(--text);
    }}

    .meta small {{
      display: block;
      margin-top: 8px;
      font-size: 14px;
      color: var(--muted);
    }}
  </style>
</head>
<body>
  <main>
    <div class="badge"><span class="dot"></span>Signal delivered</div>
    <h1>Tap to unlock the front door</h1>
    <p>
      The front door should now be unlocking. It may take a few moments to
      open. If nothing happens, refresh this page and try again.
    </p>
    <section class="meta">
      <strong>Link Expires</strong>
      <span>{expires_at_est}</span>
      <small>{expires_at_utc}</small>
    </section>
  </main>
</body>
</html>"""


def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    exp = params.get("exp")
    sig = params.get("sig")

    if not verify_link(exp, sig):
        return html(403, "<h1>Link invalid or expired</h1>")

    try:
        result = press_bot()
        if result.get("statusCode") == 100:
            return html(200, success_page(exp))
        return html(
            502,
            f"<h1>SwitchBot error</h1><pre>{json.dumps(result, indent=2)}</pre>",
        )
    except Exception as e:
        return html(500, f"<h1>Error</h1><pre>{str(e)}</pre>")
