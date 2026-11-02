"""Header value to the employee role string.

Presentation writes the result onto the domain context. A missing or blank
header is an empty role so the facade can report it as unknown.
"""

from __future__ import annotations


def role_from_header(header_value: str | None) -> str:
    if header_value is None:
        return ""
    return header_value.strip()
