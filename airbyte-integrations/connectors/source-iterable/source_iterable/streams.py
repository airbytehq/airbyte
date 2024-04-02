#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
import json
from abc import ABC, abstractmethod
from io import StringIO
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException, UserDefinedBackoffException
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from pendulum.datetime import DateTime
from requests import HTTPError, codes
from requests.exceptions import ChunkedEncodingError
from source_iterable.slice_generators import AdjustableSliceGenerator, RangeSliceGenerator, StreamSlice
from source_iterable.utils import dateutil_parse

EVENT_ROWS_LIMIT = 200
CAMPAIGNS_PER_REQUEST = 20


class IterableStream(HttpStream, ABC):
    # in case we get a 401 error (api token disabled or deleted) on a stream slice, do not make further requests within the current stream
    # to prevent 429 error on other streams
    ignore_further_slices = False

    url_base = "https://api.iterable.com/api/"
    primary_key = "id"

    def __init__(self, authenticator):
        self._cred = authenticator
        self._slice_retry = 0
        super().__init__(authenticator)

    @property
    def retry_factor(self) -> int:
        return 20

    # With factor 20 it would be from 20 to 400 seconds delay
    @property
    def max_retries(self) -> Union[int, None]:
        return 10

    @property
    @abstractmethod
    def data_field(self) -> str:
        """
        :return: Default field name to get data from response
        """

    @property
    def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
        return None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Iterable API does not support pagination
        """
        return None

    def check_generic_error(self, response: requests.Response) -> bool:
        """
        https://github.com/airbytehq/oncall/issues/1592#issuecomment-1499109251
        https://github.com/airbytehq/oncall/issues/1985
        """
        codes = ["Generic Error", "GenericError"]
        msg_pattern = "Please try again later"

        if response.status_code == 500:
            # I am not sure that all 500 errors return valid json
            try:
                response_json = json.loads(response.text)
            except ValueError:
                return
            if response_json.get("code") in codes and msg_pattern in response_json.get("msg", ""):
                return True

    def request_kwargs(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        """
        https://requests.readthedocs.io/en/latest/user/advanced/#timeouts
        https://github.com/airbytehq/oncall/issues/1985#issuecomment-1559276465
        """
        return {"timeout": (60, 300)}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json() or {}
        records = response_json.get(self.data_field, [])
        for record in records:
            yield record

    def should_retry(self, response: requests.Response) -> bool:
        if self.check_generic_error(response):
            self._slice_retry += 1
            if self._slice_retry < 3:
                return True
            return False
        return super().should_retry(response)

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        self._slice_retry = 0
        if self.ignore_further_slices:
            return

        try:
            yield from super().read_records(sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state)
        except (HTTPError, UserDefinedBackoffException, DefaultBackoffException) as e:
            response = e.response
            if self.check_generic_error(response):
                return
            raise e


class IterableExportStream(IterableStream, ABC):
    """
    This stream utilize "export" Iterable api for getting large amount of data.
    It can return data in form of new line separater strings each of each
    representing json object.
    Data could be windowed by date ranges by applying startDateTime and
    endDateTime parameters.  Single request could return large volumes of data
    and request rate is limited by 4 requests per minute.

    Details: https://api.iterable.com/api/docs#export_exportDataJson
    """

    cursor_field = "createdAt"
    primary_key = None

    def __init__(self, start_date=None, end_date=None, **kwargs):
        super().__init__(**kwargs)
        self._start_date = pendulum.parse(start_date)
        self._end_date = end_date and pendulum.parse(end_date)
        self.stream_params = {"dataTypeName": self.data_field}

    def path(self, **kwargs) -> str:
        return "export/data.json"

    @staticmethod
    def _field_to_datetime(value: Union[int, str]) -> pendulum.datetime:
        if isinstance(value, int):
            value = pendulum.from_timestamp(value / 1000.0)
        elif isinstance(value, str):
            value = dateutil_parse(value)
        else:
            raise ValueError(f"Unsupported type of datetime field {type(value)}")
        return value

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {
                self.cursor_field: str(
                    max(
                        latest_benchmark,
                        self._field_to_datetime(current_stream_state[self.cursor_field]),
                    )
                )
            }
        return {self.cursor_field: str(latest_benchmark)}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: StreamSlice,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:

        params = super().request_params(stream_state=stream_state)
        params.update(
            {
                "startDateTime": stream_slice.start_date.strftime("%Y-%m-%d %H:%M:%S"),
                "endDateTime": stream_slice.end_date.strftime("%Y-%m-%d %H:%M:%S"),
            },
            **self.stream_params,
        )
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for obj in response.iter_lines():
            record = json.loads(obj)
            record[self.cursor_field] = self._field_to_datetime(record[self.cursor_field])
            yield record

    def request_kwargs(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        """
        https://api.iterable.com/api/docs#export_exportDataJson
        Sending those type of requests could download large piece of json
        objects splitted with newline character.
        Passing stream=True argument to requests.session.send method to avoid
        loading whole analytics report content into memory.
        """
        return {
            **super().request_kwargs(stream_state, stream_slice, next_page_token),
            "stream": True,
        }

    def get_start_date(self, stream_state: Mapping[str, Any]) -> DateTime:
        stream_state = stream_state or {}
        start_datetime = self._start_date
        if stream_state.get(self.cursor_field):
            start_datetime = pendulum.parse(stream_state[self.cursor_field])
        return start_datetime

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Optional[StreamSlice]]:

        start_datetime = self.get_start_date(stream_state)
        return [StreamSlice(start_datetime, self._end_date or pendulum.now("UTC"))]


class IterableExportStreamRanged(IterableExportStream, ABC):
    """
    This class use RangeSliceGenerator class to break single request into
    ranges with same (or less for final range) number of days. By default it 90
    days.
    """

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Optional[StreamSlice]]:

        start_datetime = self.get_start_date(stream_state)

        return RangeSliceGenerator(start_datetime, self._end_date)


class IterableExportStreamAdjustableRange(IterableExportStream, ABC):
    """
    For streams that could produce large amount of data in single request so we
    cant just use IterableExportStreamRanged to split it in even ranges. If
    request processing takes a lot of time API server could just close
    connection and connector code would fail with ChunkedEncodingError.

    To solve this problem we use AdjustableSliceGenerator that able to adjust
    next slice range based on two factor:
    1. Previous slice range / time to process ratio.
    2. Had previous request failed with ChunkedEncodingError

    In case of slice processing request failed with ChunkedEncodingError (which
    means that API server closed connection cause of request takes to much
    time) make CHUNKED_ENCODING_ERROR_RETRIES (6) retries each time reducing
    slice length.

    See AdjustableSliceGenerator description for more details on next slice length adjustment alghorithm.
    """

    _adjustable_generator: AdjustableSliceGenerator = None
    CHUNKED_ENCODING_ERROR_RETRIES = 6

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Optional[StreamSlice]]:

        start_datetime = self.get_start_date(stream_state)
        self._adjustable_generator = AdjustableSliceGenerator(start_datetime, self._end_date)
        return self._adjustable_generator

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str],
        stream_slice: StreamSlice,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        start_time = pendulum.now()
        for _ in range(self.CHUNKED_ENCODING_ERROR_RETRIES):
            try:

                self.logger.info(
                    f"Processing slice of {(stream_slice.end_date - stream_slice.start_date).total_days()} days for stream {self.name}"
                )
                for record in super().read_records(
                    sync_mode=sync_mode,
                    cursor_field=cursor_field,
                    stream_slice=stream_slice,
                    stream_state=stream_state,
                ):
                    now = pendulum.now()
                    self._adjustable_generator.adjust_range(now - start_time)
                    yield record
                    start_time = now
                break
            except ChunkedEncodingError:
                self.logger.warn("ChunkedEncodingError occurred, decrease days range and try again")
                stream_slice = self._adjustable_generator.reduce_range()
        else:
            raise Exception(f"ChunkedEncodingError: Reached maximum number of retires: {self.CHUNKED_ENCODING_ERROR_RETRIES}")


class IterableExportEventsStreamAdjustableRange(IterableExportStreamAdjustableRange, ABC):
    def get_json_schema(self) -> Mapping[str, Any]:
        """All child stream share the same 'events' schema"""
        return ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema("events")


class Campaigns(IterableStream):
    data_field = "campaigns"

    def path(self, **kwargs) -> str:
        return "campaigns"


class CampaignsMetrics(IterableStream):
    name = "campaigns_metrics"
    primary_key = None
    data_field = None

    def __init__(self, start_date: str, end_date: Optional[str] = None, **kwargs):
        """
        https://api.iterable.com/api/docs#campaigns_metrics
        """
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date

    def path(self, **kwargs) -> str:
        return "campaigns/metrics"

    def request_params(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        params["campaignId"] = stream_slice.get("campaign_ids")
        params["startDateTime"] = self.start_date
        if self.end_date:
            params["endDateTime"] = self.end_date
        return params

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        lists = Campaigns(authenticator=self._cred)
        campaign_ids = []
        for list_record in lists.read_records(sync_mode=kwargs.get("sync_mode", SyncMode.full_refresh)):
            campaign_ids.append(list_record["id"])

            if len(campaign_ids) == CAMPAIGNS_PER_REQUEST:
                yield {"campaign_ids": campaign_ids}
                campaign_ids = []

        if campaign_ids:
            yield {"campaign_ids": campaign_ids}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        content = response.content.decode()
        records = self._parse_csv_string_to_dict(content)

        for record in records:
            yield {"data": record}

    @staticmethod
    def _parse_csv_string_to_dict(csv_string: str) -> List[Dict[str, Any]]:
        """
        Parse a response with a csv type to dict object
        Example:
            csv_string = "a,b,c,d
                          1,2,,3
                          6,,1,2"

            output = [{"a": 1, "b": 2, "d": 3},
                      {"a": 6, "c": 1, "d": 2}]


        :param csv_string: API endpoint response with csv format
        :return: parsed API response

        """

        reader = csv.DictReader(StringIO(csv_string), delimiter=",")
        result = []

        for row in reader:
            for key, value in row.items():
                if value == "":
                    continue
                try:
                    row[key] = int(value)
                except ValueError:
                    row[key] = float(value)
            row = {k: v for k, v in row.items() if v != ""}

            result.append(row)

        return result


class EmailBounce(IterableExportStreamAdjustableRange):
    data_field = "emailBounce"


class EmailClick(IterableExportStreamAdjustableRange):
    data_field = "emailClick"


class EmailComplaint(IterableExportStreamAdjustableRange):
    data_field = "emailComplaint"


class EmailOpen(IterableExportStreamAdjustableRange):
    data_field = "emailOpen"


class EmailSend(IterableExportStreamAdjustableRange):
    data_field = "emailSend"


class EmailSendSkip(IterableExportStreamAdjustableRange):
    data_field = "emailSendSkip"


class EmailSubscribe(IterableExportStreamAdjustableRange):
    data_field = "emailSubscribe"


class EmailUnsubscribe(IterableExportStreamAdjustableRange):
    data_field = "emailUnsubscribe"


class PushSend(IterableExportEventsStreamAdjustableRange):
    data_field = "pushSend"


class PushSendSkip(IterableExportEventsStreamAdjustableRange):
    data_field = "pushSendSkip"


class PushOpen(IterableExportEventsStreamAdjustableRange):
    data_field = "pushOpen"


class PushUninstall(IterableExportEventsStreamAdjustableRange):
    data_field = "pushUninstall"


class PushBounce(IterableExportEventsStreamAdjustableRange):
    data_field = "pushBounce"


class WebPushSend(IterableExportEventsStreamAdjustableRange):
    data_field = "webPushSend"


class WebPushClick(IterableExportEventsStreamAdjustableRange):
    data_field = "webPushClick"


class WebPushSendSkip(IterableExportEventsStreamAdjustableRange):
    data_field = "webPushSendSkip"


class InAppSend(IterableExportEventsStreamAdjustableRange):
    data_field = "inAppSend"


class InAppOpen(IterableExportEventsStreamAdjustableRange):
    data_field = "inAppOpen"


class InAppClick(IterableExportEventsStreamAdjustableRange):
    data_field = "inAppClick"


class InAppClose(IterableExportEventsStreamAdjustableRange):
    data_field = "inAppClose"


class InAppDelete(IterableExportEventsStreamAdjustableRange):
    data_field = "inAppDelete"


class InAppDelivery(IterableExportEventsStreamAdjustableRange):
    data_field = "inAppDelivery"


class InAppSendSkip(IterableExportEventsStreamAdjustableRange):
    data_field = "inAppSendSkip"


class InboxSession(IterableExportEventsStreamAdjustableRange):
    data_field = "inboxSession"


class InboxMessageImpression(IterableExportEventsStreamAdjustableRange):
    data_field = "inboxMessageImpression"


class SmsSend(IterableExportEventsStreamAdjustableRange):
    data_field = "smsSend"


class SmsBounce(IterableExportEventsStreamAdjustableRange):
    data_field = "smsBounce"


class SmsClick(IterableExportEventsStreamAdjustableRange):
    data_field = "smsClick"


class SmsReceived(IterableExportEventsStreamAdjustableRange):
    data_field = "smsReceived"


class SmsSendSkip(IterableExportEventsStreamAdjustableRange):
    data_field = "smsSendSkip"


class SmsUsageInfo(IterableExportEventsStreamAdjustableRange):
    data_field = "smsUsageInfo"


class Purchase(IterableExportEventsStreamAdjustableRange):
    data_field = "purchase"


class CustomEvent(IterableExportEventsStreamAdjustableRange):
    data_field = "customEvent"


class HostedUnsubscribeClick(IterableExportEventsStreamAdjustableRange):
    data_field = "hostedUnsubscribeClick"


class Templates(IterableExportStreamRanged):
    data_field = "templates"
    template_types = ["Base", "Blast", "Triggered", "Workflow"]
    message_types = ["Email", "Push", "InApp", "SMS"]

    def path(self, **kwargs) -> str:
        return "templates"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        for template in self.template_types:
            for message in self.message_types:
                self.stream_params = {"templateType": template, "messageMedium": message}
                yield from super().read_records(stream_slice=stream_slice, **kwargs)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        records = response_json.get(self.data_field, [])

        for record in records:
            record[self.cursor_field] = self._field_to_datetime(record[self.cursor_field])
            yield record
