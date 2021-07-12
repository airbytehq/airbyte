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

import time
from abc import ABC
from datetime import date, timedelta, datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator, TokenAuthenticator


class IntercomStream(HttpStream, ABC):
    url_base = "https://api.intercom.io/"

    # https://developers.intercom.com/intercom-api-reference/reference#rate-limiting
    rate_limit = 1000  # 1000 queries per hour == 1 req in 3,6 secs

    def __init__(
            self,
            authenticator: HttpAuthenticator,
            start_date: Union[date, str] = None,
            **kwargs,
    ):
        self.start_date = start_date

        super().__init__(authenticator=authenticator)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Accept": "application/json"}

    def _send_request(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response:
        try:
            return super()._send_request(request, request_kwargs)
        except requests.exceptions.HTTPError as e:
            error_message = e.response.text
            if error_message:
                self.logger.error(f"Stream {self.name}: {e.response.status_code} {e.response.reason} - {error_message}")
            raise e

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()
        for data_field in self.data_fields:
            if data_field is not None:
                data = data.get(data_field, [])
        if isinstance(data, list):
            data = data
        elif isinstance(data, dict):
            data = [data]

        for record in data:
            updated_at = record.get("updated_at", 0)
            if updated_at:
                record["updated_at"] = datetime.fromtimestamp(record["updated_at"]).isoformat()  # convert timestamp to datetime string
            yield record

        # wait for 3,6 seconds according to API limit
        time.sleep(3600 / self.rate_limit)


class IncrementalIntercomStream(IntercomStream, ABC):
    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, any]:
        # This method is called once for each record returned from the API to compare the cursor field value in that record with the current state
        # we then return an updated state object. If this is the first time we run a sync or no state was passed, current_stream_state will be None.
        current_stream_state = current_stream_state or {}
        current_stream_state_date = current_stream_state.get("updated_at", str(self.start_date))
        latest_record_date = latest_record.get(self.cursor_field, str(self.start_date))
        return {"updated_at": max(current_stream_state_date, latest_record_date)}


class StreamMixin:
    stream = None

    def stream_slices(self, sync_mode, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        for item in self.stream(authenticator=self.authenticator).read_records(sync_mode=sync_mode):
            yield {"id": item["id"]}

        yield from []


class Admins(IntercomStream):
    """Return list of all admins.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-admins
    Endpoint: https://api.intercom.io/admins
    """

    primary_key = "id"
    data_fields = ["admins"]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "admins"


class Companies(IncrementalIntercomStream):
    """Return list of all companies.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-companies
    Endpoint: https://api.intercom.io/companies
    """

    primary_key = "id"
    data_fields = ["data"]
    cursor_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "companies"


class CompanySegments(StreamMixin, IncrementalIntercomStream):
    """Return list of all company segments.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-attached-segments-1
    Endpoint: https://api.intercom.io/companies/<id>/segments
    """

    primary_key = "id"
    data_fields = ["data"]
    cursor_field = "updated_at"
    stream = Companies

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"/companies/{stream_slice['id']}/segments"


class Conversations(IncrementalIntercomStream):
    """Return list of all conversations.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-conversations
    Endpoint: https://api.intercom.io/conversations
    """

    primary_key = "id"
    data_fields = ["conversations"]
    cursor_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "conversations"


class ConversationParts(StreamMixin, IncrementalIntercomStream):
    """Return list of all conversation parts.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#retrieve-a-conversation
    Endpoint: https://api.intercom.io/conversations/<id>
    """

    primary_key = "id"
    data_fields = ["conversation_parts", "conversation_parts"]
    cursor_field = "updated_at"
    stream = Conversations

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"/conversations/{stream_slice['id']}"


class Segments(IncrementalIntercomStream):
    """Return list of all segments.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-segments
    Endpoint: https://api.intercom.io/segments
    """

    primary_key = "id"
    data_fields = ["segments"]
    cursor_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "segments"


class Contacts(IncrementalIntercomStream):
    """Return list of all contacts.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-contacts
    Endpoint: https://api.intercom.io/contacts
    """

    primary_key = "id"
    data_fields = ["data"]
    cursor_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "contacts"


class DataAttributes(IntercomStream):
    primary_key = "name"
    data_fields = ["data"]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "data_attributes"


class CompanyAttributes(DataAttributes):
    """Return list of all data attributes belonging to a workspace for companies.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-data-attributes
    Endpoint: https://api.intercom.io/data_attributes?model=company
    """

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {"model": "company"}


class ContactAttributes(DataAttributes):
    """Return list of all data attributes belonging to a workspace for contacts.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-data-attributes
    Endpoint: https://api.intercom.io/data_attributes?model=contact
    """

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {"model": "contact"}


class Tags(IntercomStream):
    """Return list of all tags.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-tags-for-an-app
    Endpoint: https://api.intercom.io/tags
    """

    primary_key = "name"
    data_fields = ["data"]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "tags"


class Teams(IntercomStream):
    """Return list of all teams.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-teams
    Endpoint: https://api.intercom.io/teams
    """

    primary_key = "name"
    data_fields = ["teams"]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "teams"


class SourceIntercom(AbstractSource):
    """
    Source Intercom fetch data from messaging platform
    """

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        authenticator = TokenAuthenticator(token=config["access_token"])
        try:
            url = f"{IntercomStream.url_base}/tags"
            auth_headers = {"Accept": "application/json",
                            **authenticator.get_auth_header()}
            session = requests.get(url, headers=auth_headers)
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """

        now = date.today()

        start_date = config.get("start_date")
        if start_date and isinstance(start_date, str):
            start_date = datetime.strptime(config["start_date"], "%Y-%m-%dT%H:%M:%S%z")
        config["start_date"] = start_date or now - timedelta(days=365)  # set to 1 year ago by default

        AirbyteLogger().log("INFO", f"Using start_date: {config['start_date']}")

        auth = TokenAuthenticator(token=config["access_token"])
        return [Admins(authenticator=auth, **config),
                Conversations(authenticator=auth, **config),
                ConversationParts(authenticator=auth, **config),
                CompanySegments(authenticator=auth, **config),
                CompanyAttributes(authenticator=auth, **config),
                ContactAttributes(authenticator=auth, **config),
                Segments(authenticator=auth, **config),
                Contacts(authenticator=auth, **config),
                Companies(authenticator=auth, **config),
                Tags(authenticator=auth, **config),
                Teams(authenticator=auth, **config)]
