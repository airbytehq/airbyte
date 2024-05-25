# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, Iterable, List, Tuple

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
        return HttpRequest(
            url=self.URL,
            query_params=self._query_params,
            headers=self.headers,
            body=self._request_body
        )


class CRMStreamRequestBuilder(AbstractRequestBuilder):
    URL = "https://api.hubapi.com/crm/v3/objects/{resource}"

    def __init__(self):
        self._resource = None
        self._associations = ""
        self._dt_range = ""
        self._properties = ""
        self._after = None
        self._search = False

    def for_entity(self, entity):
        self._resource = entity
        return self

    def with_dt_range(self, start_date: Tuple, end_date: Tuple):
        self._dt_range = "&".join(["{}={}".format(*start_date), "{}={}".format(*end_date)])
        return self

    def with_page_token(self, next_page_token: Dict):
        self._after = "&".join([f"{str(key)}={str(val)}" for key, val in next_page_token.items()])
        return self

    def with_associations(self, associations: Iterable[str]):
        self._associations = "&".join([f"associations={a}" for a in associations])
        return self

    def with_properties(self, properties: Iterable[str]):
        self._properties = "properties=" + ",".join(properties)
        return self

    @property
    def _limit(self):
        return "limit=100"

    @property
    def _archived(self):
        return "archived=false"

    @property
    def _query_params(self):
        return [
            self._archived,
            self._associations,
            self._limit,
            self._after,
            self._dt_range,
            self._properties
        ]

    def build(self):
        q = "&".join(filter(None, self._query_params))
        url = self.URL.format(resource=self._resource)
        return HttpRequest(url, query_params=q)


class IncrementalCRMStreamRequestBuilder(CRMStreamRequestBuilder):
    @property
    def _query_params(self):
        return [
            self._limit,
            self._after,
            self._dt_range,
            self._archived,
            self._associations,
            self._properties
        ]


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
        return filter(None, [
            self._limit,
            self._after,
            self._archived,
        ])

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
