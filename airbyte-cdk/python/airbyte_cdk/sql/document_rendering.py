# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Methods for converting Airbyte records into documents."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import yaml
from pydantic import BaseModel

from airbyte_cdk.sql.documents import Document


if TYPE_CHECKING:
    from collections.abc import Iterable


def _to_title_case(name: str, /) -> str:
    """Convert a string to title case.

    Unlike Python's built-in `str.title` method, this function doesn't lowercase the rest of the
    string. This is useful for converting "snake_case" to "Title Case" without negatively affecting
    strings that are already in title case or camel case.
    """
    return " ".join(word[0].upper() + word[1:] for word in name.split("_"))


class CustomRenderingInstructions(BaseModel):
    """Instructions for rendering a stream's records as documents."""

    title_property: str | None = None
    content_properties: list[str]
    frontmatter_properties: list[str]
    metadata_properties: list[str]


class DocumentRenderer(BaseModel):
    """Instructions for rendering a stream's records as documents."""

    title_property: str | None = None
    content_properties: list[str] | None = None
    metadata_properties: list[str] | None = None
    render_metadata: bool = False

    # TODO: Add primary key and cursor key support:
    # https://github.com/airbytehq/pyairbyte/issues/319
    # primary_key_properties: list[str]
    # cursor_property: str | None

    def render_document(self, record: dict[str, Any]) -> Document:
        """Render a record as a document.

        The document will be rendered as a markdown document, with content, frontmatter, and an
        optional title. If there are multiple properties to render as content, they will be rendered
        beneath H2 section headers. If there is only one property to render as content, it will be
        rendered without a section header. If a title property is specified, it will be rendered as
        an H1 header at the top of the document.

        Returns:
            A tuple of (content: str, metadata: dict).
        """
        content = ""
        if not self.metadata_properties:
            self.metadata_properties = [
                key
                for key in record
                if key not in (self.content_properties or []) and key != self.title_property
            ]
        if self.title_property:
            content += f"# {record[self.title_property]}\n\n"
        if self.render_metadata or not self.content_properties:
            content += "```yaml\n"
            content += yaml.dump({key: record[key] for key in self.metadata_properties})
            content += "```\n"

        if not self.content_properties:
            pass
        elif len(self.content_properties) == 1:
            # Only one property to render as content; no need for section headers.
            content += str(record[self.content_properties[0]])
        else:
            # Multiple properties to render as content; use H2 section headers.
            content += "\n".join(
                f"## {_to_title_case(key)}\n\n{record[key]}\n\n" for key in self.content_properties
            )

        return Document(
            # id=doc_id,  # TODD: Add support for primary key and doc ID generation.
            content=content,
            metadata={key: record[key] for key in self.metadata_properties},
        )

    def render_documents(self, records: Iterable[dict[str, Any]]) -> Iterable[Document]:
        """Render an iterable of records as documents."""
        yield from (self.render_document(record=record) for record in records)
