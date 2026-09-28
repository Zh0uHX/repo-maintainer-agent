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
    return parse_json_object_detail(content)[0]


def parse_json_object_detail(content: str) -> tuple[dict[str, Any], int]:
    """Parse a model reply and return it with the number of closing brackets appended.

    Models occasionally drop the final ``}`` of deeply nested replies and repeat the mistake when
    asked to regenerate. When the text ends outside a string with unclosed brackets, appending the
    missing closers is unambiguous, so it is done locally and reported to the caller.
    """
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1])
            if text.lstrip().startswith("json"):
                text = text.lstrip()[4:].lstrip()
    closed = 0
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        if start < 0:
            raise ValueError("Model response did not contain a JSON object.") from None
        closers = _missing_closers(text[start:])
        if closers:
            value = json.loads(text[start:] + closers)
            closed = len(closers)
        else:
            end = text.rfind("}")
            if end <= start:
                raise ValueError("Model response did not contain a JSON object.") from None
            value = json.loads(text[start : end + 1])
    if not isinstance(value, dict):
        raise TypeError("Model response must be a JSON object.")
    return value, closed


def _missing_closers(text: str) -> str:
    """Closers for brackets still open at the end of ``text``; empty if ending inside a string."""
    stack: list[str] = []
    in_string = escaped = False
    for char in text:
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
        elif char in "{[":
            stack.append("}" if char == "{" else "]")
        elif char in "}]" and (not stack or stack.pop() != char):
            return ""
    if in_string:
        return ""
    return "".join(reversed(stack))


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
        json_mode = True
        for attempt in range(self.retries + 1):
            content: str | None = None
            finish_reason: str | None = None
            try:
                body: dict[str, Any] = {
                    "model": self.model,
                    "messages": retry_messages,
                    "temperature": 0,
                    "max_tokens": self.max_tokens,
                }
                if json_mode:
                    body["response_format"] = {"type": "json_object"}
                payload = json.dumps(body).encode()
                request = urllib.request.Request(
                    self.url, data=payload, headers=headers, method="POST"
                )
                with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                    result = json.loads(response.read().decode("utf-8"))
                finish_reason = result["choices"][0].get("finish_reason")
                raw_content = result["choices"][0]["message"]["content"]
                if not isinstance(raw_content, str):
                    raise TypeError("Model message content must be a string.")
                content = raw_content
                provider_model = str(result.get("model", self.model))
                _accumulate_usage(usage, result.get("usage", {}))
                if not content.strip():
                    raise ValueError("Model returned an empty message.")
                parsed, closed = parse_json_object_detail(content)
                self.last_metadata = _request_metadata(
                    provider_model, usage, attempt + 1, parse_retries
                )
                if closed:
                    self.last_metadata["closed_brackets"] = closed
                if not json_mode:
                    self.last_metadata["json_mode_fallback"] = True
                if finish_reason:
                    self.last_metadata["finish_reason"] = finish_reason
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
                empty_reply = content is not None and not content.strip()
                if content is not None and not empty_reply:
                    parse_retries += 1
                    retry_messages = _json_repair_messages(messages, content, exc)
                elif empty_reply:
                    # Nothing to repair. JSON mode can yield whitespace-only replies, so resend
                    # the original request with the format constraint left to the prompt.
                    retry_messages = messages
                    json_mode = False
                self.last_metadata = _request_metadata(
                    provider_model,
                    usage,
                    attempt + 1,
                    parse_retries,
                    error=exc,
                    invalid_content=content,
                )
                if not json_mode:
                    self.last_metadata["json_mode_fallback"] = True
                if finish_reason:
                    self.last_metadata["finish_reason"] = finish_reason
                if attempt < self.retries and (content is None or empty_reply):
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
    invalid_content: str | None = None,
) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "model": model,
        "usage": dict(usage),
        "request_attempts": request_attempts,
        "parse_retries": parse_retries,
    }
    if error is not None:
        metadata["error"] = f"{type(error).__name__}: {error}"
    if invalid_content is not None:
        # Keep the unparseable reply so protocol failures can be diagnosed from the trace.
        metadata["invalid_content"] = invalid_content[:8_000]
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
