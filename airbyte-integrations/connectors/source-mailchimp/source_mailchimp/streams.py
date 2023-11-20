#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import math
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http import HttpStream

logger = logging.getLogger("airbyte")


class MailChimpStream(HttpStream, ABC):
    primary_key = "id"
    page_size = 1000

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_offset = 0
        self.data_center = kwargs["authenticator"].data_center

    @property
    def url_base(self) -> str:
        return f"https://{self.data_center}.api.mailchimp.com/3.0/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        api_data = decoded_response[self.data_field]
        if len(api_data) < self.page_size:
            self.current_offset = 0
            return None
        else:
            self.current_offset += self.page_size
            return {"offset": self.current_offset}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:

        params = {"count": self.page_size}

        # Handle pagination by inserting the next page's token in the request parameters
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json[self.data_field]

    @property
    @abstractmethod
    def data_field(self) -> str:
        """The response entry that contains useful data"""
        pass

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[StreamData]:
        try:
            yield from super().read_records(
                sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )
        except requests.exceptions.JSONDecodeError:
            logger.error(f"Unknown error while reading stream {self.name}. Response cannot be read properly. ")


class IncrementalMailChimpStream(MailChimpStream, ABC):
    state_checkpoint_interval = math.inf

    @property
    @abstractmethod
    def cursor_field(self) -> str:
        """
        Defining a cursor field indicates that a stream is incremental, so any incremental stream must extend this class
        and define a cursor field.
        """
        pass

    @property
    def filter_field(self):
        return f"since_{self.cursor_field}"

    @property
    def sort_field(self):
        return self.cursor_field

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_state = latest_record.get(self.cursor_field)
        current_state = current_stream_state.get(self.cursor_field) or latest_state
        return {self.cursor_field: max(latest_state, current_state)}

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        slice_ = {}
        stream_state = stream_state or {}
        cursor_value = stream_state.get(self.cursor_field)
        if cursor_value:
            slice_[self.filter_field] = cursor_value
        yield slice_

    def request_params(self, stream_state=None, stream_slice=None, **kwargs):
        stream_state = stream_state or {}
        stream_slice = stream_slice or {}
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, **kwargs)
        default_params = {"sort_field": self.sort_field, "sort_dir": "ASC", **stream_slice}
        params.update(default_params)
        return params


class MailChimpListSubStream(IncrementalMailChimpStream):
    """
    Base class for incremental Mailchimp streams that are children of the Lists stream.
    """

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        stream_state = stream_state or {}
        parent = Lists(authenticator=self.authenticator).read_records(sync_mode=SyncMode.full_refresh)
        for slice in parent:
            yield {"list_id": slice["id"]}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        list_id = stream_slice.get("list_id")
        return f"lists/{list_id}/{self.data_field}"

    def request_params(self, stream_state=None, stream_slice=None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, **kwargs)

        # Exclude the _links field, as it is not user-relevant data
        params["exclude_fields"] = f"{self.data_field}._links"

        # Get the current state value for this list_id, if it exists
        # Then, use the value in state to filter the request
        current_slice = stream_slice.get("list_id")
        filter_date = stream_state.get(current_slice)
        if filter_date:
            params[self.filter_field] = filter_date.get(self.cursor_field)
        return params

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        current_stream_state = current_stream_state or {}
        list_id = latest_record.get("list_id")
        latest_cursor_value = latest_record.get(self.cursor_field)

        # Get the current state value for this list, if it exists
        list_state = current_stream_state.get(list_id, {})
        current_cursor_value = list_state.get(self.cursor_field, latest_cursor_value)

        # Update the cursor value and set it in state
        updated_cursor_value = max(current_cursor_value, latest_cursor_value)
        current_stream_state[list_id] = {self.cursor_field: updated_cursor_value}

        return current_stream_state


class Lists(IncrementalMailChimpStream):
    cursor_field = "date_created"
    data_field = "lists"

    def path(self, **kwargs) -> str:
        return "lists"


class Campaigns(IncrementalMailChimpStream):
    cursor_field = "create_time"
    data_field = "campaigns"

    def path(self, **kwargs) -> str:
        return "campaigns"


class Automations(IncrementalMailChimpStream):
    """Doc Link: https://mailchimp.com/developer/marketing/api/automation/get-automation-info/"""

    cursor_field = "create_time"
    data_field = "automations"

    def path(self, **kwargs) -> str:
        return "automations"


