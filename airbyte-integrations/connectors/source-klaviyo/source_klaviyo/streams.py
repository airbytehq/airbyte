#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import urllib.parse
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.core import CheckpointMixin, StreamData
from airbyte_cdk.sources.streams.http import HttpStream
from requests import Response

from .availability_strategy import KlaviyoAvailabilityStrategy
from .exceptions import KlaviyoBackoffError


class KlaviyoStream(HttpStream, CheckpointMixin, ABC):
    """Base stream for api version v2023-10-15"""

    url_base = "https://a.klaviyo.com/api/"
    primary_key = "id"
    page_size = None
    api_revision = "2023-10-15"

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    def __init__(self, api_key: str, start_date: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._api_key = api_key
        self._start_ts = start_date
        if not hasattr(self, "_state"):
            self._state = {}

    @property
    def availability_strategy(self) -> Optional[AvailabilityStrategy]:
        return KlaviyoAvailabilityStrategy()

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {
            "Accept": "application/json",
            "Revision": self.api_revision,
            "Authorization": f"Klaviyo-API-Key {self._api_key}",
        }

    def next_page_token(self, response: Response) -> Optional[Mapping[str, Any]]:
        """
        This method should return a Mapping (e.g: dict) containing whatever information
        required to make paginated requests.

        Klaviyo uses cursor-based pagination https://developers.klaviyo.com/en/reference/api_overview#pagination
        This method returns the params in the pre-constructed url nested in links[next]
        """

        decoded_response = response.json()

        next_page_link = decoded_response.get("links", {}).get("next")
        if not next_page_link:
            return None

        next_url = urllib.parse.urlparse(next_page_link)
        return {str(k): str(v) for (k, v) in urllib.parse.parse_qsl(next_url.query)}

    def request_params(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        # If next_page_token is set, all the parameters are already provided
        if next_page_token:
            return next_page_token
        else:
            return {"page[size]": self.page_size} if self.page_size else {}

    def parse_response(self, response: Response, **kwargs) -> Iterable[Mapping]:
        """Return an iterable containing each record in the response"""

        response_json = response.json()
        for record in response_json.get("data", []):  # API returns records in a container array "data"
            record = self.map_record(record)
            yield record

    def map_record(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """Subclasses can override this to apply custom mappings to a record"""

        record[self.cursor_field] = record["attributes"][self.cursor_field]
        return record

    def _get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record.
        This typically compared the cursor_field from the latest record and the current state and picks
        the 'most' recent cursor. This is how a stream's state is determined.
        Required for incremental.
        """

        current_stream_cursor_value = current_stream_state.get(self.cursor_field, self._start_ts)
        latest_cursor = pendulum.parse(latest_record[self.cursor_field])
        if current_stream_cursor_value:
            latest_cursor = max(latest_cursor, pendulum.parse(current_stream_cursor_value))
        current_stream_state[self.cursor_field] = latest_cursor.isoformat()
        return current_stream_state

    def backoff_time(self, response: Response) -> Optional[float]:
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

        current_state = self.state or {}
        try:
            for record in super().read_records(sync_mode, cursor_field, stream_slice, current_state):
                self.state = self._get_updated_state(current_state, record)
                yield record

        except KlaviyoBackoffError as e:
            self.logger.warning(repr(e))


class IncrementalKlaviyoStream(KlaviyoStream, ABC):
    """Base class for all incremental streams, requires cursor_field to be declared"""

    @property
    @abstractmethod
    def cursor_field(self) -> Union[str, List[str]]:
        """
        Override to return the cursor field used by this stream e.g: an API entity might always use
        created_at as the cursor field. This is usually id or date based. This field's presence tells the framework
        this in an incremental stream. Required for incremental.
        :return str: The name of the cursor field.
        """

    def request_params(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        """Add incremental filters"""

        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

        if not params.get("filter"):
            stream_state_cursor_value = stream_state.get(self.cursor_field)
            latest_cursor = stream_state_cursor_value or self._start_ts
            if latest_cursor:
                latest_cursor = pendulum.parse(latest_cursor)
                if stream_state_cursor_value:
                    latest_cursor = max(latest_cursor, pendulum.parse(stream_state_cursor_value))
                # Klaviyo API will throw an error if the request filter is set too close to the current time.
                # Setting a minimum value of at least 3 seconds from the current time ensures this will never happen,
                # and allows our 'abnormal_state' acceptance test to pass.
                latest_cursor = min(latest_cursor, pendulum.now().subtract(seconds=3))
                params["filter"] = f"greater-than({self.cursor_field},{latest_cursor.isoformat()})"
            params["sort"] = self.cursor_field
        return params


class IncrementalKlaviyoStreamWithArchivedRecords(IncrementalKlaviyoStream, ABC):
    """A base class which should be used when archived records need to be read"""

    def _get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
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
            return super()._get_updated_state(current_stream_state, latest_record)

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        return [{"archived": flag} for flag in (False, True)]

    def request_params(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        state = (stream_state or {}).get("archived") if stream_slice.get("archived") else stream_state
        params = super().request_params(stream_state=state, stream_slice=stream_slice, next_page_token=next_page_token)
        if stream_slice.get("archived"):
            archived_filter = "equals(archived,true)"
            if "filter" in params and archived_filter not in params["filter"]:
                params["filter"] = f"and({params['filter']},{archived_filter})"
            elif "filter" not in params:
                params["filter"] = archived_filter
        return params


class Campaigns(IncrementalKlaviyoStreamWithArchivedRecords):
    """Docs: https://developers.klaviyo.com/en/v2023-06-15/reference/get_campaigns"""

    cursor_field = "updated_at"
    api_revision = "2023-06-15"

    def path(self, **kwargs) -> str:
        return "campaigns"


class CampaignsDetailed(Campaigns):
    raise_on_http_errors = False

    def parse_response(self, response: Response, **kwargs: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        for record in super().parse_response(response, **kwargs):
            yield self._transform_record(record)

    def _transform_record(self, record: Mapping[str, Any]) -> Mapping[str, Any]:
        self._set_recipient_count(record)
        self._set_campaign_message(record)
        return record

    def _set_recipient_count(self, record: Mapping[str, Any]) -> None:
        campaign_id = record["id"]
        recipient_count_request = self._create_prepared_request(
            path=f"{self.url_base}campaign-recipient-estimations/{campaign_id}",
            headers=self.request_headers(),
        )
        recipient_count_response = self._send_request(recipient_count_request, {})
        record["estimated_recipient_count"] = (
            recipient_count_response.json().get("data", {}).get("attributes", {}).get("estimated_recipient_count", 0)
        )

    def _set_campaign_message(self, record: Mapping[str, Any]) -> None:
        message_id = record.get("attributes", {}).get("message")
        if message_id:
            campaign_message_request = self._create_prepared_request(
                path=f"{self.url_base}campaign-messages/{message_id}", headers=self.request_headers()
            )
            campaign_message_response = self._send_request(campaign_message_request, {})
            record["campaign_message"] = campaign_message_response.json().get("data")


class Flows(IncrementalKlaviyoStreamWithArchivedRecords):
    """Docs: https://developers.klaviyo.com/en/reference/get_flows"""

    cursor_field = "updated"
    state_checkpoint_interval = 50  # API can return maximum 50 records per page

    def path(self, **kwargs) -> str:
        return "flows"
