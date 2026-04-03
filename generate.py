import argparse
import hashlib
import hmac
import os
import time
import urllib.parse

BASE_URL = os.environ["BASE_URL"]
LINK_SIGNING_SECRET = os.environ["LINK_SIGNING_SECRET"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a signed SwitchBot visitor link."
    )
    ttl_group = parser.add_mutually_exclusive_group()
    ttl_group.add_argument(
        "--hours",
        type=float,
        help="Set the link expiration window in hours.",
    )
    ttl_group.add_argument(
        "--days",
        type=float,
        help="Set the link expiration window in days.",
    )
    ttl_group.add_argument(
        "--weeks",
        type=float,
        help="Set the link expiration window in weeks.",
    )
    parser.add_argument(
        "--note",
        help="Optional purpose or note to embed in the signed link.",
    )
    return parser.parse_args()


def resolve_ttl_seconds(args: argparse.Namespace) -> int:
    if args.hours is not None:
        return int(args.hours * 60 * 60)
    if args.days is not None:
        return int(args.days * 24 * 60 * 60)
    if args.weeks is not None:
        return int(args.weeks * 7 * 24 * 60 * 60)

    env_ttl = os.environ.get("TTL_SECONDS") or os.environ.get("LINK_TTL_SECONDS")
    return int(env_ttl or "900")


def main() -> None:
    args = parse_args()
    ttl_seconds = resolve_ttl_seconds(args)
    exp = int(time.time()) + ttl_seconds
    note = args.note or ""
    signed_payload = f"{exp}\n{note}"
    sig = hmac.new(
        LINK_SIGNING_SECRET.encode("utf-8"),
        signed_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    params = {"exp": str(exp), "sig": sig}
    if note:
        params["note"] = note
    query = urllib.parse.urlencode(params)

    print(f"{BASE_URL}?{query}")


if __name__ == "__main__":
    main()
