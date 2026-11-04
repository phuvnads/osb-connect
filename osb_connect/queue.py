"""A simple post queue stored as a CSV file, easy to open in Excel or Google Sheets.

Columns: id, platform, publish_at, status, text, result
- publish_at: "YYYY-MM-DD HH:MM" in local time
- status: draft | approved | posted | failed

Only rows marked "approved" are ever posted. Nothing goes out without a human OK.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass, fields
from datetime import datetime
from pathlib import Path

TIME_FORMAT = "%Y-%m-%d %H:%M"
STATUSES = {"draft", "approved", "posted", "failed"}


@dataclass
class Post:
    id: str
    platform: str
    publish_at: str
    status: str
    text: str
    result: str = ""

    def due(self, now: datetime) -> bool:
        return self.status == "approved" and datetime.strptime(self.publish_at, TIME_FORMAT) <= now


COLUMNS = [f.name for f in fields(Post)]


def load(path: str | Path) -> list[Post]:
    path = Path(path)
    if not path.is_file():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        posts = [Post(**{k: row.get(k, "") or "" for k in COLUMNS}) for row in csv.DictReader(f)]
    for p in posts:
        if p.status not in STATUSES:
            raise ValueError(f"Post {p.id}: unknown status '{p.status}'")
        datetime.strptime(p.publish_at, TIME_FORMAT)  # validate early
    return posts


def save(path: str | Path, posts: list[Post]) -> None:
    with Path(path).open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for p in posts:
            writer.writerow(asdict(p))


def add(path: str | Path, platform: str, publish_at: str, text: str) -> Post:
    datetime.strptime(publish_at, TIME_FORMAT)
    posts = load(path)
    next_id = str(max((int(p.id) for p in posts if p.id.isdigit()), default=0) + 1)
    post = Post(id=next_id, platform=platform, publish_at=publish_at, status="draft", text=text)
    posts.append(post)
    save(path, posts)
    return post
