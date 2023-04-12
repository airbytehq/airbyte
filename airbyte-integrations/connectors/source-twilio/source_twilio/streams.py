#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union
from urllib.parse import parse_qsl, urlparse

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from pendulum.datetime import DateTime
from requests.auth import AuthBase

TWILIO_API_URL_BASE = "https://api.twilio.com"
TWILIO_API_URL_BASE_VERSIONED = f"{TWILIO_API_URL_BASE}/2010-04-01/"
TWILIO_MONITOR_URL_BASE = "https://monitor.twilio.com/v1/"
TWILIO_STUDIO_API_BASE = "https://studio.twilio.com/v1/"
TWILIO_CONVERSATIONS_URL_BASE = "https://conversations.twilio.com/v1/"


class TwilioStream(HttpStream, ABC):
    url_base = TWILIO_API_URL_BASE
    primary_key = "sid"
    page_size = 1000
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization)

    @property
    def data_field(self):
        return self.name

    @property
    def changeable_fields(self):
        """
        :return list of changeable fields that should be removed from the records
        """
        return []

    @property
    def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
        return None

    def path(self, **kwargs):
        return f"{self.name.title()}.json"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        stream_data = response.json()
        next_page_uri = stream_data.get("next_page_uri")
        if next_page_uri:
            next_url = urlparse(next_page_uri)
            next_page_params = dict(parse_qsl(next_url.query))
            return next_page_params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        records = response.json().get(self.data_field, [])
        if self.changeable_fields:
            for record in records:
                for field in self.changeable_fields:
                    record.pop(field, None)
                    yield record
        yield from records

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """This method is called if we run into the rate limit.
        Twilio puts the retry time in the `Retry-After` response header so we
        we return that value. If the response is anything other than a 429 (e.g: 5XX)
        fall back on default retry behavior.
        Rate Limits Docs: https://support.twilio.com/hc/en-us/articles/360032845014-Verify-V2-Rate-Limiting"""

        backoff_time = response.headers.get("Retry-After")
        if backoff_time is not None:
            return float(backoff_time)

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params["PageSize"] = self.page_size
        if next_page_token:
            params.update(**next_page_token)
        return params

    @transformer.registerCustomTransform
    def custom_transform_function(original_value: Any, field_schema: Mapping[str, Any]) -> Any:
        if original_value and field_schema.get("format") == "date-time":
            try:
                return pendulum.from_format(original_value, "ddd, D MMM YYYY HH:mm:ss ZZ").in_timezone("UTC").to_iso8601_string()
            except ValueError:
                """Twilio API returns datetime in two formats:
                  - RFC2822, like "Fri, 11 Dec 2020 04:28:40 +0000";
                  - ISO8601, like "2020-12-11T04:29:09Z".
                If `ValueError` exception was raised this means that datetime was already in ISO8601 format and there
                is no need in transforming anything."""
                pass
        return original_value


