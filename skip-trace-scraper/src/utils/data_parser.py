thonimport json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class SearchQuery:
    """Represents a single search query for the skip trace scraper."""
    search_option: str
    input_value: str

def _normalize_search_option(option: str) -> str:
    normalized = option.strip()
    if not normalized:
        raise ValueError("Search option cannot be empty")
    return normalized

def _normalize_input_value(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("Input value cannot be empty")
    return normalized

def load_queries(path: Path) -> List[SearchQuery]:
    """
    Load search queries from a JSON file.

    Expected schema:
        [
            {
                "search_option": "Name Search",
                "input_value": "James E Whitsitt"
            },
            ...
        ]
    """
    if not path.exists():
        raise FileNotFoundError(f"Input file not found at: {path}")

    logger.debug("Loading queries from: %s", path)

    try:
        with path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in input file: {exc}") from exc

    if not isinstance(raw, list):
        raise ValueError("Input JSON must be a list of query objects")

    queries: List[SearchQuery] = []

    for idx, item in enumerate(raw):
        if not isinstance(item, dict):
            logger.warning("Skipping non-dict entry at index %d", idx)
            continue

        search_option = item.get("search_option") or item.get("Search Option")
        input_value = item.get("input_value") or item.get("Input Given") or item.get("input")

        if search_option is None or input_value is None:
            logger.warning(
                "Skipping entry at index %d due to missing fields: %s",
                idx,
                item,
            )
            continue

        try:
            query = SearchQuery(
                search_option=_normalize_search_option(search_option),
                input_value=_normalize_input_value(input_value),
            )
        except ValueError as exc:
            logger.warning(
                "Skipping invalid entry at index %d: %s (error: %s)",
                idx,
                item,
                exc,
            )
            continue

        queries.append(query)

    logger.info("Loaded %d valid queries from %s", len(queries), path)
    return queries