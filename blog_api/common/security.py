from typing import Any, Dict, List, Union

import bleach  # type: ignore

JsonValue = Union[Dict[str, Any], List[Any], str, int, float, bool, None]


def sanitize_html_input(text: str) -> str:
    if not text:
        return ""
    return str(bleach.clean(text, tags=[], attributes={}, strip=True))


def sanitize_data(data: dict[str, Any], max_depth: int = 10) -> dict[str, Any]:
    """
    Sanitizes dictionary by stripping HTML from all string values.

    Args:
        data: Dictionary to sanitize
        max_depth: Maximum allowed nesting level to prevent DoS

    Returns:
        Sanitized dictionary

    Raises:
        ValueError: If nesting depth exceeds max_depth
    """

    def walk_and_sanitize(obj: JsonValue, depth: int = 0) -> JsonValue:
        if depth > max_depth:
            raise ValueError(f"Payload structure exceeds maximum depth of {max_depth}")

        if isinstance(obj, dict):
            return {
                sanitize_html_input(str(k)): walk_and_sanitize(v, depth + 1)
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [walk_and_sanitize(i, depth + 1) for i in obj]
        elif isinstance(obj, str):
            return sanitize_html_input(obj)

        return obj

    result = walk_and_sanitize(data)

    assert isinstance(result, dict), "Sanitized data is not a dictionary"

    return result
