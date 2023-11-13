#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import urllib.parse
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http import HttpStream

from .availability_strategy import KlaviyoAvailabilityStrategy
from .exceptions import KlaviyoBackoffError


class KlaviyoStream(HttpStream, ABC):
    """Base stream for api version v2023-10-15"""

    url_base = "https://a.klaviyo.com/api/"
    primary_key = "id"
    page_size = None
    api_revision = "2023-10-15"

    def __init__(self, api_key: str, start_date: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self._api_key = api_key
        self._start_ts = start_date

    @property
    def availability_strategy(self) -> Optional[AvailabilityStrategy]:
        return KlaviyoAvailabilityStrategy()

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {
            "Accept": "application/json",
            "Revision": self.api_revision,
            "Authorization": f"Klaviyo-API-Key {self._api_key}",
        }

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests.

        Klaviyo uses cursor-based pagination https://developers.klaviyo.com/en/reference/api_overview#pagination
        This method returns the params in the pre-constructed url nested in links[next]
        """

        decoded_response = response.json()

        links = decoded_response.get("links", {})
        next = links.get("next")
        if not next:
            return None

        next_url = urllib.parse.urlparse(next)
        return {str(k): str(v) for (k, v) in urllib.parse.parse_qsl(next_url.query)}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        # If next_page_token is set, all the parameters are already provided
        if next_page_token:
            return next_page_token
        else:
            return {"page[size]": self.page_size} if self.page_size else {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """:return an iterable containing each record in the response"""

        response_json = response.json()
        for record in response_json.get("data", []):  # API returns records in a container array "data"
            record = self.map_record(record)
            yield record

    def map_record(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """Subclasses can override this to apply custom mappings to a record"""

        record[self.cursor_field] = record["attributes"][self.cursor_field]
        return record

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest
        record and the current state and picks the 'most' recent cursor. This is how a stream's state is determined.
        Required for incremental.
        """

        current_stream_cursor_value = current_stream_state.get(self.cursor_field, self._start_ts)
        latest_cursor = pendulum.parse(latest_record[self.cursor_field])
        if current_stream_cursor_value:
            latest_cursor = max(latest_cursor, pendulum.parse(current_stream_cursor_value))
        current_stream_state[self.cursor_field] = latest_cursor.isoformat()
        return current_stream_state

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_after = float(retry_after) if retry_after else None
            if retry_after and retry_after >= self.max_time:
                raise KlaviyoBackoffError(
                    f"Stream {self.name} has reached rate limit with 'Retry-After' of {retry_after} seconds, exit from stream."
                )
            return retry_after

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        try:
            yield from super().read_records(sync_mode, cursor_field, stream_slice, stream_state)
        except KlaviyoBackoffError as e:
            self.logger.warning(repr(e))


class IncrementalKlaviyoStream(KlaviyoStream, ABC):
    """Base class for all incremental streams, requires cursor_field to be declared"""

    @property
    @abstractmethod
    def cursor_field(self) -> Union[str, List[str]]:
        """
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.
        :return str: The name of the cursor field.
        """

    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs):
        """Add incremental filters"""

        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)

        if not params.get("filter"):
            stream_state_cursor_value = stream_state.get(self.cursor_field)
            latest_cursor = stream_state_cursor_value or self._start_ts
            if latest_cursor:
                latest_cursor = pendulum.parse(latest_cursor)
                if stream_state_cursor_value:
                    latest_cursor = max(latest_cursor, pendulum.parse(stream_state_cursor_value))
                latest_cursor = min(latest_cursor, pendulum.now())
                params["filter"] = f"greater-than({self.cursor_field},{latest_cursor.isoformat()})"
            params["sort"] = self.cursor_field
        return params


class SemiIncrementalKlaviyoStream(KlaviyoStream, ABC):
    """Base class for all streams that have a cursor field, but underlying API does not support either sorting or filtering"""

    @property
    @abstractmethod
    def cursor_field(self) -> Union[str, List[str]]:
        """
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.
        :return str: The name of the cursor field.
        """

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        stream_state = stream_state or {}
        starting_point = stream_state.get(self.cursor_field, self._start_ts)
        for record in super().read_records(
            sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
        ):
            if starting_point and record[self.cursor_field] > starting_point or not starting_point:
                yield record