class EmailActivity(IncrementalMailChimpStream):
    cursor_field = "timestamp"
    filter_field = "since"
    sort_field = "create_time"
    data_field = "emails"
    primary_key = ["timestamp", "email_id", "action"]

    def __init__(self, campaign_id: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.campaign_id = campaign_id

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        stream_state = stream_state or {}
        if self.campaign_id:
            # this is a workaround to speed up SATs and enable incremental tests
            campaigns = [{"id": self.campaign_id}]
        else:
            campaigns = Campaigns(authenticator=self.authenticator).read_records(sync_mode=SyncMode.full_refresh)
        for campaign in campaigns:
            slice_ = {"campaign_id": campaign["id"]}
            cursor_value = stream_state.get(campaign["id"], {}).get(self.cursor_field)
            if cursor_value:
                slice_[self.filter_field] = cursor_value
            yield slice_

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        campaign_id = stream_slice["campaign_id"]
        return f"reports/{campaign_id}/email-activity"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the campaign_id and cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        campaign_id = latest_record.get("campaign_id")
        latest_cursor_value = latest_record.get(self.cursor_field)
        current_stream_state = current_stream_state or {}
        current_state = current_stream_state.get(campaign_id) if current_stream_state else None
        if current_state:
            current_state = current_state.get(self.cursor_field)
        current_state_value = current_state or latest_cursor_value
        max_value = max(current_state_value, latest_cursor_value)
        new_value = {self.cursor_field: max_value}

        current_stream_state[campaign_id] = new_value
        return current_stream_state

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        try:
            response_json = response.json()
        except requests.exceptions.JSONDecodeError:
            logger.error(f"Response returned with {response.status_code=}, {response.content=}")
            response_json = {}
        # transform before save
        # [{'campaign_id', 'list_id', 'list_is_active', 'email_id', 'email_address', 'activity[array[object]]', '_links'}] ->
        # -> [[{'campaign_id', 'list_id', 'list_is_active', 'email_id', 'email_address', '**activity[i]', '_links'}, ...]]
        data = response_json.get(self.data_field, [])
        for item in data:
            for activity_item in item.pop("activity", []):
                yield {**item, **activity_item}


class ListMembers(MailChimpListSubStream):
    """
    Get information about members in a specific Mailchimp list.
    Docs link: https://mailchimp.com/developer/marketing/api/list-members/list-members-info/
    """

    cursor_field = "last_changed"
    data_field = "members"


class Reports(IncrementalMailChimpStream):
    cursor_field = "send_time"
    data_field = "reports"

    @staticmethod
    def remove_empty_datetime_fields(record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        In some cases, the 'clicks.last_click' and 'opens.last_open' fields are returned as an empty string,
        which causes validation errors on the `date-time` format.
        To avoid this, we remove the fields if they are empty.
        """
        clicks = record.get("clicks", {})
        opens = record.get("opens", {})
        if not clicks.get("last_click"):
            clicks.pop("last_click", None)
        if not opens.get("last_open"):
            opens.pop("last_open", None)
        return record

    def path(self, **kwargs) -> str:
        return "reports"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response = super().parse_response(response, **kwargs)
        for record in response:
            yield self.remove_empty_datetime_fields(record)


class Segments(MailChimpListSubStream):
    """
    Get information about all available segments for a specific list.
    Docs link: https://mailchimp.com/developer/marketing/api/list-segments/list-segments/
    """

    cursor_field = "updated_at"
    data_field = "segments"


class Unsubscribes(IncrementalMailChimpStream):
    """
    List of members who have unsubscribed from a specific campaign.
    Docs link: https://mailchimp.com/developer/marketing/api/unsub-reports/list-unsubscribed-members/
    """

    cursor_field = "timestamp"
    data_field = "unsubscribes"
    # There is no unique identifier for unsubscribes, so we use a composite key
    # consisting of the campaign_id, email_id, and timestamp.
    primary_key = ["campaign_id", "email_id", "timestamp"]

    def __init__(self, campaign_id: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.campaign_id = campaign_id

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:

        if self.campaign_id:
            # Similar to EmailActivity stream, this is a workaround to speed up SATs
            # and enable incremental tests by reading from a single campaign
            campaigns = [{"id": self.campaign_id}]
        else:
            campaigns = Campaigns(authenticator=self.authenticator).read_records(sync_mode=SyncMode.full_refresh)
        for campaign in campaigns:
            yield {"campaign_id": campaign["id"]}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        campaign_id = stream_slice.get("campaign_id")
        return f"reports/{campaign_id}/unsubscribed"

    def request_params(self, stream_state=None, stream_slice=None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, **kwargs)
        # Exclude the _links field, as it is not user-relevant data
        params["exclude_fields"] = "unsubscribes._links"
        return params

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:

        response = super().parse_response(response, **kwargs)

        # Unsubscribes endpoint does not support sorting, so we need to filter out records that are older than the current state
        for record in response:
            current_cursor_value = stream_state.get(record.get("campaign_id"), {}).get(self.cursor_field)
            record_cursor_value = record.get(self.cursor_field)
            if current_cursor_value is None or record_cursor_value >= current_cursor_value:
                yield record

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        current_stream_state = current_stream_state or {}
        campaign_id = latest_record.get("campaign_id")
        latest_cursor_value = latest_record.get(self.cursor_field)

        # Get the current state value for this campaign, if it exists
        campaign_state = current_stream_state.get(campaign_id, {})
        current_cursor_value = campaign_state.get(self.cursor_field, latest_cursor_value)

        # Update the cursor value and set it in state
        updated_cursor_value = max(current_cursor_value, latest_cursor_value)
        current_stream_state[campaign_id] = {self.cursor_field: updated_cursor_value}
        return current_stream_state
