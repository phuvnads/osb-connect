"""Publish posts through each platform's official API.

Only official APIs are used, with tokens the user creates for their own Page.
No browser automation, no fake accounts.

Supported now:
- facebook: Facebook Page posts via the Graph API

Every publisher supports dry_run=True, which prints what would be sent.
"""

from __future__ import annotations

import os

GRAPH_VERSION = "v21.0"


class PublishError(RuntimeError):
    pass


def publish_facebook(text: str, dry_run: bool = True) -> str:
    """Post text to a Facebook Page. Needs FB_PAGE_ID and FB_PAGE_TOKEN."""
    page_id = os.environ.get("FB_PAGE_ID", "")
    token = os.environ.get("FB_PAGE_TOKEN", "")
    if dry_run:
        return f"[dry-run] would post {len(text)} characters to Facebook Page {page_id or '<FB_PAGE_ID>'}"
    if not page_id or not token:
        raise PublishError("Set FB_PAGE_ID and FB_PAGE_TOKEN in your .env file")

    import requests

    resp = requests.post(
        f"https://graph.facebook.com/{GRAPH_VERSION}/{page_id}/feed",
        data={"message": text, "access_token": token},
        timeout=30,
    )
    if resp.status_code != 200:
        raise PublishError(f"Facebook API error {resp.status_code}: {resp.text[:300]}")
    return resp.json().get("id", "")


PUBLISHERS = {"facebook": publish_facebook}


def publish(platform: str, text: str, dry_run: bool = True) -> str:
    try:
        fn = PUBLISHERS[platform]
    except KeyError:
        raise PublishError(
            f"Platform '{platform}' is not supported yet. Supported: {', '.join(PUBLISHERS)}"
        ) from None
    return fn(text, dry_run=dry_run)