class IncrementalTwilioStream(TwilioStream, IncrementalMixin):
    time_filter_template = "YYYY-MM-DD HH:mm:ss[Z]"
    # This attribute allows balancing between sync speed and memory consumption.
    # The greater a slice is - the bigger memory consumption and the faster syncs are since fewer requests are made.
    slice_step_default = pendulum.duration(years=1)
    # time gap between when previous slice ends and current slice begins
    slice_granularity = pendulum.duration(microseconds=1)
    state_checkpoint_interval = 1000

    def __init__(
        self,
        authenticator: Union[AuthBase, HttpAuthenticator],
        start_date: str = None,
        lookback_window: int = 0,
        slice_step_map: Mapping[str, int] = None,
    ):
        super().__init__(authenticator)
        slice_step = (slice_step_map or {}).get(self.name)
        self._slice_step = slice_step and pendulum.duration(days=slice_step)
        self._start_date = start_date if start_date is not None else "1970-01-01T00:00:00Z"
        self._lookback_window = lookback_window
        self._cursor_value = None

    @property
    def slice_step(self):
        return self._slice_step or self.slice_step_default

    @property
    @abstractmethod
    def lower_boundary_filter_field(self) -> str:
        """
        return: date filter query parameter name
        """

    @property
    @abstractmethod
    def upper_boundary_filter_field(self) -> str:
        """
        return: date filter query parameter name
        """

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {
                self.cursor_field: self._cursor_value,
            }

        return {}

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        if self._lookback_window and value.get(self.cursor_field):
            new_start_date = (
                pendulum.parse(value[self.cursor_field]) - pendulum.duration(minutes=self._lookback_window)
            ).to_iso8601_string()
            if new_start_date > self._start_date:
                value[self.cursor_field] = new_start_date
        self._cursor_value = value.get(self.cursor_field)

    def generate_date_ranges(self) -> Iterable[Optional[MutableMapping[str, Any]]]:
        def align_to_dt_format(dt: DateTime) -> DateTime:
            return pendulum.parse(dt.format(self.time_filter_template))

        end_datetime = pendulum.now("utc")
        start_datetime = min(end_datetime, pendulum.parse(self.state.get(self.cursor_field, self._start_date)))
        current_start = start_datetime
        current_end = start_datetime
        # Aligning to a datetime format is done to avoid the following scenario:
        # start_dt = 2021-11-14T00:00:00, end_dt (now) = 2022-11-14T12:03:01, time_filter_template = "YYYY-MM-DD"
        # First slice: (2021-11-14, 2022-11-14)
        # (!) Second slice: (2022-11-15, 2022-11-14) - because 2022-11-14T00:00:00 (prev end) < 2022-11-14T12:03:01,
        # so we have to compare dates, not date-times to avoid yielding that last slice
        while align_to_dt_format(current_end) < align_to_dt_format(end_datetime):
            current_end = min(end_datetime, current_start + self.slice_step)
            slice_ = {
                self.lower_boundary_filter_field: current_start.format(self.time_filter_template),
                self.upper_boundary_filter_field: current_end.format(self.time_filter_template),
            }
            yield slice_
            current_start = current_end + self.slice_granularity

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for super_slice in super().stream_slices(sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state):
            for dt_range in self.generate_date_ranges():
                slice_ = copy.deepcopy(super_slice) if super_slice else {}
                slice_.update(dt_range)
                yield slice_

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        lower_bound = stream_slice and stream_slice.get(self.lower_boundary_filter_field)
        upper_bound = stream_slice and stream_slice.get(self.upper_boundary_filter_field)
        if lower_bound:
            params[self.lower_boundary_filter_field] = lower_bound
        if upper_bound:
            params[self.upper_boundary_filter_field] = upper_bound
        return params

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        unsorted_records = []
        for record in super().read_records(sync_mode, cursor_field, stream_slice, stream_state):
            record[self.cursor_field] = pendulum.parse(record[self.cursor_field], strict=False).to_iso8601_string()
            unsorted_records.append(record)
        sorted_records = sorted(unsorted_records, key=lambda x: x[self.cursor_field])
        for record in sorted_records:
            if record[self.cursor_field] >= self.state.get(self.cursor_field, self._start_date):
                self._cursor_value = record[self.cursor_field]
                yield record


class TwilioNestedStream(TwilioStream):
    """
    Basic class for the streams that are dependant on the results of another stream output (parent-child relations).
    Parent class read is always full refresh, even if it supports incremental read.
    """

    media_exist_validation = {}
    uri_from_subresource = True

    def path(self, stream_slice: Mapping[str, Any], **kwargs):
        return stream_slice["subresource_uri"]

    @property
    def subresource_uri_key(self):
        return self.data_field

    @property
    @abstractmethod
    def parent_stream(self) -> TwilioStream:
        """
        :return: parent stream class
        """

    @cached_property
    def parent_stream_instance(self):
        return self.parent_stream(authenticator=self.authenticator)

    def parent_record_to_stream_slice(self, record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {"subresource_uri": record["subresource_uris"][self.subresource_uri_key]}

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        stream_instance = self.parent_stream_instance
        stream_slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh, cursor_field=stream_instance.cursor_field)
        for stream_slice in stream_slices:
            for item in stream_instance.read_records(
                sync_mode=SyncMode.full_refresh, stream_slice=stream_slice, cursor_field=stream_instance.cursor_field
            ):
                if not self.uri_from_subresource:
                    yield self.parent_record_to_stream_slice(item)
                elif item.get("subresource_uris", {}).get(self.subresource_uri_key):
                    validated = True
                    for key, value in self.media_exist_validation.items():
                        validated = item.get(key) and item.get(key) != value
                        if not validated:
                            break
                    if validated:
                        yield self.parent_record_to_stream_slice(item)


class Accounts(TwilioStream):
    """https://www.twilio.com/docs/usage/api/account#read-multiple-account-resources"""

    url_base = TWILIO_API_URL_BASE_VERSIONED


class Addresses(TwilioNestedStream):
    """https://www.twilio.com/docs/usage/api/address#read-multiple-address-resources"""

    parent_stream = Accounts


