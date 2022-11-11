#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional
from urllib.parse import parse_qsl, urlparse

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer

TWILIO_API_URL_BASE = "https://api.twilio.com"
TWILIO_API_URL_BASE_VERSIONED = f"{TWILIO_API_URL_BASE}/2010-04-01/"
TWILIO_MONITOR_URL_BASE = "https://monitor.twilio.com/v1/"


class TwilioStream(HttpStream, ABC):
    url_base = TWILIO_API_URL_BASE
    primary_key = "sid"
    page_size = 1000
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def data_field(self):
        return self.name

    @property
    def changeable_fields(self):
        """
        :return list of changeable fields that should be removed from the records
        """
        return []

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
        self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)
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
    state_checkpoint_interval = 1000

    def __init__(self, start_date: str = None, lookback_window: int = 0, **kwargs):
        super().__init__(**kwargs)
        self._start_date = start_date if start_date is not None else "1970-01-01T00:00:00Z"
        self._lookback_window = lookback_window
        self._cursor_value = None

    @property
    @abstractmethod
    def incremental_filter_field(self) -> str:
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
    def state(self, value: Mapping[str, Any]):
        if self._lookback_window and value.get(self.cursor_field):
            new_start_date = (
                pendulum.parse(value[self.cursor_field]) - pendulum.duration(minutes=self._lookback_window)
            ).to_iso8601_string()
            if new_start_date > self._start_date:
                value[self.cursor_field] = new_start_date
        self._cursor_value = value.get(self.cursor_field)

    def request_params(
        self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)
        start_date = self.state.get(self.cursor_field, self._start_date)
        params[self.incremental_filter_field] = pendulum.parse(start_date).format(self.time_filter_template)
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

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        stream_instance = self.parent_stream(authenticator=self.authenticator)
        stream_slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh, cursor_field=stream_instance.cursor_field)
        for stream_slice in stream_slices:
            for item in stream_instance.read_records(
                sync_mode=SyncMode.full_refresh, stream_slice=stream_slice, cursor_field=stream_instance.cursor_field
            ):
                if item.get("subresource_uris", {}).get(self.subresource_uri_key):
                    validated = True
                    for key, value in self.media_exist_validation.items():
                        validated = item.get(key) and item.get(key) != value
                        if not validated:
                            break
                    if validated:
                        yield {"subresource_uri": item["subresource_uris"][self.subresource_uri_key]}


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

    def path(self, stream_slice: Mapping[str, Any], **kwargs):
        return f"Accounts/{stream_slice['account_sid']}/Addresses/{stream_slice['sid']}/DependentPhoneNumbers.json"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        stream_instance = self.parent_stream(authenticator=self.authenticator)
        stream_slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh, cursor_field=stream_instance.cursor_field)
        for stream_slice in stream_slices:
            for item in stream_instance.read_records(
                sync_mode=SyncMode.full_refresh, stream_slice=stream_slice, cursor_field=stream_instance.cursor_field
            ):
                yield {"sid": item["sid"], "account_sid": item["account_sid"]}


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


class Calls(TwilioNestedStream, IncrementalTwilioStream):
    """https://www.twilio.com/docs/voice/api/call-resource#create-a-call-resource"""

    parent_stream = Accounts
    incremental_filter_field = "EndTime>"
    cursor_field = "end_time"
    time_filter_template = "YYYY-MM-DD"


class Conferences(TwilioNestedStream, IncrementalTwilioStream):
    """https://www.twilio.com/docs/voice/api/conference-resource#read-multiple-conference-resources"""

    parent_stream = Accounts
    incremental_filter_field = "DateCreated>"
    cursor_field = "date_created"
    time_filter_template = "YYYY-MM-DD"


class ConferenceParticipants(TwilioNestedStream):
    """
    https://www.twilio.com/docs/voice/api/conference-participant-resource#read-multiple-participant-resources

    This streams has records only if there are active conference participants (participants,
    which are on conference call at the moment request is made).
    """

    primary_key = ["account_sid", "conference_sid"]
    parent_stream = Conferences
    data_field = "participants"


class OutgoingCallerIds(TwilioNestedStream):
    """https://www.twilio.com/docs/voice/api/outgoing-caller-ids#outgoingcallerids-list-resource"""

    parent_stream = Accounts


class Recordings(TwilioNestedStream, IncrementalTwilioStream):
    """https://www.twilio.com/docs/voice/api/recording#read-multiple-recording-resources"""

    parent_stream = Accounts
    incremental_filter_field = "DateCreated>"
    cursor_field = "date_created"


class Transcriptions(TwilioNestedStream):
    """https://www.twilio.com/docs/voice/api/recording-transcription?code-sample=code-read-list-all-transcriptions&code-language=curl&code-sdk-version=json#read-multiple-transcription-resources"""

    parent_stream = Accounts


class Queues(TwilioNestedStream):
    """https://www.twilio.com/docs/voice/api/queue-resource#read-multiple-queue-resources"""

    parent_stream = Accounts


class Messages(TwilioNestedStream, IncrementalTwilioStream):
    """https://www.twilio.com/docs/sms/api/message-resource#read-multiple-message-resources"""

    parent_stream = Accounts
    incremental_filter_field = "DateSent>"
    cursor_field = "date_sent"


class MessageMedia(TwilioNestedStream, IncrementalTwilioStream):
    """https://www.twilio.com/docs/sms/api/media-resource#read-multiple-media-resources"""

    parent_stream = Messages
    data_field = "media_list"
    subresource_uri_key = "media"
    media_exist_validation = {"num_media": "0"}
    incremental_filter_field = "DateCreated>"
    cursor_field = "date_created"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        stream_instance = self.parent_stream(
            authenticator=self.authenticator, start_date=self._start_date, lookback_window=self._lookback_window
        )
        stream_slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh, cursor_field=stream_instance.cursor_field)
        for stream_slice in stream_slices:
            for item in stream_instance.read_records(
                sync_mode=SyncMode.full_refresh, stream_slice=stream_slice, cursor_field=stream_instance.cursor_field
            ):
                if item.get("subresource_uris", {}).get(self.subresource_uri_key):
                    validated = True
                    for key, value in self.media_exist_validation.items():
                        validated = item.get(key) and item.get(key) != value
                        if not validated:
                            break
                    if validated:

                        yield {"subresource_uri": item["subresource_uris"][self.subresource_uri_key]}


class UsageNestedStream(TwilioNestedStream):
    url_base = TWILIO_API_URL_BASE_VERSIONED

    @property
    @abstractmethod
    def path_name(self) -> str:
        """
        return: name of the end of the usage paths
        """

    def path(self, stream_slice: Mapping[str, Any], **kwargs):
        return f"Accounts/{stream_slice['account_sid']}/Usage/{self.path_name}.json"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        stream_instance = self.parent_stream(authenticator=self.authenticator)
        stream_slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh, cursor_field=stream_instance.cursor_field)
        for stream_slice in stream_slices:
            for item in stream_instance.read_records(
                sync_mode=SyncMode.full_refresh, stream_slice=stream_slice, cursor_field=stream_instance.cursor_field
            ):
                yield {"account_sid": item["sid"]}


class UsageRecords(UsageNestedStream, IncrementalTwilioStream):
    """https://www.twilio.com/docs/usage/api/usage-record#read-multiple-usagerecord-resources"""

    parent_stream = Accounts
    incremental_filter_field = "StartDate"
    cursor_field = "start_date"
    time_filter_template = "YYYY-MM-DD"
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
    incremental_filter_field = "StartDate"
    cursor_field = "date_generated"

    def path(self, **kwargs):
        return self.name.title()
