#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import gzip
import io
import json
import logging
import zipfile
from dataclasses import InitVar, dataclass
from typing import IO, Any, Iterable, List, Mapping, MutableMapping, Union

import pendulum
import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.schema.json_file_schema_loader import JsonFileSchemaLoader
from airbyte_cdk.sources.declarative.types import Config, Record


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


@dataclass
class EventsExtractor(RecordExtractor):
    """
    Response for event stream is a zip file with a list of gziped json files inside it.
    Issue: https://github.com/airbytehq/airbyte/issues/23144
    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]):
        self.name = parameters.get("name")
        self.date_time_fields = self._get_date_time_items_from_schema()

    def _get_schema_root_properties(self):
        schema_loader = JsonFileSchemaLoader(config=self.config, parameters={"name": self.name})
        schema = schema_loader.get_json_schema()
        return schema["properties"]

    def _get_date_time_items_from_schema(self):
        """
        Get all properties from schema with format: 'date-time'
        """
        result = []
        schema = self._get_schema_root_properties()
        for key, value in schema.items():
            if value.get("format") == "date-time":
                result.append(key)
        return result

    def _date_time_to_rfc3339(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Transform 'date-time' items to RFC3339 format
        """
        for item in record:
            if item in self.date_time_fields and record[item]:
                record[item] = pendulum.parse(record[item]).to_rfc3339_string()
        return record

    def extract_records(
        self,
        response: requests.Response,
    ) -> List[Record]:
        try:
            logger.info(f"The size of the response body is: {len(response.content)}")
            zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        except zipfile.BadZipFile:
            logger.exception(
                f"Received an invalid zip file in response to URL: {response.request.url}."
                f"The size of the response body is: {len(response.content)}"
            )
            return []

        for gzip_filename in zip_file.namelist():
            with zip_file.open(gzip_filename) as file:
                for record in self._parse_zip_file(file):
                    yield self._date_time_to_rfc3339(record)  # transform all `date-time` fields to RFC3339

    def _parse_zip_file(self, zip_file: Union[IO[bytes], str]) -> Iterable[MutableMapping]:
        with gzip.open(zip_file) as file:
            for record in file:
                yield json.loads(record)
