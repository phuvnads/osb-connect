"""Command line entry point.

    python -m osb_connect write  --brain examples/brain --topic "..." [--add-to queue.csv --at "2026-11-05 08:00"]
    python -m osb_connect list   --queue queue.csv
    python -m osb_connect approve --queue queue.csv --id 3
    python -m osb_connect run    --queue queue.csv [--live]
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

from . import publishers, queue
from .brain import Brain
from .writer import write_post


def _load_env(path: str = ".env") -> None:
    """Minimal .env loader so users don't need extra packages."""
    p = Path(path)
    if not p.is_file():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"'))


def cmd_write(args) -> None:
    brain = Brain.load(args.brain)
    text = write_post(brain, args.topic, platform=args.platform)
    print(text)
    if args.add_to:
        post = queue.add(args.add_to, args.platform, args.at, text)
        print(f"\nAdded as draft #{post.id}. Review it, then: approve --id {post.id}")


def cmd_list(args) -> None:
    for p in queue.load(args.queue):
        first_line = p.text.splitlines()[0][:60] if p.text else ""
        print(f"#{p.id:>3}  {p.status:<8}  {p.publish_at}  {p.platform:<9}  {first_line}")


def cmd_approve(args) -> None:
    posts = queue.load(args.queue)
    for p in posts:
        if p.id == args.id:
            p.status = "approved"
            queue.save(args.queue, posts)
            print(f"Approved #{p.id}")
            return
    sys.exit(f"No post with id {args.id}")


def cmd_run(args) -> None:
    posts = queue.load(args.queue)
    now = datetime.now()
    due = [p for p in posts if p.due(now)]
    if not due:
        print("Nothing due.")
        return
    for p in due:
        try:
            result = publishers.publish(p.platform, p.text, dry_run=not args.live)
            if args.live:
                p.status, p.result = "posted", result
            print(f"#{p.id}: {result}")
        except publishers.PublishError as e:
            p.status, p.result = "failed", str(e)
            print(f"#{p.id}: FAILED {e}")
    if args.live:
        queue.save(args.queue, posts)
    else:
        print("\nDry run only. Add --live to really publish.")


def main(argv: list[str] | None = None) -> None:
    _load_env()
    parser = argparse.ArgumentParser(prog="osb-connect", description="AI marketing automation for small businesses")
    sub = parser.add_subparsers(dest="command", required=True)

    w = sub.add_parser("write", help="write a post with AI from your brain folder")
    w.add_argument("--brain", required=True, help="folder with profile.md, voice.md, word-fixes.md")
    w.add_argument("--topic", required=True, help="topic and key points of the post")
    w.add_argument("--platform", default="facebook")
    w.add_argument("--add-to", help="queue CSV to add the post to, as a draft")
    w.add_argument("--at", default=datetime.now().strftime(queue.TIME_FORMAT), help="publish time, YYYY-MM-DD HH:MM")
    w.set_defaults(func=cmd_write)

    ls = sub.add_parser("list", help="show the queue")
    ls.add_argument("--queue", required=True)
    ls.set_defaults(func=cmd_list)

    ap = sub.add_parser("approve", help="approve a draft so it can be posted")
    ap.add_argument("--queue", required=True)
    ap.add_argument("--id", required=True)
    ap.set_defaults(func=cmd_approve)

    r = sub.add_parser("run", help="publish approved posts that are due")
    r.add_argument("--queue", required=True)
    r.add_argument("--live", action="store_true", help="really publish (default is dry run)")
    r.set_defaults(func=cmd_run)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
