#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import math
from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream


class MailChimpStream(HttpStream, ABC):
    primary_key = "id"
    page_size = 100

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
        """The responce entry that contains useful data"""
        pass


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

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_state = latest_record.get(self.cursor_field)
        current_state = current_stream_state.get(self.cursor_field) or latest_state
        return {self.cursor_field: max(latest_state, current_state)}

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        default_params = {"sort_field": self.cursor_field, "sort_dir": "ASC"}
        since_value = stream_state.get(self.cursor_field)
        if since_value:
            default_params[f"since_{self.cursor_field}"] = since_value
        params.update(default_params)
        return params


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


class EmailActivity(IncrementalMailChimpStream):
    cursor_field = "timestamp"
    data_field = "emails"
    primary_key = None

    def stream_slices(self, **kwargs):
        campaign_stream = Campaigns(authenticator=self.authenticator)
        for campaign in campaign_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"campaign_id": campaign["id"]}

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

    def request_params(self, stream_state=None, stream_slice: Mapping[str, Any] = None, **kwargs):
        stream_state = stream_state or {}
        params = MailChimpStream.request_params(self, stream_state=stream_state, **kwargs)

        since_value_camp = stream_state.get(stream_slice["campaign_id"])
        if since_value_camp:
            since_value = since_value_camp.get(self.cursor_field)
            if since_value:
                params["since"] = since_value
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        # transform before save
        # [{'campaign_id', 'list_id', 'list_is_active', 'email_id', 'email_address', 'activity[array[object]]', '_links'}] ->
        # -> [[{'campaign_id', 'list_id', 'list_is_active', 'email_id', 'email_address', '**activity[i]', '_links'}, ...]]
        data = response_json[self.data_field]
        for item in data:
            for activity_item in item.pop("activity", []):
                yield {**item, **activity_item}
