from typing import Any

from .exceptions import MissingRequiredField


def get_required_field(data: dict[str, Any], field: str) -> Any:
    """:raises MissingRequiredField:"""

    if field not in data:
        raise MissingRequiredField(field=field)

    return data[field]
