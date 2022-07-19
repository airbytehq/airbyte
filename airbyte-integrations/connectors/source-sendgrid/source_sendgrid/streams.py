#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
import urllib
from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import pendulum
import requests
from airbyte_cdk.sources.streams.http import HttpStream


class SendgridStream(HttpStream, ABC):
    url_base = "https://api.sendgrid.com/v3/"
    primary_key = "id"
    limit = 50
    data_field = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        pass

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        json_response = response.json()
        records = json_response.get(self.data_field, []) if self.data_field is not None else json_response

        if records is not None:
            for record in records:
                yield record
        else:
            # TODO sendgrid's API is sending null responses at times. This seems like a bug on the API side, so we're adding
            #  log statements to help reproduce and prevent the connector from failing.
            err_msg = (
                f"Response contained no valid JSON data. Response body: {response.text}\n"
                f"Response status: {response.status_code}\n"
                f"Response body: {response.text}\n"
                f"Response headers: {response.headers}\n"
                f"Request URL: {response.request.url}\n"
                f"Request body: {response.request.body}\n"
            )
            # do NOT print request headers as it contains auth token
            self.logger.info(err_msg)


class SendgridStreamOffsetPagination(SendgridStream):
    offset = 0

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(next_page_token=next_page_token, **kwargs)
        params["limit"] = self.limit
        if next_page_token:
            params.update(**next_page_token)
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        stream_data = response.json()
        if self.data_field:
            stream_data = stream_data[self.data_field]
        if len(stream_data) < self.limit:
            return
        self.offset += self.limit
        return {"offset": self.offset}


class SendgridStreamIncrementalMixin(HttpStream, ABC):
    cursor_field = "created"

    def __init__(self, start_time: int, **kwargs):
        super().__init__(**kwargs)
        self._start_time = start_time

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_benchmark, current_stream_state[self.cursor_field])}
        return {self.cursor_field: latest_benchmark}

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state)
        start_time = self._start_time
        if stream_state.get(self.cursor_field):
            start_time = stream_state[self.cursor_field]
        params.update({"start_time": start_time, "end_time": pendulum.now().int_timestamp})
        return params


class SendgridStreamMetadataPagination(SendgridStream):
    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {}
        if not next_page_token:
            params = {"page_size": self.limit}
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page_url = response.json()["_metadata"].get("next", False)
        if next_page_url:
            return {"next_page_url": next_page_url.replace(self.url_base, "")}

    @staticmethod
    @abstractmethod
    def initial_path() -> str:
        """
        :return: initial path for the API endpoint if no next metadata url found
        """

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        if next_page_token:
            return next_page_token["next_page_url"]
        return self.initial_path()


class Scopes(SendgridStream):
    def path(self, **kwargs) -> str:
        return "scopes"


class Lists(SendgridStreamMetadataPagination):
    data_field = "result"

    @staticmethod
    def initial_path() -> str:
        return "marketing/lists"


class Campaigns(SendgridStreamMetadataPagination):
    data_field = "result"

    @staticmethod
    def initial_path() -> str:
        return "marketing/campaigns"


class Contacts(SendgridStream):
    data_field = "result"

    def path(self, **kwargs) -> str:
        return "marketing/contacts"


class StatsAutomations(SendgridStreamMetadataPagination):
    data_field = "results"

    @staticmethod
    def initial_path() -> str:
        return "marketing/stats/automations"


class Segments(SendgridStream):
    data_field = "results"

    def path(self, **kwargs) -> str:
        return "marketing/segments"


class SingleSends(SendgridStreamMetadataPagination):
    """
    https://docs.sendgrid.com/api-reference/marketing-campaign-stats/get-all-single-sends-stats
    """

    data_field = "results"

    @staticmethod
    def initial_path() -> str:
        return "marketing/stats/singlesends"


class Templates(SendgridStreamMetadataPagination):
    data_field = "result"

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(next_page_token=next_page_token, **kwargs)
        params["generations"] = "legacy,dynamic"
        return params

    @staticmethod
    def initial_path() -> str:
        return "templates"


class Messages(SendgridStream, SendgridStreamIncrementalMixin):
    """
    https://docs.sendgrid.com/api-reference/e-mail-activity/filter-all-messages
    """

    data_field = "messages"
    cursor_field = "last_event_time"
    primary_key = "msg_id"
    limit = 1000

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        time_filter_template = "%Y-%m-%dT%H:%M:%SZ"
        params = super().request_params(stream_state=stream_state, **kwargs)
        if isinstance(params["start_time"], int):
            date_start = datetime.datetime.fromtimestamp(params["start_time"]).strftime(time_filter_template)
        else:
            date_start = params["start_time"]
        date_end = datetime.datetime.fromtimestamp(int(params["end_time"])).strftime(time_filter_template)
        queryapi = f'last_event_time BETWEEN TIMESTAMP "{date_start}" AND TIMESTAMP "{date_end}"'
        params["query"] = urllib.parse.quote(queryapi)
        params["limit"] = self.limit
        payload_str = "&".join("%s=%s" % (k, v) for k, v in params.items() if k not in ["start_time", "end_time"])
        return payload_str

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "messages"


class GlobalSuppressions(SendgridStreamOffsetPagination, SendgridStreamIncrementalMixin):
    primary_key = "email"

    def path(self, **kwargs) -> str:
        return "suppression/unsubscribes"


class SuppressionGroups(SendgridStream):
    def path(self, **kwargs) -> str:
        return "asm/groups"


class SuppressionGroupMembers(SendgridStreamOffsetPagination):
    primary_key = "group_id"

    def path(self, **kwargs) -> str:
        return "asm/suppressions"


class Blocks(SendgridStreamOffsetPagination, SendgridStreamIncrementalMixin):
    primary_key = "email"

    def path(self, **kwargs) -> str:
        return "suppression/blocks"


class Bounces(SendgridStream, SendgridStreamIncrementalMixin):
    primary_key = "email"

    def path(self, **kwargs) -> str:
        return "suppression/bounces"


class InvalidEmails(SendgridStreamOffsetPagination, SendgridStreamIncrementalMixin):
    primary_key = "email"

    def path(self, **kwargs) -> str:
        return "suppression/invalid_emails"


class SpamReports(SendgridStreamOffsetPagination, SendgridStreamIncrementalMixin):
    primary_key = "email"

    def path(self, **kwargs) -> str:
        return "suppression/spam_reports"
