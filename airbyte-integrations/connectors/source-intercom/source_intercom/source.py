#
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
#

import time
from abc import ABC
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator, TokenAuthenticator


class IntercomStream(HttpStream, ABC):
    url_base = "https://api.intercom.io/"

    # https://developers.intercom.com/intercom-api-reference/reference#rate-limiting
    queries_per_minute = 1000  # 1000 queries per minute == 16.67 req per sec

    primary_key = "id"
    data_fields = ["data"]

    def __init__(
        self,
        authenticator: HttpAuthenticator,
        start_date: str = None,
        **kwargs,
    ):
        self.start_date = start_date

        super().__init__(authenticator=authenticator)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Abstract method of HttpStream - should be overwritten.
        Returning None means there are no more pages to read in response.
        """

        next_page = response.json().get("pages", {}).get("next")

        if next_page:
            return {"starting_after": next_page["starting_after"]}
        else:
            return None

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = {}
        if next_page_token:
            params.update(**next_page_token)
        return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"Accept": "application/json"}

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        try:
            yield from super().read_records(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            error_message = e.response.text
            if error_message:
                self.logger.error(f"Stream {self.name}: {e.response.status_code} " f"{e.response.reason} - {error_message}")
            raise e

    def get_data(self, response: requests.Response) -> List:
        data = response.json()

        for data_field in self.data_fields:
            if data and isinstance(data, dict):
                data = data.get(data_field, [])

        if isinstance(data, list):
            data = data
        elif isinstance(data, dict):
            data = [data]

        return data

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        data = self.get_data(response)

        for record in data:
            yield record

        # This is probably overkill because the request itself likely took more
        # than the rate limit, but keep it just to be safe.
        time.sleep(60.0 / self.queries_per_minute)


class IncrementalIntercomStream(IntercomStream, ABC):
    cursor_field = "updated_at"

    def filter_by_state(self, stream_state: Mapping[str, Any] = None, record: Mapping[str, Any] = None) -> Iterable:
        """
        Endpoint does not provide query filtering params, but they provide us
        updated_at field in most cases, so we used that as incremental filtering
        during the slicing.
        """

        if not stream_state or record[self.cursor_field] >= stream_state.get(self.cursor_field):
            yield record

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        record = super().parse_response(response, stream_state, **kwargs)

        for record in record:
            updated_at = record.get(self.cursor_field)

            if updated_at:
                record[self.cursor_field] = datetime.fromtimestamp(
                    record[self.cursor_field]
                ).isoformat()  # convert timestamp to datetime string

            yield from self.filter_by_state(stream_state=stream_state, record=record)

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, any]:
        """
        This method is called once for each record returned from the API to
        compare the cursor field value in that record with the current state
        we then return an updated state object. If this is the first time we
        run a sync or no state was passed, current_stream_state will be None.
        """

        current_stream_state = current_stream_state or {}

        current_stream_state_date = current_stream_state.get(self.cursor_field, self.start_date)
        latest_record_date = latest_record.get(self.cursor_field, self.start_date)

        return {self.cursor_field: max(current_stream_state_date, latest_record_date)}


class ChildStreamMixin:
    parent_stream_class: Optional[IntercomStream] = None

    def stream_slices(self, sync_mode, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        for item in self.parent_stream_class(authenticator=self.authenticator, start_date=self.start_date).read_records(
            sync_mode=sync_mode
        ):
            yield {"id": item["id"]}

        yield from []


class Admins(IntercomStream):
    """Return list of all admins.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-admins
    Endpoint: https://api.intercom.io/admins
    """

    data_fields = ["admins"]

    def path(self, **kwargs) -> str:
        return "admins"


class Companies(IncrementalIntercomStream):
    """Return list of all companies.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#iterating-over-all-companies
    Endpoint: https://api.intercom.io/companies/scroll
    """

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """For reset scroll needs to iterate pages untill the last.
        Another way need wait 1 min for the scroll to expire to get a new list for companies segments."""

        data = response.json().get("data")

        if data:
            return {"scroll_param": response.json()["scroll_param"]}
        else:
            return None

    def path(self, **kwargs) -> str:
        return "companies/scroll"


class CompanySegments(ChildStreamMixin, IncrementalIntercomStream):
    """Return list of all company segments.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-attached-segments-1
    Endpoint: https://api.intercom.io/companies/<id>/segments
    """

    parent_stream_class = Companies

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"/companies/{stream_slice['id']}/segments"


class Conversations(IncrementalIntercomStream):
    """Return list of all conversations.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-conversations
    Endpoint: https://api.intercom.io/conversations
    """

    data_fields = ["conversations"]

    def path(self, **kwargs) -> str:
        return "conversations"


class ConversationParts(ChildStreamMixin, IncrementalIntercomStream):
    """Return list of all conversation parts.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#retrieve-a-conversation
    Endpoint: https://api.intercom.io/conversations/<id>
    """

    data_fields = ["conversation_parts", "conversation_parts"]
    parent_stream_class = Conversations

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"/conversations/{stream_slice['id']}"


class Segments(IncrementalIntercomStream):
    """Return list of all segments.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-segments
    Endpoint: https://api.intercom.io/segments
    """

    data_fields = ["segments"]

    def path(self, **kwargs) -> str:
        return "segments"


class Contacts(IncrementalIntercomStream):
    """Return list of all contacts.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-contacts
    Endpoint: https://api.intercom.io/contacts
    """

    def path(self, **kwargs) -> str:
        return "contacts"


class DataAttributes(IntercomStream):
    primary_key = "name"

    def path(self, **kwargs) -> str:
        return "data_attributes"


class CompanyAttributes(DataAttributes):
    """Return list of all data attributes belonging to a workspace for companies.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-data-attributes
    Endpoint: https://api.intercom.io/data_attributes?model=company
    """

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        return {"model": "company"}


class ContactAttributes(DataAttributes):
    """Return list of all data attributes belonging to a workspace for contacts.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-data-attributes
    Endpoint: https://api.intercom.io/data_attributes?model=contact
    """

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        return {"model": "contact"}


class Tags(IntercomStream):
    """Return list of all tags.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-tags-for-an-app
    Endpoint: https://api.intercom.io/tags
    """

    primary_key = "name"

    def path(self, **kwargs) -> str:
        return "tags"


class Teams(IntercomStream):
    """Return list of all teams.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-teams
    Endpoint: https://api.intercom.io/teams
    """

    primary_key = "name"
    data_fields = ["teams"]

    def path(self, **kwargs) -> str:
        return "teams"


class SourceIntercom(AbstractSource):
    """
    Source Intercom fetch data from messaging platform.
    """

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        authenticator = TokenAuthenticator(token=config["access_token"])
        try:
            url = f"{IntercomStream.url_base}/tags"
            auth_headers = {"Accept": "application/json", **authenticator.get_auth_header()}
            session = requests.get(url, headers=auth_headers)
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        AirbyteLogger().log("INFO", f"Using start_date: {config['start_date']}")

        auth = TokenAuthenticator(token=config["access_token"])
        return [
            Admins(authenticator=auth, **config),
            Companies(authenticator=auth, **config),
            CompanySegments(authenticator=auth, **config),
            Conversations(authenticator=auth, **config),
            ConversationParts(authenticator=auth, **config),
            Contacts(authenticator=auth, **config),
            CompanyAttributes(authenticator=auth, **config),
            ContactAttributes(authenticator=auth, **config),
            Segments(authenticator=auth, **config),
            Tags(authenticator=auth, **config),
            Teams(authenticator=auth, **config),
        ]
