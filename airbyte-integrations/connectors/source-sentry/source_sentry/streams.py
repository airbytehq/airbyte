#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import pendulum
import requests
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream


class SentryStream(HttpStream, ABC):
    API_VERSION = "0"
    URL_TEMPLATE = "https://{hostname}/api/{api_version}/"
    primary_key = "id"

    def __init__(self, hostname: str, **kwargs):
        super().__init__(**kwargs)
        self._url_base = self.URL_TEMPLATE.format(hostname=hostname, api_version=self.API_VERSION)
        # hardcode the start_date default value, since it's not present in spec.
        self.start_date = "1900-01-01T00:00:00.0Z"

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


class SentryIncremental(SentryStreamPagination, IncrementalMixin):
    def __init__(self, *args, **kwargs):
        super(SentryIncremental, self).__init__(*args, **kwargs)
        self._cursor_value = None

    def validate_state_value(self, state_value: str = None) -> str:
        none_or_empty = state_value == "None" if state_value else True
        return self.start_date if none_or_empty else state_value

    def get_state_value(self, stream_state: Mapping[str, Any] = None) -> str:
        state_value = self.validate_state_value(stream_state.get(self.cursor_field, self.start_date) if stream_state else self.start_date)
        return pendulum.parse(state_value)

    def filter_by_state(self, stream_state: Mapping[str, Any] = None, record: Mapping[str, Any] = None) -> Iterable:
        """
        Endpoint does not provide query filtering params, but they provide us
        cursor field in most cases, so we used that as incremental filtering
        during the parsing.
        """
        if pendulum.parse(record[self.cursor_field]) > self.get_state_value(stream_state):
            # Persist state.
            # There is a bug in state setter: because of self._cursor_value is not defined it raises Attribute error
            # which is ignored in airbyte_cdk/sources/abstract_source.py:320 and we have an empty state in return
            # See: https://github.com/airbytehq/oncall/issues/1317
            self.state = record
            yield record

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[MutableMapping]:
        json_response = response.json() or []

        for record in json_response:
            yield from self.filter_by_state(stream_state=stream_state, record=record)

    @property
    def state(self) -> Mapping[str, Any]:
        return {self.cursor_field: self._cursor_value}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        """
        Define state as a max between given value and current state
        """
        if not self._cursor_value:
            self._cursor_value = value.get(self.cursor_field)
        else:
            current_value = value.get(self.cursor_field) or self.start_date
            current_state = str(self.get_state_value(self.state))
            self._cursor_value = max(current_value, current_state)


class Events(SentryIncremental):
    """
    Docs: https://docs.sentry.io/api/events/list-a-projects-events/
    """

    primary_key = "id"
    cursor_field = "dateCreated"

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


class Issues(SentryIncremental):
    """
    Docs: https://docs.sentry.io/api/events/list-a-projects-issues/
    """

    primary_key = "id"
    cursor_field = "lastSeen"

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


class Projects(SentryIncremental):
    """
    Docs: https://docs.sentry.io/api/projects/list-your-projects/
    """

    primary_key = "id"
    cursor_field = "dateCreated"

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