class ArchivedRecordsStream(IncrementalKlaviyoStream):
    def __init__(self, path: str, cursor_field: str, start_date: Optional[str] = None, api_revision: Optional[str] = None, **kwargs):
        super().__init__(start_date=start_date, **kwargs)
        self._path = path
        self._cursor_field = cursor_field
        if api_revision:
            self.api_revision = api_revision

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return self._cursor_field

    def path(self, **kwargs) -> str:
        return self._path

    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs):
        archived_stream_state = stream_state.get("archived") if stream_state else None
        params = super().request_params(archived_stream_state, next_page_token, **kwargs)
        archived_filter = "equals(archived,true)"
        if "filter" in params:
            params["filter"] = f"and({params['filter']},{archived_filter})"
        else:
            params["filter"] = archived_filter
        return params


class ArchivedRecordsMixin(IncrementalKlaviyoStream, ABC):
    """A mixin class which should be used when archived records need to be read"""

    @property
    def archived_campaigns(self) -> ArchivedRecordsStream:
        return ArchivedRecordsStream(self.path(), self.cursor_field, self._start_ts, self.api_revision, api_key=self._api_key)

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Extend the stream state with `archived` property to store such records' state separately from the stream state
        """

        if latest_record.get("attributes", {}).get("archived", False):
            current_archived_stream_cursor_value = current_stream_state.get("archived", {}).get(self.cursor_field, self._start_ts)
            latest_archived_cursor = pendulum.parse(latest_record[self.cursor_field])
            if current_archived_stream_cursor_value:
                latest_archived_cursor = max(latest_archived_cursor, pendulum.parse(current_archived_stream_cursor_value))
            current_stream_state["archived"] = {self.cursor_field: latest_archived_cursor.isoformat()}
            return current_stream_state
        else:
            return super().get_updated_state(current_stream_state, latest_record)

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        yield from super().read_records(sync_mode, cursor_field, stream_slice, stream_state)
        yield from self.archived_campaigns.read_records(sync_mode, cursor_field, stream_slice, stream_state)


class Profiles(IncrementalKlaviyoStream):
    """Docs: https://developers.klaviyo.com/en/v2023-02-22/reference/get_profiles"""

    cursor_field = "updated"
    api_revision = "2023-02-22"
    page_size = 100
    state_checkpoint_interval = 100  # API can return maximum 100 records per page

    def path(self, *args, next_page_token: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return "profiles"


class Campaigns(ArchivedRecordsMixin, IncrementalKlaviyoStream):
    """Docs: https://developers.klaviyo.com/en/v2023-06-15/reference/get_campaigns"""

    cursor_field = "updated_at"
    api_revision = "2023-06-15"

    def path(self, **kwargs) -> str:
        return "campaigns"


class Lists(SemiIncrementalKlaviyoStream):
    """Docs: https://developers.klaviyo.com/en/reference/get_lists"""

    max_retries = 10
    cursor_field = "updated"

    def path(self, **kwargs) -> str:
        return "lists"


class GlobalExclusions(Profiles):
    """
    Docs: https://developers.klaviyo.com/en/v2023-02-22/reference/get_profiles
    This stream takes data from 'profiles' endpoint, but suppressed records only
    """

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for record in super().parse_response(response, **kwargs):
            if not record["attributes"].get("subscriptions", {}).get("email", {}).get("marketing", {}).get("suppressions"):
                continue
            yield record


class Metrics(SemiIncrementalKlaviyoStream):
    """Docs: https://developers.klaviyo.com/en/reference/get_metrics"""

    cursor_field = "updated"

    def path(self, **kwargs) -> str:
        return "metrics"


class Events(IncrementalKlaviyoStream):
    """Docs: https://developers.klaviyo.com/en/reference/get_events"""

    cursor_field = "datetime"
    state_checkpoint_interval = 200  # API can return maximum 200 records per page

    def path(self, **kwargs) -> str:
        return "events"


class Flows(ArchivedRecordsMixin, IncrementalKlaviyoStream):
    """Docs: https://developers.klaviyo.com/en/reference/get_flows"""

    cursor_field = "updated"
    state_checkpoint_interval = 50  # API can return maximum 50 records per page

    def path(self, **kwargs) -> str:
        return "flows"


class EmailTemplates(IncrementalKlaviyoStream):
    """Docs: https://developers.klaviyo.com/en/reference/get_templates"""

    cursor_field = "updated"
    state_checkpoint_interval = 10  # API can return maximum 10 records per page

    def path(self, **kwargs) -> str:
        return "templates"
