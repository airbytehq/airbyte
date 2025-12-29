# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List, Optional

from airbyte_cdk.test.mock_http import HttpResponse


class LinkedInAdsPaginatedResponseBuilder:
    """Builder class for creating LinkedIn Ads API paginated responses.

    LinkedIn Ads API uses 'elements' as the record container and 'metadata' for pagination info.
    Pagination uses 'nextPageToken' for cursor-based pagination.
    """

    def __init__(self):
        self._records: List[Dict[str, Any]] = []
        self._next_page_token: Optional[str] = None
        self._total: Optional[int] = None
        self._status_code: int = 200

    def with_records(self, records: List[Dict[str, Any]]) -> "LinkedInAdsPaginatedResponseBuilder":
        self._records = records
        return self

    def with_next_page_token(self, token: str) -> "LinkedInAdsPaginatedResponseBuilder":
        self._next_page_token = token
        return self

    def with_total(self, total: int) -> "LinkedInAdsPaginatedResponseBuilder":
        self._total = total
        return self

    def with_status_code(self, status_code: int) -> "LinkedInAdsPaginatedResponseBuilder":
        self._status_code = status_code
        return self

    def build(self) -> HttpResponse:
        body: Dict[str, Any] = {"elements": self._records}

        metadata: Dict[str, Any] = {}
        if self._next_page_token:
            metadata["nextPageToken"] = self._next_page_token
        if self._total is not None:
            metadata["total"] = self._total

        if metadata:
            body["metadata"] = metadata

        return HttpResponse(body=json.dumps(body), status_code=self._status_code)

    @classmethod
    def single_page(cls, records: List[Dict[str, Any]], total: Optional[int] = None) -> HttpResponse:
        builder = cls().with_records(records)
        if total is not None:
            builder.with_total(total)
        return builder.build()

    @classmethod
    def empty_page(cls) -> HttpResponse:
        return cls().with_records([]).build()


class LinkedInAdsOffsetPaginatedResponseBuilder:
    """Builder class for creating LinkedIn Ads API offset-paginated responses.

    Used for streams like account_users and conversions that use OffsetIncrement pagination.
    """

    def __init__(self):
        self._records: List[Dict[str, Any]] = []
        self._paging: Dict[str, Any] = {}
        self._status_code: int = 200

    def with_records(self, records: List[Dict[str, Any]]) -> "LinkedInAdsOffsetPaginatedResponseBuilder":
        self._records = records
        return self

    def with_paging(self, start: int, count: int, total: int) -> "LinkedInAdsOffsetPaginatedResponseBuilder":
        self._paging = {"start": start, "count": count, "total": total}
        return self

    def with_status_code(self, status_code: int) -> "LinkedInAdsOffsetPaginatedResponseBuilder":
        self._status_code = status_code
        return self

    def build(self) -> HttpResponse:
        body: Dict[str, Any] = {"elements": self._records}

        if self._paging:
            body["paging"] = self._paging

        return HttpResponse(body=json.dumps(body), status_code=self._status_code)

    @classmethod
    def single_page(cls, records: List[Dict[str, Any]], total: Optional[int] = None) -> HttpResponse:
        builder = cls().with_records(records)
        if total is not None:
            builder.with_paging(start=0, count=len(records), total=total)
        return builder.build()

    @classmethod
    def empty_page(cls) -> HttpResponse:
        return cls().with_records([]).with_paging(start=0, count=0, total=0).build()


class LinkedInAdsAnalyticsResponseBuilder:
    """Builder class for creating LinkedIn Ads Analytics API responses.

    Analytics streams have a different response structure with no pagination.
    """

    def __init__(self):
        self._records: List[Dict[str, Any]] = []
        self._status_code: int = 200

    def with_records(self, records: List[Dict[str, Any]]) -> "LinkedInAdsAnalyticsResponseBuilder":
        self._records = records
        return self

    def with_status_code(self, status_code: int) -> "LinkedInAdsAnalyticsResponseBuilder":
        self._status_code = status_code
        return self

    def build(self) -> HttpResponse:
        body: Dict[str, Any] = {"elements": self._records}
        return HttpResponse(body=json.dumps(body), status_code=self._status_code)

    @classmethod
    def single_page(cls, records: List[Dict[str, Any]]) -> HttpResponse:
        return cls().with_records(records).build()

    @classmethod
    def empty_page(cls) -> HttpResponse:
        return cls().with_records([]).build()
