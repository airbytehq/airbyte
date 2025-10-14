# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, Iterable, List, Optional, Tuple

from airbyte_cdk.test.mock_http import HttpRequest

from . import AbstractRequestBuilder


class WebAnalyticsRequestBuilder(AbstractRequestBuilder):
    URL = "https://api.hubapi.com/events/v3/events"

    def __init__(self):
        self._token = None
        self._query_params = {}
        self._request_body = None
        self._headers = {}

    def with_token(self, token: str):
        self._token = token
        return self

    @property
    def headers(self) -> Dict[str, Any]:
        return {"Authorization": f"Bearer {self._token}"}

    def with_query(self, qp):
        self._query_params = qp
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(url=self.URL, query_params=self._query_params, headers=self.headers, body=self._request_body)


class CRMSearchRequestBuilder(AbstractRequestBuilder):
    URL = "https://api.hubapi.com/crm/v3/objects/{resource}/search"

    def __init__(self):
        self._resource: Optional[str] = None
        self._properties: Iterable[str] = ()
        self._cursor_field: str = "hs_lastmodifieddate"
        self._start_ms: Optional[int] = None
        self._end_ms: Optional[int] = None
        self._after: Optional[str] = 0
        self._id_floor: int = 0
        self._limit: int = 200

    def for_entity(self, entity: str) -> "CRMSearchRequestBuilder":
        self._resource = entity
        return self

    def with_properties(self, properties: Iterable[str]) -> "CRMSearchRequestBuilder":
        self._properties = properties
        return self

    def with_cursor_range_ms(self, cursor_field: str, start_ms: int, end_ms: int) -> "CRMSearchRequestBuilder":
        self._cursor_field = cursor_field
        self._start_ms = start_ms
        self._end_ms = end_ms
        return self

    def with_page_token(self, next_page_token: Dict[str, Any]) -> "CRMSearchRequestBuilder":
        """
        Accepts either:
          {"after": "..."} or {"next_page_token": {"after": "...", "id": "123"}}
        """
        token = next_page_token.get("next_page_token", next_page_token)
        if "after" in token:
            self._after = token["after"]
        if "id" in token:
            try:
                self._id_floor = int(token["id"])
            except Exception:
                # keep default 0 if not an int
                pass
        return self

    def build(self) -> HttpRequest:
        filters = [
            {
                "propertyName": self._cursor_field,
                "operator": "GTE",
                "value": self._start_ms,
            },
            {
                "propertyName": self._cursor_field,
                "operator": "LTE",
                "value": self._end_ms,
            },
            {
                "propertyName": "hs_object_id",
                "operator": "GTE",
                "value": self._id_floor,
            },
        ]

        body = {
            "limit": self._limit,
            "sorts": [{"propertyName": "hs_object_id", "direction": "ASCENDING"}],
            "filters": filters,
            "properties": list(self._properties),
            "after": self._after,
        }

        url = self.URL.format(resource=self._resource)
        return HttpRequest(url=url, body=json.dumps(body))


class AssociationsBatchReadRequestBuilder(AbstractRequestBuilder):
    """
    Builds: POST https://api.hubapi.com/crm/v4/associations/{parent}/{association}/batch/read
    Body:   {"inputs":[{"id":"<record-id>"}, ...]}
    """

    URL = "https://api.hubapi.com/crm/v4/associations/{parent}/{association}/batch/read"

    def __init__(self):
        self._parent: Optional[str] = None
        self._association: Optional[str] = None
        self._ids: List[str] = []

    def for_parent(self, parent: str) -> "AssociationsBatchReadRequestBuilder":
        self._parent = parent
        return self

    def for_association(self, association: str) -> "AssociationsBatchReadRequestBuilder":
        self._association = association
        return self

    def with_ids(self, ids: Iterable[str]) -> "AssociationsBatchReadRequestBuilder":
        self._ids = [str(i) for i in ids]
        return self

    def build(self) -> HttpRequest:
        url = self.URL.format(parent=self._parent, association=self._association)
        body = json.dumps({"inputs": [{"id": i} for i in self._ids]})
        return HttpRequest(url=url, body=body)


class OwnersArchivedStreamRequestBuilder(AbstractRequestBuilder):
    URL = "https://api.hubapi.com/crm/v3/owners"

    def __init__(self):
        self._after = None

    @property
    def _limit(self):
        return "limit=100"

    @property
    def _archived(self):
        return "archived=true"

    @property
    def _query_params(self):
        return filter(
            None,
            [
                self._limit,
                self._after,
                self._archived,
            ],
        )

    def with_page_token(self, next_page_token: Dict):
        self._after = "&".join([f"{str(key)}={str(val)}" for key, val in next_page_token.items()])
        return self

    def build(self):
        q = "&".join(filter(None, self._query_params))
        return HttpRequest(self.URL, query_params=q)


# We only need to mock the Contacts endpoint because it services the data extracted by ListMemberships, FormSubmissions, MergedAudit
class ContactsStreamRequestBuilder(AbstractRequestBuilder):
    URL = "https://api.hubapi.com/contacts/v1/lists/all/contacts/all"

    def __init__(self) -> None:
        self._filters = []
        self._vid_offset = None

    @property
    def _count(self) -> str:
        return "count=100"

    def with_filter(self, filter_field: str, filter_value: Any) -> "ContactsStreamRequestBuilder":
        self._filters.append(f"{filter_field}={filter_value}")
        return self

    def with_vid_offset(self, vid_offset: str) -> "ContactsStreamRequestBuilder":
        self._vid_offset = f"vidOffset={vid_offset}"
        return self

    @property
    def _query_params(self) -> List[str]:
        params = [
            self._count,
            self._vid_offset,
        ]
        params.extend(self._filters)
        return filter(None, params)

    def build(self) -> HttpRequest:
        q = "&".join(filter(None, self._query_params))
        return HttpRequest(self.URL, query_params=q)
