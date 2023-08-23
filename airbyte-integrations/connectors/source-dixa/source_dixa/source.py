#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from . import utils


class DixaStream(HttpStream, ABC):

    primary_key = "id"
    url_base = "https://exports.dixa.io/v1/"

    backoff_sleep = 60  # seconds

    def __init__(self, config: Mapping[str, Any]) -> None:
        super().__init__(authenticator=config["authenticator"])
        self.start_date = datetime.strptime(config["start_date"], "%Y-%m-%d")
        self.start_timestamp = utils.datetime_to_ms_timestamp(self.start_date)
        self.end_timestamp = utils.datetime_to_ms_timestamp(datetime.now()) + 1
        self.batch_size = config["batch_size"]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        return stream_slice

    def backoff_time(self, response: requests.Response):
        """
        The rate limit is 10 requests per minute, so we sleep
        for defined backoff_sleep time (default is 60 sec) before we continue.

        See https://support.dixa.help/en/articles/174-export-conversations-via-api
        """
        return self.backoff_sleep


class IncrementalDixaStream(DixaStream):

    cursor_field = "updated_at"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, any]:
        """
        Uses the `updated_at` field, which is a Unix timestamp with millisecond precision.
        """
        current_stream_state = current_stream_state or {}
        return {
            self.cursor_field: max(
                current_stream_state.get(self.cursor_field, self.start_timestamp),
                latest_record.get(self.cursor_field, self.start_timestamp),
            )
        }

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs):
        """
        Returns slices of size self.batch_size.
        """
        slices = []

        stream_state = stream_state or {}
        # If stream_state contains the cursor field and the value of the cursor
        # field is higher than start_timestamp, then start at the cursor field
        # value. Otherwise, start at start_timestamp.
        updated_after = max(stream_state.get(self.cursor_field, 0), self.start_timestamp)
        updated_before = min(utils.add_days_to_ms_timestamp(days=self.batch_size, ms_timestamp=updated_after), self.end_timestamp)

        # When we have abnormaly_large start_date, start_date > Now(),
        # assign updated_before to the value of updated_after + batch_size,
        # return single slice
        if updated_after > updated_before:
            updated_before = utils.add_days_to_ms_timestamp(days=self.batch_size, ms_timestamp=updated_after)
            return [{"updated_after": updated_after, "updated_before": updated_before}]
        else:
            while updated_after < self.end_timestamp:
                updated_before = min(utils.add_days_to_ms_timestamp(days=self.batch_size, ms_timestamp=updated_after), self.end_timestamp)
                slices.append({"updated_after": updated_after, "updated_before": updated_before})
                updated_after = updated_before

        return slices


class ConversationExport(IncrementalDixaStream):
    """
    https://support.dixa.help/en/articles/174-export-conversations-via-api
    """

    def path(self, **kwargs) -> str:
        return "conversation_export"


class SourceDixa(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """
        Check connectivity using one day's worth of data.
        """
        try:
            config["authenticator"] = TokenAuthenticator(token=config["api_token"])
            stream = ConversationExport(config)
            # using 1 day batch size for slices.
            stream.batch_size = 1
            # use the first slice from stream_slices list
            stream_slice = stream.stream_slices()[0]
            list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice))
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config["authenticator"] = TokenAuthenticator(token=config["api_token"])
        return [
            ConversationExport(config),
        ]
