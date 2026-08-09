from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any

_RAW_TOKEN = re.compile(r"[A-Za-z0-9_]+|[\u3400-\u9fff]+")
_IDENTIFIER_PART = re.compile(r"[A-Z]+(?=[A-Z][a-z]|\d|$)|[A-Z]?[a-z]+|\d+")
_STOP_WORDS = {
    "a",
    "an",
    "and",
    "code",
    "file",
    "for",
    "function",
    "in",
    "method",
    "of",
    "or",
    "the",
    "to",
    "with",
}


@dataclass(slots=True)
class ContextChunk:
    path: str
    start_line: int
    end_line: int
    symbol: str
    kind: str
    content: str
    score: float = 0.0
    matched_terms: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["matched_terms"] = list(self.matched_terms)
        return value


def query_terms(query: str) -> tuple[str, ...]:
    terms: list[str] = []
    for raw in _RAW_TOKEN.findall(query):
        pieces = raw.split("_")
        expanded: list[str] = []
        for piece in pieces:
            expanded.extend(_IDENTIFIER_PART.findall(piece) or [piece])
        for piece in expanded:
            normalized = piece.casefold()
            if normalized and normalized not in _STOP_WORDS and normalized not in terms:
                terms.append(normalized)
    return tuple(terms)


def rank_repository_context(
    query: str,
    documents: list[dict[str, Any]],
    *,
    limit: int = 8,
    window_lines: int = 80,
) -> list[dict[str, Any]]:
    terms = query_terms(query)
    if not terms:
        return []
    query_phrase = " ".join(terms)
    candidates: list[ContextChunk] = []
    for document in documents:
        path = str(document.get("path", ""))
        text = str(document.get("text", ""))
        lines = text.splitlines()
        symbols = document.get("symbols", [])
        if isinstance(symbols, list):
            for symbol in symbols:
                if not isinstance(symbol, dict):
                    continue
                start = _bounded_line(symbol.get("line"), len(lines), 1)
                end = _bounded_line(symbol.get("end_line"), len(lines), start)
                candidates.append(
                    ContextChunk(
                        path=path,
                        start_line=start,
                        end_line=end,
                        symbol=str(symbol.get("qualified_name", "")),
                        kind=str(symbol.get("kind", "")),
                        content="\n".join(lines[start - 1 : end]),
                    )
                )
        if not lines:
            continue
        step = max(1, window_lines - 20)
        for offset in range(0, len(lines), step):
            end = min(len(lines), offset + window_lines)
            candidates.append(
                ContextChunk(
                    path=path,
                    start_line=offset + 1,
                    end_line=end,
                    symbol="",
                    kind="text",
                    content="\n".join(lines[offset:end]),
                )
            )
            if end == len(lines):
                break

    ranked: list[ContextChunk] = []
    for candidate in candidates:
        score, matched = _score(candidate, terms, query_phrase)
        if score <= 0:
            continue
        candidate.score = round(score, 3)
        candidate.matched_terms = matched
        ranked.append(candidate)
    ranked.sort(key=lambda item: (-item.score, item.path, item.start_line, item.end_line))

    selected: list[ContextChunk] = []
    for candidate in ranked:
        if any(_mostly_overlaps(candidate, existing) for existing in selected):
            continue
        selected.append(candidate)
        if len(selected) >= max(1, min(int(limit), 12)):
            break
    return [_render_chunk(item) for item in selected]


def _score(
    chunk: ContextChunk, terms: tuple[str, ...], query_phrase: str
) -> tuple[float, tuple[str, ...]]:
    path = chunk.path.casefold()
    symbol = chunk.symbol.casefold()
    content = chunk.content.casefold()
    searchable = " ".join((path.replace("_", " "), symbol.replace("_", " "), content))
    matched: list[str] = []
    score = 0.0
    if query_phrase and query_phrase in searchable:
        score += 8.0
    for term in terms:
        term_score = 0.0
        if term == symbol or symbol.endswith(f".{term}"):
            term_score += 10.0
        elif term in symbol:
            term_score += 6.0
        if term in path:
            term_score += 3.0
        occurrences = content.count(term)
        if occurrences:
            term_score += min(occurrences, 4) * 1.25
        if term_score:
            matched.append(term)
            score += term_score
    if matched:
        score += 6.0 * len(matched) / len(terms)
    if chunk.symbol:
        score += 0.5
    return score, tuple(matched)


def _render_chunk(chunk: ContextChunk) -> dict[str, Any]:
    value = chunk.to_dict()
    numbered = [
        f"{number}: {line}"
        for number, line in enumerate(chunk.content.splitlines(), chunk.start_line)
    ]
    value["content"] = "\n".join(numbered)[:4_000]
    return value


def _bounded_line(value: Any, total: int, default: int) -> int:
    if not isinstance(value, int):
        return default
    return max(1, min(value, max(1, total)))


def _mostly_overlaps(left: ContextChunk, right: ContextChunk) -> bool:
    if left.path != right.path:
        return False
    overlap = max(
        0, min(left.end_line, right.end_line) - max(left.start_line, right.start_line) + 1
    )
    shorter = min(left.end_line - left.start_line + 1, right.end_line - right.start_line + 1)
    return bool(shorter and overlap / shorter >= 0.8)
