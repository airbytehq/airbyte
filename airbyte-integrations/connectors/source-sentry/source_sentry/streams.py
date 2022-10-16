#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
        return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        return {}


class SentryStreamPagination(SentryStream):
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Expect the link header field to always contain the values ​​for `rel`, `results`, and `cursor`.
        If there is actually the next page, rel="next"; results="true"; cursor="<next-page-token>".
        """
        if response.links["next"]["results"] == "true":
            return {"cursor": response.links["next"]["cursor"]}
        else:
            return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        if next_page_token:
            params.update(next_page_token)

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()


class Events(SentryStreamPagination):
    """
    Docs: https://docs.sentry.io/api/events/list-a-projects-events/
    """

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
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params.update({"full": "true"})

        return params


class Issues(SentryStreamPagination):
    """
    Docs: https://docs.sentry.io/api/events/list-a-projects-issues/
    """

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
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params.update({"statsPeriod": "", "query": ""})

        return params


class Projects(SentryStreamPagination):
    """
    Docs: https://docs.sentry.io/api/projects/list-your-projects/
    """

    def path(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return "projects/"


class ProjectDetail(SentryStream):
    """
    Docs: https://docs.sentry.io/api/projects/retrieve-a-project/
    """

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
