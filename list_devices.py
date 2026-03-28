import base64
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid


API_BASE = "https://api.switch-bot.com"


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


def get_required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        print(f"Missing required environment variable: {name}", file=sys.stderr)
        sys.exit(1)
    return value


def main() -> int:
    token = get_required_env("SWITCHBOT_TOKEN")
    secret = get_required_env("SWITCHBOT_SECRET")

    request = urllib.request.Request(
        f"{API_BASE}/v1.1/devices",
        headers=make_switchbot_headers(token, secret),
        method="GET",
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        print(f"SwitchBot API request failed: HTTP {exc.code}", file=sys.stderr)
        print(error_body, file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"SwitchBot API request failed: {exc.reason}", file=sys.stderr)
        return 1

    payload = json.loads(body)
    device_list = payload.get("body", {}).get("deviceList", [])
    infrared_list = payload.get("body", {}).get("infraredRemoteList", [])

    print("Devices:")
    if device_list:
        print(json.dumps(device_list, indent=2))
    else:
        print("[]")

    print("\nInfrared Remotes:")
    if infrared_list:
        print(json.dumps(infrared_list, indent=2))
    else:
        print("[]")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
