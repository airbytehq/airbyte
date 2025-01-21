#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, MutableMapping, Optional

import pendulum
import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.schema import JsonFileSchemaLoader
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, Record
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState
from airbyte_cdk.utils import AirbyteTracedException


logger = logging.getLogger("airbyte")


class AverageSessionLengthRecordExtractor(RecordExtractor):
    """
    Create records from complex response structure
    Issue: https://github.com/airbytehq/airbyte/issues/23145
    """

    def extract_records(self, response: requests.Response) -> List[Record]:
        response_data = response.json().get("data", [])
        if response_data:
            # From the Amplitude documentation it follows that "series" is an array with one element which is itself
            # an array that contains the average session length for each day.
            # https://developers.amplitude.com/docs/dashboard-rest-api#returns-2
            series = response_data.get("series", [])
            if len(series) > 0:
                series = series[0]  # get the nested list
                return [{"date": date, "length": length} for date, length in zip(response_data["xValues"], series)]
        return []


class ActiveUsersRecordExtractor(RecordExtractor):
    """
    Create records from complex response structure
    Issue: https://github.com/airbytehq/airbyte/issues/23145
    """

    def extract_records(self, response: requests.Response) -> List[Record]:
        response_data = response.json().get("data", [])
        if response_data:
            series = list(zip(*response_data["series"]))
            if series:
                return [
                    {"date": date, "statistics": dict(zip(response_data["seriesLabels"], users))}
                    for date, users in zip(response_data["xValues"], series)
                ]
        return []


class TransformDatetimesToRFC3339(RecordTransformation):
    def __init__(self):
        self.name = "events"
        self.date_time_fields = [
            "event_time",
            "server_upload_time",
            "processed_time",
            "server_received_time",
            "user_creation_time",
            "client_upload_time",
            "client_event_time",
        ]

    def transform(
        self,
        record: Dict[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        """
        Transform 'date-time' items to RFC3339 format
        """
        for item in record:
            if item in self.date_time_fields and record[item]:
                try:
                    record[item] = pendulum.parse(record[item]).to_rfc3339_string()
                except Exception as e:
                    logger.error(f"Error converting {item} to RFC3339 format: {e}")
                    raise AirbyteTracedException(
                        message=f"Error converting {item} to RFC3339 format. See logs for more infromation",
                        internal_message=f"Error converting {item} to RFC3339 format: {e}",
                        failure_type=FailureType.system_error,
                    ) from e
        return record
