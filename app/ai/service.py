import httpx

from app.core.config import settings

SYSTEM_PROMPT = """You are a competitive-programming coach.
Give a progressive hint, not a full solution. Point at the key observation, keep it
under 150 words, and never claim code was executed. If the submitted code has an
obvious bug, mention the failing idea without rewriting the whole program."""


class AiNotConfigured(Exception):
    pass


class AiUpstreamError(Exception):
    pass


def is_configured() -> bool:
    return bool(settings.ai_api_key.get_secret_value() and settings.ai_model)


def generate_hint(
    *,
    name: str,
    rating: int | None,
    tags: list[str],
    code: str,
    level: int,
    transport: httpx.BaseTransport | None = None,
) -> str:
    if not is_configured():
        raise AiNotConfigured

    difficulty = f"rating {rating}" if rating is not None else "unrated"
    prompt = (
        f"Problem: {name} ({difficulty}; tags: {', '.join(tags) or 'none'}).\n"
        f"Hint level: {level} of 3 (1 = gentle nudge, 3 = near the algorithm).\n"
        f"User's current code:\n{code}"
    )
    payload = {
        "model": settings.ai_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 400,
    }
    url = f"{settings.ai_base_url.rstrip('/')}/chat/completions"
    headers = {"Authorization": f"Bearer {settings.ai_api_key.get_secret_value()}"}

    try:
        with httpx.Client(
            timeout=settings.ai_timeout_seconds,
            transport=transport,
        ) as client:
            response = client.post(url, headers=headers, json=payload)
    except httpx.HTTPError as exc:
        raise AiUpstreamError from exc

    if response.status_code >= 400:
        raise AiUpstreamError

    try:
        content = response.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise AiUpstreamError from exc
    if not isinstance(content, str) or not content.strip():
        raise AiUpstreamError
    return content.strip()
