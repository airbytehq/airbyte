# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Dict

from airbyte_cdk.test.mock_http import HttpRequest


class GranolaRequestBuilder:
    """
    Builder for Granola API requests.

    Example usage:
        request = (
            GranolaRequestBuilder.notes_endpoint()
            .with_created_after("2025-10-12T00:00:00Z")
            .with_created_before("2025-11-10T23:59:59Z")
            .build()
        )
    """

    BASE_URL = "https://public-api.granola.ai"

    def __init__(self, path: str) -> None:
        self._path = path
        self._query_params: Dict[str, str] = {}

    @classmethod
    def notes_endpoint(cls) -> "GranolaRequestBuilder":
        return cls("/v1/notes").with_page_size(30)

    @classmethod
    def note_endpoint(cls, note_id: str) -> "GranolaRequestBuilder":
        return cls(f"/v1/notes/{note_id}")

    @classmethod
    def transcript_endpoint(cls, note_id: str) -> "GranolaRequestBuilder":
        return cls(f"/v1/notes/{note_id}/transcript").with_page_size(100)

    def with_include(self, include: str) -> "GranolaRequestBuilder":
        return self.with_query_param("include", include)

    def with_page_size(self, page_size: int) -> "GranolaRequestBuilder":
        return self.with_query_param("page_size", str(page_size))

    def with_created_after(self, created_after: str) -> "GranolaRequestBuilder":
        return self.with_query_param("created_after", created_after)

    def with_created_before(self, created_before: str) -> "GranolaRequestBuilder":
        return self.with_query_param("created_before", created_before)

    def with_cursor(self, cursor: str) -> "GranolaRequestBuilder":
        return self.with_query_param("cursor", cursor)

    def with_query_param(self, key: str, value: str) -> "GranolaRequestBuilder":
        self._query_params[key] = value
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(url=f"{self.BASE_URL}{self._path}", query_params=dict(self._query_params))