class DependentPhoneNumbers(TwilioNestedStream):
    """https://www.twilio.com/docs/usage/api/address?code-sample=code-list-dependent-pns-subresources&code-language=curl&code-sdk-version=json#instance-subresources"""

    parent_stream = Addresses
    url_base = TWILIO_API_URL_BASE_VERSIONED
    uri_from_subresource = False

    def path(self, stream_slice: Mapping[str, Any], **kwargs):
        return f"Accounts/{stream_slice['account_sid']}/Addresses/{stream_slice['sid']}/DependentPhoneNumbers.json"

    def parent_record_to_stream_slice(self, record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {"sid": record["sid"], "account_sid": record["account_sid"]}


class Applications(TwilioNestedStream):
    """https://www.twilio.com/docs/usage/api/applications#read-multiple-application-resources"""

    parent_stream = Accounts


class AvailablePhoneNumberCountries(TwilioNestedStream):
    """
    https://www.twilio.com/docs/phone-numbers/api/availablephonenumber-resource#read-a-list-of-countries

    List of available phone number countries, as well as local, mobile and toll free numbers
    may be different on each request, so could not pass the full refresh tests.
    """

    parent_stream = Accounts
    data_field = "countries"
    subresource_uri_key = "available_phone_numbers"
    primary_key = None


class AvailablePhoneNumbersLocal(TwilioNestedStream):
    """https://www.twilio.com/docs/phone-numbers/api/availablephonenumberlocal-resource#read-multiple-availablephonenumberlocal-resources"""

    parent_stream = AvailablePhoneNumberCountries
    data_field = "available_phone_numbers"
    subresource_uri_key = "local"
    primary_key = None


class AvailablePhoneNumbersMobile(TwilioNestedStream):
    """https://www.twilio.com/docs/phone-numbers/api/availablephonenumber-mobile-resource#read-multiple-availablephonenumbermobile-resources"""

    parent_stream = AvailablePhoneNumberCountries
    data_field = "available_phone_numbers"
    subresource_uri_key = "mobile"
    primary_key = None


class AvailablePhoneNumbersTollFree(TwilioNestedStream):
    """https://www.twilio.com/docs/phone-numbers/api/availablephonenumber-tollfree-resource#read-multiple-availablephonenumbertollfree-resources"""

    parent_stream = AvailablePhoneNumberCountries
    data_field = "available_phone_numbers"
    subresource_uri_key = "toll_free"
    primary_key = None


class IncomingPhoneNumbers(TwilioNestedStream):
    """https://www.twilio.com/docs/phone-numbers/api/incomingphonenumber-resource#read-multiple-incomingphonenumber-resources"""

    parent_stream = Accounts


class Keys(TwilioNestedStream):
    """https://www.twilio.com/docs/usage/api/keys#read-a-key-resource"""

    parent_stream = Accounts


class Calls(IncrementalTwilioStream, TwilioNestedStream):
    """https://www.twilio.com/docs/voice/api/call-resource#create-a-call-resource"""

    parent_stream = Accounts
    lower_boundary_filter_field = "EndTime>"
    upper_boundary_filter_field = "EndTime<"
    cursor_field = "end_time"
    time_filter_template = "YYYY-MM-DD"
    slice_granularity = pendulum.duration(days=1)


class Conferences(IncrementalTwilioStream, TwilioNestedStream):
    """https://www.twilio.com/docs/voice/api/conference-resource#read-multiple-conference-resources"""

    parent_stream = Accounts
    lower_boundary_filter_field = "DateCreated>"
    upper_boundary_filter_field = "DateCreated<"
    cursor_field = "date_created"
    time_filter_template = "YYYY-MM-DD"
    slice_granularity = pendulum.duration(days=1)


class ConferenceParticipants(TwilioNestedStream):
    """
    https://www.twilio.com/docs/voice/api/conference-participant-resource#read-multiple-participant-resources

    This streams has records only if there are active conference participants (participants,
    which are on conference call at the moment request is made).
    """

    primary_key = ["account_sid", "conference_sid"]
    parent_stream = Conferences
    data_field = "participants"


class Flows(TwilioStream):
    """
    https://www.twilio.com/docs/studio/rest-api/flow#read-a-list-of-flows
    """

    url_base = TWILIO_STUDIO_API_BASE

    def path(self, **kwargs):
        return "Flows"


class Executions(TwilioNestedStream):
    """
    https://www.twilio.com/docs/studio/rest-api/execution#read-a-list-of-executions
    """

    parent_stream = Flows
    url_base = TWILIO_STUDIO_API_BASE
    uri_from_subresource = False

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        return f"Flows/{ stream_slice['flow_sid'] }/Executions"

    def parent_record_to_stream_slice(self, record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {"flow_sid": record["sid"]}


class OutgoingCallerIds(TwilioNestedStream):
    """https://www.twilio.com/docs/voice/api/outgoing-caller-ids#outgoingcallerids-list-resource"""

    parent_stream = Accounts


class Recordings(IncrementalTwilioStream, TwilioNestedStream):
    """https://www.twilio.com/docs/voice/api/recording#read-multiple-recording-resources"""

    parent_stream = Accounts
    lower_boundary_filter_field = "DateCreated>"
    upper_boundary_filter_field = "DateCreated<"
    cursor_field = "date_created"


class Transcriptions(TwilioNestedStream):
    """https://www.twilio.com/docs/voice/api/recording-transcription?code-sample=code-read-list-all-transcriptions&code-language=curl&code-sdk-version=json#read-multiple-transcription-resources"""

    parent_stream = Accounts


class Queues(TwilioNestedStream):
    """https://www.twilio.com/docs/voice/api/queue-resource#read-multiple-queue-resources"""

    parent_stream = Accounts


class Messages(IncrementalTwilioStream, TwilioNestedStream):
    """https://www.twilio.com/docs/sms/api/message-resource#read-multiple-message-resources"""

    parent_stream = Accounts
    slice_step_default = pendulum.duration(days=1)
    lower_boundary_filter_field = "DateSent>"
    upper_boundary_filter_field = "DateSent<"
    cursor_field = "date_sent"


class MessageMedia(IncrementalTwilioStream, TwilioNestedStream):
    """https://www.twilio.com/docs/sms/api/media-resource#read-multiple-media-resources"""

    parent_stream = Messages
    data_field = "media_list"
    subresource_uri_key = "media"
    media_exist_validation = {"num_media": "0"}
    lower_boundary_filter_field = "DateCreated>"
    upper_boundary_filter_field = "DateCreated<"
    cursor_field = "date_created"

    @cached_property
    def parent_stream_instance(self):
        return self.parent_stream(authenticator=self.authenticator, start_date=self._start_date, lookback_window=self._lookback_window)


class UsageNestedStream(TwilioNestedStream):
    url_base = TWILIO_API_URL_BASE_VERSIONED
    uri_from_subresource = False

    @property
    @abstractmethod
    def path_name(self) -> str:
        """
        return: name of the end of the usage paths
        """

    def path(self, stream_slice: Mapping[str, Any], **kwargs):
        return f"Accounts/{stream_slice['account_sid']}/Usage/{self.path_name}.json"

    def parent_record_to_stream_slice(self, record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {"account_sid": record["sid"]}


class UsageRecords(IncrementalTwilioStream, UsageNestedStream):
    """https://www.twilio.com/docs/usage/api/usage-record#read-multiple-usagerecord-resources"""

    parent_stream = Accounts
    lower_boundary_filter_field = "StartDate"
    upper_boundary_filter_field = "EndDate"
    cursor_field = "start_date"
    time_filter_template = "YYYY-MM-DD"
    slice_granularity = pendulum.duration(days=1)
    path_name = "Records"
    primary_key = [["account_sid"], ["category"]]
    changeable_fields = ["as_of"]


class UsageTriggers(UsageNestedStream):
    """https://www.twilio.com/docs/usage/api/usage-trigger#read-multiple-usagetrigger-resources"""

    parent_stream = Accounts
    subresource_uri_key = "triggers"
    path_name = "Triggers"


class Alerts(IncrementalTwilioStream):
    """https://www.twilio.com/docs/usage/monitor-alert#read-multiple-alert-resources"""

    url_base = TWILIO_MONITOR_URL_BASE
    lower_boundary_filter_field = "StartDate="
    upper_boundary_filter_field = "EndDate="
    cursor_field = "date_generated"

    def path(self, **kwargs):
        return self.name.title()


class Conversations(TwilioStream):
    """https://www.twilio.com/docs/conversations/api/conversation-resource#read-multiple-conversation-resources"""

    url_base = TWILIO_CONVERSATIONS_URL_BASE

    def path(self, **kwargs):
        return self.name.title()


class ConversationMessages(TwilioNestedStream):
    """https://www.twilio.com/docs/conversations/api/conversation-message-resource#list-all-conversation-messages"""

    parent_stream = Conversations
    url_base = TWILIO_CONVERSATIONS_URL_BASE
    uri_from_subresource = False
    data_field = "messages"

    def path(self, stream_slice: Mapping[str, Any], **kwargs):
        return f"Conversations/{stream_slice['conversation_sid']}/Messages"

    def parent_record_to_stream_slice(self, record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {"conversation_sid": record["sid"]}
