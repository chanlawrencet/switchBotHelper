import argparse
import hashlib
import hmac
import os
import time

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
    sig = hmac.new(
        LINK_SIGNING_SECRET.encode("utf-8"),
        str(exp).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    print(f"{BASE_URL}?exp={exp}&sig={sig}")


if __name__ == "__main__":
    main()
