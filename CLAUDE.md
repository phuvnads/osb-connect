# CLAUDE.md

Guide for Claude Code (and other AI coding agents) working on this repository.

## What this project is

OSB Connect: a small Python CLI that writes marketing posts in the user's voice with Claude and publishes approved posts through official platform APIs. Target users are Vietnamese small businesses and solo marketers who are not technical.

## Rules

- Keep it simple: standard library first. Runtime dependencies are only `anthropic` and `requests`.
- Never post without approval. Only queue rows with status `approved` may be published, and `run` stays dry-run unless `--live` is passed.
- Official APIs only. Do not add browser automation, scraping, or anything that breaks a platform's terms.
- Secrets live in `.env` (gitignored). Never hardcode tokens, never commit `.env`, never log tokens.
- The writer must not invent facts. Keep the "no invented stories, numbers, customers" instruction in `Brain.system_prompt()`.
- User-facing text in posts is Vietnamese. Code, comments and docs are English, README has a Vietnamese section.
- Model: `claude-opus-5-5` with adaptive thinking (see `writer.py`). Do not change the model unless asked.

## Commands

```bash
python -m unittest discover -s tests     # run tests (no network)
python -m osb_connect --help             # CLI help
```

## Adding a publisher

1. Add `publish_<platform>(text, dry_run=True) -> str` in `publishers.py`, returning the created post id.
2. Read credentials from environment variables and document them in `.env.example`.
3. Register it in `PUBLISHERS` and add a dry-run test in `tests/test_core.py`.
