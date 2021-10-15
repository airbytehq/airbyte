#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream


class SentryStream(HttpStream, ABC):
    API_VERSION = "0"
    URL_TEMPLATE = "https://{hostname}/api/{api_version}/"
    primary_key = "id"

    def __init__(self, hostname: str, **kwargs):
        super().__init__(**kwargs)
        self._url_base = self.URL_TEMPLATE.format(hostname=hostname, api_version=self.API_VERSION)

    @property
    def url_base(self) -> str:
        return self._url_base

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Expect the link header field to always contain the values ​​for `rel`, `results`, and `cursor`.
        If there is actually the next page, rel="next"; results="true"; cursor="<next-page-token>".
        """
        try:
            if response.links["next"]["results"] == "true":
                return {"cursor": response.links["next"]["cursor"]}
            else:
                return None
        except KeyError:
            return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()


class Events(SentryStream):
    def __init__(self, organization: str, project: str, **kwargs):
        super().__init__(**kwargs)
        self._organization = organization
        self._project = project

    def path(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return f"projects/{self._organization}/{self._project}/events/"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        return {"full": "true"}


class Issues(SentryStream):
    def __init__(self, organization: str, project: str, **kwargs):
        super().__init__(**kwargs)
        self._organization = organization
        self._project = project

    def path(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return f"projects/{self._organization}/{self._project}/issues/"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        return {"statsPeriod": "", "query": ""}


class ProjectDetail(SentryStream):
    def __init__(self, organization: str, project: str, **kwargs):
        super().__init__(**kwargs)
        self._organization = organization
        self._project = project

    def path(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return f"projects/{self._organization}/{self._project}/"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield response.json()


class Projects(SentryStream):
    def path(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return "projects/"
