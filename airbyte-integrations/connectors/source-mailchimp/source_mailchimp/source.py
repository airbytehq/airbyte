# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import base64
import math
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import dateutil.parser
import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator
from mailchimp3 import MailChimp


class MailChimpStream(HttpStream, ABC):
    url_base = "https://us2.api.mailchimp.com/3.0/"
    primary_key = "id"
    PAGINATION = 100

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.url_base = url_base #but `us2` can differ as {ds} in docs
        self.current_offset = 0

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        api_data = decoded_response[self.data_field]
        if len(api_data) < self.PAGINATION:
            return {}
        else:
            self.current_offset += self.PAGINATION
            return {"offset": self.current_offset}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:

        params = {"count": self.PAGINATION}

        # Handle pagination by inserting the next page's token in the request parameters
        if next_page_token:
            params.update(next_page_token)
        return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json[self.data_field]


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

        zero_date = datetime(1900, 1, 1)

        current_state = current_stream_state.get(self.cursor_field)
        latest_state = latest_record.get(self.cursor_field)
        if not any([current_state, latest_state]):  # noqa
            return {self.cursor_field: zero_date}

        if not all([current_state, latest_state]):
            nonzero_state = list(filter(bool, [current_state, latest_state]))[0]
            if not isinstance(nonzero_state, datetime):
                nonzero_state = dateutil.parser.isoparse(nonzero_state)
            return {self.cursor_field: nonzero_state}
        else:
            if not isinstance(current_state, datetime):
                current_state = dateutil.parser.isoparse(current_state)
            if not isinstance(latest_state, datetime):
                latest_state = dateutil.parser.isoparse(latest_state)
            max_value = max(latest_state, current_state)
            return {self.cursor_field: max_value}

    def request_params(self, stream_state=None, **kwargs):

        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        default_params = {"sort_field": self.cursor_field, "sort_dir": "ASC"}
        since_value = stream_state.get(self.cursor_field)
        if isinstance(since_value, datetime):
            since_value = since_value.isoformat()
        default_params[f"since_{self.cursor_field}"] = since_value
        params.update(default_params)
        return params


class Lists(IncrementalMailChimpStream):
    cursor_field = "date_created"
    name = "Lists"
    data_field = "lists"

    def path(self, **kwargs) -> str:
        return "lists"


class Campaigns(IncrementalMailChimpStream):
    cursor_field = "create_time"
    name = "Campaigns"
    data_field = "campaigns"

    def path(self, **kwargs) -> str:
        return "campaigns"


class EmailActivity(MailChimpStream):
    cursor_field = "timestamp"
    name = "Email_activity"
    data_field = "emails"

    def stream_slices(self, **kwargs):
        campaign_stream = Campaigns(authenticator=self.authenticator)
        for campaign in campaign_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"campaign_id": campaign["id"]}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        campaign_id = stream_slice["campaign_id"]
        return f"reports/{campaign_id}/email-activity"

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        since_value = stream_state.get(self.cursor_field)
        if since_value:
            if isinstance(since_value, datetime):
                since_value = since_value.isoformat()
            params["since"] = since_value
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        # transform before save
        # [{'campaign_id', 'list_id', 'list_is_active', 'email_id', 'email_address', 'activity[array[object]]', '_links'}] ->
        # -> [[{'campaign_id', 'list_id', 'list_is_active', 'email_id', 'email_address', '**activity[i]', '_links'}, ...]]
        data = response_json[self.data_field]
        for item in data:
            for activity_record in item["activity"]:
                new_record = {k: v for k, v in item.items() if k != "activity"}
                for k, v in activity_record.items():
                    new_record[k] = v
                yield new_record


class HttpBasicAuthenticator(HttpAuthenticator):  # should not placed in this file but we havent it!
    def __init__(self, auth: Tuple[str, str]):
        self.auth = auth

    def get_auth_header(self) -> Mapping[str, str]:
        # origin: resp = requests.get(url, auth=(anystring, 'your_apikey'))
        # -> use Basic Authorization header instead
        auth_string = f"{self.auth[0]}:{self.auth[1]}".encode("utf8")
        b64_encoded = base64.b64encode(auth_string).decode("utf8")
        return {"Authorization": "Basic " + b64_encoded}


class SourceMailchimp(AbstractSource):
    def _setup_properties(self, config: Mapping[str, Any]) -> None:
        if not hasattr(self, "_client"):
            self._client = MailChimp(mc_api=config["apikey"], mc_user=config["username"])
            self.apikey = config["apikey"]
            # MailChimpStream.url_base = self._client.base_url

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            self._setup_properties(config=config)
            self._client.ping.get()
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        self._setup_properties(config=config)
        authenticator = HttpBasicAuthenticator(auth=("anystring", self.apikey))
        streams_ = [Lists(authenticator=authenticator), Campaigns(authenticator=authenticator), EmailActivity(authenticator=authenticator)]

        return streams_
