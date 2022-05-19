#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import datetime
import urllib
from abc import ABC, abstractmethod
from asyncio import streams
from asyncio.log import logger
from cgi import parse_multipart
from distutils.command.config import config
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from pytest import param


class SendgridStream(HttpStream, ABC):
    url_base = "https://api.sendgrid.com/v3/"
    primary_key = "id"
    limit = 50
    data_field = None
    
    # def backoff_time(self, response: requests.Response) -> Optional[float]:
    #     """This method is called if we run into the rate limit.
    #     Sendgrid puts the retry time in the `X-RateLimit-Reset` response header so we
    #     we return that value. If the response is anything other than a 429 (e.g: 5XX)
    #     fall back on default retry behavior.
    #     Rate Limits Docs: https://docs.sendgrid.com/api-reference/how-to-use-the-sendgrid-v3-api/rate-limits"""

    #     backoff_time = response.headers.get("X-RateLimit-Reset")
    #     if backoff_time is not None:
    #       return float(backoff_time)

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

   # def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
       # params = super().request_params(next_page_token=next_page_token, **kwargs)
        params = super().request_params(stream_state, stream_slice, next_page_token, **kwargs)
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


class ChildStreamMixin(HttpSubStream):
    # parent_stream_class: Optional[SendgridStream] = None
    # filter_field: str

    def __init__(self, authenticator: str , start_time: int, parent: object, **kwargs):
       # super().__init__(**kwargs)
        self._authenticator = authenticator
        self._start_time = start_time
        self._parent = parent

    def stream_slices(self, sync_mode, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        for item in self._parent(authenticator=self._authenticator, start_time=self._start_time).read_records(sync_mode=sync_mode):
            print (item)
            yield {"id": item["msg_id"]}    


    # def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
    #     stream_instance = self.parent_stream_class(authenticator=self.parent_stream_class._authenticator, start_time=self.parent_stream_class.cursor_field)
    #     print (stream_instance)
    #     stream_slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh, cursor_field=stream_instance.cursor_field)
    #     print (stream_slices)
    #     for stream_slice in stream_slices:
    #         for item in stream_instance.read_records(
    #             sync_mode=SyncMode.full_refresh, stream_slice=stream_slice, cursor_field=stream_instance.cursor_field
    #         ):
    #             yield {"id": item[self.filter_field]}    


class SendgridStreamIncrementalMixin(HttpStream, ABC):
    cursor_field = "created"
   # time_filter_template = "%Y-%m-%dT%H:%M:%SZ"

    def __init__(self, start_time: int, authenticator: str , **kwargs):
        super().__init__(**kwargs)
        self._start_time = start_time
        self._authenticator = authenticator

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_benchmark, current_stream_state[self.cursor_field])}
        return {self.cursor_field: latest_benchmark}

   # def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        #params = super().request_params(stream_state=stream_state)
        params = super().request_params(stream_state, stream_slice, next_page_token, **kwargs)
        start_time = self._start_time
        if stream_state.get(self.cursor_field):
            start_time = stream_state[self.cursor_field]
            #datetime.datetime.strptime(stream_state[self.cursor_field],self.time_filter_template)
            # int(round(curr_dt.timestamp()))
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

  #  def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(next_page_token=next_page_token, **kwargs)
        params["generations"] = "legacy,dynamic"
        return params

    @staticmethod
    def initial_path() -> str:
        return "templates"

class Messages(SendgridStreamOffsetPagination, SendgridStreamIncrementalMixin):
    """
    https://docs.sendgrid.com/api-reference/e-mail-activity/filter-all-messages
    """
    data_field = "messages"
    cursor_field = "last_event_time"
    limit = 1000

    @property
    def use_cache(self) -> bool:
        return True

    
    # def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        time_filter_template = "%Y-%m-%dT%H:%M:%SZ"
        params = super().request_params(stream_state, stream_slice, next_page_token, **kwargs)
        # if type(params["start_time"]) == dict:
        #     print(params)
        #     params["authenticator"]=params["start_time"]["authenticator"]
        #     params["start_time"]=params["start_time"]["start_time"]
        # if stream_state:
        #     date_start = int(round(datetime.datetime.strptime(stream_state.get[self.cursor_field],self.time_filter_template).timestamp()))
        # else:
        print (f'INFOOOOOOO: {params["start_time"]}')
        if type(params["start_time"]) == int:
            date_start = datetime.datetime.fromtimestamp(int(params["start_time"])).strftime(time_filter_template)
        else:
            date_start = params["start_time"]
        date_end = datetime.datetime.fromtimestamp(int(params["end_time"])).strftime(time_filter_template)
        queryapi = f'last_event_time BETWEEN TIMESTAMP "{date_start}" AND TIMESTAMP "{date_end}"'
        params['query'] = urllib.parse.quote(queryapi)
        payload_str = "&".join("%s=%s" % (k,v) for k,v in params.items() if k not in ['start_time', 'end_time'])
        print (params)
        return payload_str

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "messages"

class MessagesDetails(SendgridStreamOffsetPagination, ChildStreamMixin):
    """
    https://docs.sendgrid.com/api-reference/e-mail-activity/filter-messages-by-message-id
    """

   # parent_stream_class = Messages
    limit = 1000
   # filter_field = 'msg_id'

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        print (stream_slice)
        return f'messages/{stream_slice["id"]}'

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token, **kwargs)
        params["msg_id"] = stream_slice["id"]
        return params["msg_id"]

    # def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
    #     stream_instance = self.parent_stream_class(authenticator=self.parent_stream_class._authenticator, start_time=self.parent_stream_class.cursor_field)
    #     print (stream_instance)
    #     stream_slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh, cursor_field=stream_instance.cursor_field)
    #     print (stream_slices)
    #     for stream_slice in stream_slices:
    #         for item in stream_instance.read_records(
    #             sync_mode=SyncMode.full_refresh, stream_slice=stream_slice, cursor_field=stream_instance.cursor_field
    #         ):
    #             yield {"id": item[self.filter_field]}    

    # def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
    #     stream_state = stream_state or {}
    #     print (self.cursor_field)
    #     start_date = stream_state.get(tuple(self.cursor_field))
    #     stream_instance = self._parent(authenticator=self._parent._get_authenticator, start_time=start_date)
    #     stream_slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh, cursor_field=stream_instance.cursor_field)
    #     for stream_slice in stream_slices:
    #         for item in stream_instance.read_records(
    #             sync_mode=SyncMode.full_refresh, stream_slice=stream_slice, cursor_field=stream_instance.cursor_field
    #         ):
    #             yield {"msg_id": item["msg_id"]}

# class MessagesTemplate(HttpSubStream, SendgridStream):
#     """
#     https://docs.sendgrid.com/api-reference/transactional-templates/retrieve-a-single-transactional-template
#     """
#     limit = 1000

#     def path(self, stream_slice: Mapping[str, Any], **kwargs):
#         return f"templates/{stream_slice['template_id']}"

#     def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
#         stream_instance = MessagesDetails(authenticator=self.authenticator, parent=Messages)
#         stream_slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh, cursor_field=stream_instance.cursor_field)
#         for stream_slice in stream_slices:
#             for item in stream_instance.read_records(
#                 sync_mode=SyncMode.full_refresh, stream_slice=stream_slice, cursor_field=stream_instance.cursor_field
#             ):
#                 yield {"template_id": item["template_id"]}    


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
