"""Write a post with Claude, using the context from the brain."""

from __future__ import annotations

from .brain import Brain

DEFAULT_MODEL = "claude-opus-5-5"


class RefusedError(RuntimeError):
    """Claude declined to write this post."""


def build_request(brain: Brain, topic: str, platform: str, model: str = DEFAULT_MODEL) -> dict:
    """Return the keyword arguments for the Messages API call (kept separate for testing)."""
    return {
        "model": model,
        "max_tokens": 16000,
        "thinking": {"type": "adaptive"},
        "output_config": {"effort": "medium"},
        # Server-side fallback: if a request is declined, the API retries on a fallback model.
        "betas": ["server-side-fallback-2026-07-01"],
        "fallbacks": "default",
        "system": brain.system_prompt(),
        "messages": [
            {
                "role": "user",
                "content": (
                    f"Platform: {platform}\n"
                    f"Topic and key points:\n{topic}\n\n"
                    "Write one post. The first 2 lines must tell the reader what they "
                    "get if they keep reading."
                ),
            }
        ],
    }


def write_post(brain: Brain, topic: str, platform: str = "facebook",
               model: str = DEFAULT_MODEL, client=None) -> str:
    """Generate a post. Needs ANTHROPIC_API_KEY (or an `ant auth login` profile)."""
    if client is None:
        import anthropic  # imported here so the rest of the tool works without the SDK

        client = anthropic.Anthropic()

    response = client.beta.messages.create(**build_request(brain, topic, platform, model))

    if response.stop_reason == "refusal":
        raise RefusedError("Claude declined this topic. Try rewording it.")

    text = "".join(block.text for block in response.content if block.type == "text").strip()
    return brain.apply_word_fixes(text)
