"""Read a "brain" folder of plain Markdown notes (for example an Obsidian vault).

The brain gives the AI the context it needs to write like you:

- profile.md     who you are, what you sell, who your customers are
- voice.md       how you write: tone, sentence length, words you like
- word-fixes.md  a table of words you always replace (left -> right)

Every file is optional. Missing files are simply skipped.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

PROFILE_FILE = "profile.md"
VOICE_FILE = "voice.md"
WORD_FIXES_FILE = "word-fixes.md"

_FRONTMATTER = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)


def _read(path: Path) -> str:
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    return _FRONTMATTER.sub("", text).strip()


def parse_word_fixes(markdown: str) -> list[tuple[str, str]]:
    """Parse a Markdown table with two columns: wrong word | right word.

    The header row and the separator row are ignored.
    """
    fixes: list[tuple[str, str]] = []
    for line in markdown.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        wrong, right = cells[0], cells[1]
        if not wrong or set(wrong) <= set("-: "):
            continue
        if wrong.lower() in {"wrong", "sai", "chữ cũ", "thay", "tránh viết"}:
            continue  # header row
        fixes.append((wrong, right))
    return fixes


@dataclass
class Brain:
    profile: str = ""
    voice: str = ""
    word_fixes: list[tuple[str, str]] = field(default_factory=list)

    @classmethod
    def load(cls, folder: str | Path) -> "Brain":
        root = Path(folder)
        if not root.is_dir():
            raise FileNotFoundError(f"Brain folder not found: {root}")
        return cls(
            profile=_read(root / PROFILE_FILE),
            voice=_read(root / VOICE_FILE),
            word_fixes=parse_word_fixes(_read(root / WORD_FIXES_FILE)),
        )

    def system_prompt(self) -> str:
        """Build the system prompt the writer sends to Claude."""
        parts = [
            "You write social media posts in natural Vietnamese for the person "
            "described below. Write in their voice, about their real work. "
            "Never invent stories, numbers, customers or years of experience. "
            "If a fact is missing, leave a placeholder like [ĐIỀN: ...]. "
            "Do not use the em dash character. Return only the post text.",
        ]
        if self.profile:
            parts.append("## Profile\n" + self.profile)
        if self.voice:
            parts.append("## Voice\n" + self.voice)
        if self.word_fixes:
            rows = "\n".join(f"- write '{r}' instead of '{w}'" for w, r in self.word_fixes)
            parts.append("## Word choices\n" + rows)
        return "\n\n".join(parts)

    def apply_word_fixes(self, text: str) -> str:
        """Apply the word-fix table and remove em dashes, as a safety net."""
        for wrong, right in self.word_fixes:
            text = text.replace(wrong, right)
        return text.replace(" — ", ", ").replace("—", ", ")
