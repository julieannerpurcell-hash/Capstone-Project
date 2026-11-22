"""One place that talks to an outside AI service.

Which service is used is decided by settings in the .env file, so the rest
of the app never needs to know:

    AI_PROVIDER=demo        (default - no AI service, no key needed)
    AI_PROVIDER=gemini      (Google Gemini API)
    AI_PROVIDER=anthropic   (Claude API)
    AI_API_KEY=...          (the key for that service - keep it in .env only)
    AI_MODEL=...            (optional - the model name to use)
"""
import json
import os
import urllib.error
import urllib.request

TIMEOUT_SECONDS = 25
MAX_OUTPUT_TOKENS = 700

DEFAULT_MODELS = {
    "gemini": "gemini-flash-latest",
    "anthropic": "claude-haiku-5-5",
}


class AIUnavailable(Exception):
    """The AI service is not set up, or it did not answer."""


def provider_name():
    return os.getenv("AI_PROVIDER", "demo").strip().lower() or "demo"


def ai_enabled():
    """True when a real AI service is configured."""
    return provider_name() in DEFAULT_MODELS and bool(os.getenv("AI_API_KEY"))


def _post(url, headers, body):
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        raise AIUnavailable(type(exc).__name__) from exc


def generate(system_prompt, user_prompt):
    """Send the prompts to the configured AI service and return its text answer."""
    provider = provider_name()
    key = os.getenv("AI_API_KEY", "")
    if provider not in DEFAULT_MODELS or not key:
        raise AIUnavailable("not configured")
    model = os.getenv("AI_MODEL") or DEFAULT_MODELS[provider]

    try:
        if provider == "gemini":
            data = _post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                {"x-goog-api-key": key},
                {
                    "systemInstruction": {"parts": [{"text": system_prompt}]},
                    "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
                    "generationConfig": {"maxOutputTokens": MAX_OUTPUT_TOKENS, "temperature": 0.4},
                },
            )
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            data = _post(
                "https://api.anthropic.com/v1/messages",
                {"x-api-key": key, "anthropic-version": "2023-06-01"},
                {
                    "model": model,
                    "max_tokens": MAX_OUTPUT_TOKENS,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}],
                },
            )
            text = data["content"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise AIUnavailable("unexpected response") from exc

    text = (text or "").strip()
    if not text:
        raise AIUnavailable("empty answer")
    return text