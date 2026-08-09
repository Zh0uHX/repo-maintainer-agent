from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from collections.abc import Iterable
from typing import Any, Protocol


class ModelClient(Protocol):
    def complete(self, messages: list[dict[str, str]]) -> dict[str, Any]: ...


def parse_json_object(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1])
            if text.lstrip().startswith("json"):
                text = text.lstrip()[4:].lstrip()
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("Model response did not contain a JSON object.") from None
        value = json.loads(text[start : end + 1])
    if not isinstance(value, dict):
        raise TypeError("Model response must be a JSON object.")
    return value


class OpenAICompatibleClient:
    """Small dependency-free client for OpenAI-compatible chat-completions APIs."""

    def __init__(
        self,
        *,
        model: str,
        api_key: str | None,
        base_url: str,
        timeout_seconds: int = 120,
        retries: int = 2,
        max_tokens: int = 8_192,
    ) -> None:
        self.model = model
        self.api_key = api_key
        self.url = f"{base_url.rstrip('/')}/chat/completions"
        self.timeout_seconds = timeout_seconds
        self.retries = retries
        self.max_tokens = max_tokens
        self.last_metadata: dict[str, Any] = {}

    def complete(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        last_error: Exception | None = None
        retry_messages = messages
        usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        provider_model = self.model
        parse_retries = 0
        for attempt in range(self.retries + 1):
            content: str | None = None
            try:
                payload = json.dumps(
                    {
                        "model": self.model,
                        "messages": retry_messages,
                        "temperature": 0,
                        "max_tokens": self.max_tokens,
                        "response_format": {"type": "json_object"},
                    }
                ).encode()
                request = urllib.request.Request(
                    self.url, data=payload, headers=headers, method="POST"
                )
                with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                    result = json.loads(response.read().decode("utf-8"))
                raw_content = result["choices"][0]["message"]["content"]
                if not isinstance(raw_content, str):
                    raise TypeError("Model message content must be a string.")
                content = raw_content
                provider_model = str(result.get("model", self.model))
                _accumulate_usage(usage, result.get("usage", {}))
                parsed = parse_json_object(content)
                self.last_metadata = _request_metadata(
                    provider_model, usage, attempt + 1, parse_retries
                )
                return parsed
            except (
                urllib.error.URLError,
                KeyError,
                IndexError,
                json.JSONDecodeError,
                TypeError,
                ValueError,
            ) as exc:
                last_error = exc
                if content is not None:
                    parse_retries += 1
                    retry_messages = _json_repair_messages(messages, content, exc)
                self.last_metadata = _request_metadata(
                    provider_model, usage, attempt + 1, parse_retries, error=exc
                )
                if attempt < self.retries and content is None:
                    time.sleep(2**attempt)
        raise RuntimeError(f"Model request failed after retries: {last_error}") from last_error


def _json_repair_messages(
    messages: list[dict[str, str]], content: str, error: Exception
) -> list[dict[str, str]]:
    return [
        *messages,
        {"role": "assistant", "content": content},
        {
            "role": "user",
            "content": (
                "Your previous response was invalid JSON "
                f"({type(error).__name__}: {error}). Regenerate the same intended response as "
                "one syntactically valid JSON object only. Preserve the intended action and all "
                "string contents; add no Markdown or explanation."
            ),
        },
    ]


def _accumulate_usage(total: dict[str, int], value: Any) -> None:
    if not isinstance(value, dict):
        return
    aliases = {
        "prompt_tokens": ("prompt_tokens", "input_tokens"),
        "completion_tokens": ("completion_tokens", "output_tokens"),
        "total_tokens": ("total_tokens",),
    }
    for target, names in aliases.items():
        for name in names:
            amount = value.get(name)
            if isinstance(amount, int):
                total[target] += amount
                break


def _request_metadata(
    model: str,
    usage: dict[str, int],
    request_attempts: int,
    parse_retries: int,
    *,
    error: Exception | None = None,
) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "model": model,
        "usage": dict(usage),
        "request_attempts": request_attempts,
        "parse_retries": parse_retries,
    }
    if error is not None:
        metadata["error"] = f"{type(error).__name__}: {error}"
    return metadata


class ScriptedClient:
    """Deterministic model used by tests and examples."""

    def __init__(self, responses: Iterable[dict[str, Any]]) -> None:
        self._responses = iter(responses)
        self.last_metadata: dict[str, Any] = {}

    def complete(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        del messages
        try:
            return next(self._responses)
        except StopIteration:
            raise RuntimeError("Scripted model has no response left.") from None
