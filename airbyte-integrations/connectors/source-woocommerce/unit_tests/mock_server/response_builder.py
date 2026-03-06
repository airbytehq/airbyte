# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""
Response builder helper for pagination testing.

This module provides utilities to generate paginated responses for mock server tests.
It allows creating responses with configurable number of records to test pagination behavior.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def get_response_template_path(stream_name: str) -> Path:
    """Get the path to a response template file."""
    return Path(__file__).parent.parent / "resource" / "http" / "response" / f"{stream_name}.json"


def load_response_template(stream_name: str) -> List[Dict[str, Any]]:
    """Load a response template from file."""
    template_path = get_response_template_path(stream_name)
    if template_path.exists():
        return json.loads(template_path.read_text())
    return []


class ResponseBuilder:
    """
    Builder for creating mock HTTP responses with configurable records.

    This is useful for pagination testing where you need to generate
    multiple pages of records.
    """

    def __init__(self, template: Optional[Dict[str, Any]] = None):
        self._template = template or {}
        self._records: List[Dict[str, Any]] = []

    @classmethod
    def from_template(cls, stream_name: str) -> "ResponseBuilder":
        """Create a ResponseBuilder from a stream's response template."""
        templates = load_response_template(stream_name)
        template = templates[0] if templates else {}
        return cls(template=template)

    def with_record(self, record: Dict[str, Any]) -> "ResponseBuilder":
        """Add a single record to the response."""
        self._records.append(record)
        return self

    def with_records(self, records: List[Dict[str, Any]]) -> "ResponseBuilder":
        """Add multiple records to the response."""
        self._records.extend(records)
        return self

    def with_record_count(self, count: int, id_start: int = 1) -> "ResponseBuilder":
        """
        Generate multiple records based on the template.

        Args:
            count: Number of records to generate
            id_start: Starting ID for generated records
        """
        for i in range(count):
            record = copy.deepcopy(self._template)
            if "id" in record:
                record["id"] = id_start + i
            self._records.append(record)
        return self

    def with_pagination_page(self, page_size: int, page_number: int, total_records: int, id_field: str = "id") -> "ResponseBuilder":
        """
        Generate a page of records for pagination testing.

        Args:
            page_size: Number of records per page
            page_number: Current page number (0-indexed)
            total_records: Total number of records across all pages
            id_field: Field name for the record ID
        """
        start_idx = page_number * page_size
        end_idx = min(start_idx + page_size, total_records)

        for i in range(start_idx, end_idx):
            record = copy.deepcopy(self._template)
            if id_field in record:
                record[id_field] = i + 1
            self._records.append(record)
        return self

    def build(self) -> List[Dict[str, Any]]:
        """Build the response as a list of records."""
        return self._records

    def build_json(self) -> str:
        """Build the response as a JSON string."""
        return json.dumps(self._records)


def create_pagination_responses(stream_name: str, total_records: int, page_size: int = 100) -> List[str]:
    """
    Create a list of JSON responses for pagination testing.

    Args:
        stream_name: Name of the stream (used to load template)
        total_records: Total number of records to generate
        page_size: Number of records per page (default 100)

    Returns:
        List of JSON strings, one per page
    """
    template = load_response_template(stream_name)
    base_record = template[0] if template else {"id": 0}

    responses = []
    num_pages = (total_records + page_size - 1) // page_size

    for page in range(num_pages):
        builder = ResponseBuilder(template=base_record)
        builder.with_pagination_page(page_size=page_size, page_number=page, total_records=total_records)
        responses.append(builder.build_json())

    return responses


def create_substream_parent_records(parent_stream_name: str, parent_ids: List[int]) -> str:
    """
    Create a response with specific parent record IDs for substream testing.

    Args:
        parent_stream_name: Name of the parent stream
        parent_ids: List of parent record IDs to include

    Returns:
        JSON string with parent records
    """
    template = load_response_template(parent_stream_name)
    base_record = template[0] if template else {"id": 0}

    records = []
    for parent_id in parent_ids:
        record = copy.deepcopy(base_record)
        record["id"] = parent_id
        records.append(record)

    return json.dumps(records)
