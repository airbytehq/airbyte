#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import csv
import json
import urllib.parse as urlparse
from io import StringIO
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.models import SyncMode
from source_iterable.iterable_streams import (
    IterableExportEventsStreamAdjustableRange,
    IterableExportStreamAdjustableRange,
    IterableExportStreamRanged,
    IterableStream,
)

EVENT_ROWS_LIMIT = 200
CAMPAIGNS_PER_REQUEST = 20


class Lists(IterableStream):
    data_field = "lists"

    def path(self, **kwargs) -> str:
        return "lists"


class ListUsers(IterableStream):
    primary_key = "listId"
    data_field = "getUsers"
    name = "list_users"

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"lists/{self.data_field}?listId={stream_slice['list_id']}"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        lists = Lists(authenticator=self._cred)
        for list_record in lists.read_records(sync_mode=kwargs.get("sync_mode", SyncMode.full_refresh)):
            yield {"list_id": list_record["id"]}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        list_id = self._get_list_id(response.url)
        for user in response.iter_lines():
            yield {"email": user.decode(), "listId": list_id}

    @staticmethod
    def _get_list_id(url: str) -> int:
        parsed_url = urlparse.urlparse(url)
        for q in parsed_url.query.split("&"):
            key, value = q.split("=")
            if key == "listId":
                return int(value)


class Campaigns(IterableStream):
    data_field = "campaigns"

    def path(self, **kwargs) -> str:
        return "campaigns"


class CampaignsMetrics(IterableStream):
    name = "campaigns_metrics"
    primary_key = None
    data_field = None

    def __init__(self, start_date: str, **kwargs):
        """
        https://api.iterable.com/api/docs#campaigns_metrics
        """
        super().__init__(**kwargs)
        self.start_date = start_date

    def path(self, **kwargs) -> str:
        return "campaigns/metrics"

    def request_params(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        params["campaignId"] = stream_slice.get("campaign_ids")
        params["startDateTime"] = self.start_date

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


class Channels(IterableStream):
    data_field = "channels"

    def path(self, **kwargs) -> str:
        return "channels"


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


class Events(IterableStream):
    """
    https://api.iterable.com/api/docs#export_exportUserEvents
    """

    primary_key = None
    data_field = "events"
    common_fields = ("itblInternal", "_type", "createdAt", "email")

    def path(self, **kwargs) -> str:
        return "export/userEvents"

    def request_params(self, stream_slice: Optional[Mapping[str, Any]], **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        params.update({"email": stream_slice["email"], "includeCustomEvents": "true"})

        return params

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        lists = ListUsers(authenticator=self._cred)
        stream_slices = lists.stream_slices()

        for stream_slice in stream_slices:
            for list_record in lists.read_records(sync_mode=kwargs.get("sync_mode", SyncMode.full_refresh), stream_slice=stream_slice):
                yield {"email": list_record["email"]}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Parse jsonl response body.
        Put common event fields at the top level.
        Put the rest of the fields in the `data` subobject.
        """

        jsonl_records = StringIO(response.text)
        for record in jsonl_records:
            record_dict = json.loads(record)
            record_dict_common_fields = {}
            for field in self.common_fields:
                record_dict_common_fields[field] = record_dict.pop(field, None)

            yield {**record_dict_common_fields, "data": record_dict}


class MessageTypes(IterableStream):
    data_field = "messageTypes"
    name = "message_types"

    def path(self, **kwargs) -> str:
        return "messageTypes"


class Metadata(IterableStream):
    primary_key = None
    data_field = "results"

    def path(self, **kwargs) -> str:
        return "metadata"


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


class Users(IterableExportStreamRanged):
    data_field = "user"
    cursor_field = "profileUpdatedAt"
