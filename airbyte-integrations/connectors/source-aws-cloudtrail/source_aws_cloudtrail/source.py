#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
import math
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import boto3
import botocore
import botocore.exceptions
import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from botocore.config import Config


class Client:
    def __init__(self, aws_key_id: str, aws_secret_key: str, aws_region_name: str):
        config = Config(
            parameter_validation=False,
            retries=dict(
                # use similar configuration as in http source
                max_attempts=5,
                # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/retries.html#adaptive-retry-mode
                mode="adaptive",
            ),
        )

        self.session: botocore.client.CloudTrail = boto3.client(
            "cloudtrail", aws_access_key_id=aws_key_id, aws_secret_access_key=aws_secret_key, region_name=aws_region_name, config=config
        )


class AwsCloudtrailStream(Stream, ABC):
    limit: int = 50

    start_date_format = "YYYY-MM-DD"

    def __init__(self, aws_key_id: str, aws_secret_key: str, aws_region_name: str, start_date: str, **kwargs):
        self.aws_secret_key = aws_secret_key
        self.aws_key_id = aws_key_id
        self.start_date = pendulum.from_format(start_date, self.start_date_format).int_timestamp
        self.client = Client(aws_key_id, aws_secret_key, aws_region_name)
        # records_limit: is an option to limit maximum amount of records read by connector
        # use it for testing and development porpuses only
        self.records_left = kwargs.get("records_limit", math.inf)

    def next_page_token(self, response: Mapping[str, Any]) -> Optional[Mapping[str, Any]]:
        return response.get("NextToken")

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"MaxResults": self.limit}

        if self.start_date:
            params["StartTime"] = self.start_date
        if next_page_token:
            params["NextToken"] = next_page_token

        return params

    def datetime_to_timestamp(self, date: datetime) -> int:
        return int(datetime.timestamp(date))

    @abstractmethod
    def send_request(self, **kwargs) -> Mapping[str, Any]:
        """
        This method should be overridden by subclasses to send proper request with appropriate parameters to CloudTrail
        """
        pass

    def is_read_limit_reached(self) -> bool:
        if self.records_left <= 0:
            # limit of fetched records is reached
            return True
        return False

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        pagination_complete = False
        next_page_token = None

        if self.is_read_limit_reached():
            return iter(())

        while not pagination_complete:
            params = self.request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
            response = self.send_request(**params)

            next_page_token = self.next_page_token(response)
            if not next_page_token:
                pagination_complete = True

            for record in self.parse_response(response):
                yield record
                self.records_left -= 1

                if self.is_read_limit_reached():
                    return iter(())

        yield from []


class IncrementalAwsCloudtrailStream(AwsCloudtrailStream, ABC):

    # API does not support read in ascending order
    # save state only once after full read
    state_checkpoint_interval = None

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        record_time = latest_record[self.time_field]
        return {self.cursor_field: max(record_time, current_stream_state.get(self.cursor_field, 0))}


class ManagementEvents(IncrementalAwsCloudtrailStream):
    primary_key = "EventId"

    time_field = "EventTime"

    cursor_field = "EventTime"

    data_field = "Events"

    data_lifetime = 90 * (24 * 60 * 60)  # in seconds (90 days)

    def send_request(self, **kwargs) -> Mapping[str, Any]:
        return self.client.session.lookup_events(**kwargs)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

        if stream_slice:
            # override time ranges using slice
            if stream_slice.get("StartTime"):
                params["StartTime"] = stream_slice["StartTime"]
            if stream_slice.get("EndTime"):
                params["EndTime"] = stream_slice["EndTime"]

        return params

    def parse_response(self, response: dict, **kwargs) -> Iterable[Mapping]:
        for event in response[self.data_field]:
            # boto3 converts timestamps to datetime object
            # we need to convert it back to timestamp to persist original API type
            event[self.time_field] = self.datetime_to_timestamp(event[self.time_field])
            yield event

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Slices whole time range to more granular slices (24h slices). Latest time slice should be the first to avoid data loss
        """
        cursor_data = stream_state.get(self.cursor_field) if stream_state else 0
        end_time = pendulum.now()
        # API stores data for last 90 days. Adjust starting time to avoid unnecessary API requests
        # ignores state if start_date option is higher than cursor
        start_time = max(end_time.int_timestamp - self.data_lifetime, self.start_date, cursor_data)
        last_start_time = pendulum.from_timestamp(start_time)

        slices = []
        while last_start_time < end_time:
            slices.append(
                {
                    "StartTime": last_start_time.int_timestamp,
                    # decrement second as API include records with specified StartTime and EndTime
                    "EndTime": last_start_time.add(days=1).int_timestamp - 1,
                }
            )
            last_start_time = last_start_time.add(days=1)

        return slices


class SourceAwsCloudtrail(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        client = Client(config["aws_key_id"], config["aws_secret_key"], config["aws_region_name"])
        try:
            client.session.lookup_events(MaxResults=1)
        except botocore.exceptions.ClientError as error:
            return False, error

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [ManagementEvents(**config)]
