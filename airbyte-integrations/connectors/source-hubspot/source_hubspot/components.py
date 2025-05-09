#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from datetime import timedelta
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union

import dpath
import requests

from airbyte_cdk.sources.declarative.datetime.datetime_parser import DatetimeParser
from airbyte_cdk.sources.declarative.decoders import Decoder, JsonDecoder
from airbyte_cdk.sources.declarative.extractors.http_selector import HttpSelector
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.requesters import HttpRequester
from airbyte_cdk.sources.declarative.requesters.requester import Requester
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now, ab_datetime_parse


class NewtoLegacyFieldTransformation(RecordTransformation):
    """
    Implements a custom transformation which adds the legacy field equivalent of v2 fields for streams which contain Deals and Contacts entities.

    This custom implementation was developed in lieu of the AddFields component due to the dynamic-nature of the record properties for the HubSpot source. Each

    For example:
    hs_v2_date_exited_{stage_id} -> hs_date_exited_{stage_id} where {stage_id} is a user-generated value
    """

    def __init__(self, field_mapping: Dict[str, str]) -> None:
        self._field_mapping = field_mapping

    def transform(
        self,
        record_or_schema: Dict[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        """
        Transform a record in place by adding fields directly to the record by manipulating the injected fields into a legacy field to avoid breaking syncs.

        :param record_or_schema: The input record or schema to be transformed.
        """
        is_record = record_or_schema.get("properties") is not None

        for field, value in list(record_or_schema.get("properties", record_or_schema).items()):
            for legacy_field, new_field in self._field_mapping.items():
                if new_field in field:
                    transformed_field = field.replace(new_field, legacy_field)

                    if legacy_field == "hs_lifecyclestage_" and not transformed_field.endswith("_date"):
                        transformed_field += "_date"

                    if is_record:
                        if record_or_schema["properties"].get(transformed_field) is None:
                            record_or_schema["properties"][transformed_field] = value
                    else:
                        if record_or_schema.get(transformed_field) is None:
                            record_or_schema[transformed_field] = value


class MigrateEmptyStringState(StateMigration):
    cursor_field: str
    config: Config
    cursor_format: Optional[str] = None

    def __init__(self, cursor_field, config: Config, cursor_format: Optional[str] = None):
        self.cursor_field = cursor_field
        self.cursor_format = cursor_format
        self.config = config

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        # if start date wasn't provided in the config default date will be used
        start_date = self.config.get("start_date", "2006-06-01T00:00:00.000Z")
        if self.cursor_format:
            dt = ab_datetime_parse(start_date)
            formatted_start_date = DatetimeParser().format(dt, self.cursor_format)
            return {self.cursor_field: formatted_start_date}

        return {self.cursor_field: start_date}

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return stream_state.get(self.cursor_field) == ""


@dataclass
class HubspotPropertyHistoryExtractor(RecordExtractor):
    """
    Custom record extractor which parses the JSON response from Hubspot and for each instance returned for the specified
    object type (ex. Contacts, Deals, etc.), yields records for every requested property. Because this is a property
    history stream, an individual property can yield multiple records representing the previous version of that property.

    The custom behavior of this component is:
    - Iterating over and extracting property history instances as individual records
    - Injecting fields from out levels of the response into yielded records to be used as primary keys
    """

    field_path: List[Union[InterpolatedString, str]]
    entity_primary_key: str
    additional_keys: Optional[List[str]]
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    decoder: Decoder = field(default_factory=lambda: JsonDecoder(parameters={}))

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._field_path = [InterpolatedString.create(path, parameters=parameters) for path in self.field_path]
        for path_index in range(len(self.field_path)):
            if isinstance(self.field_path[path_index], str):
                self._field_path[path_index] = InterpolatedString.create(self.field_path[path_index], parameters=parameters)

    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        for body in self.decoder.decode(response):
            results = []
            if len(self._field_path) == 0:
                extracted = body
            else:
                path = [path.eval(self.config) for path in self._field_path]
                if "*" in path:
                    extracted = dpath.values(body, path)
                else:
                    extracted = dpath.get(body, path, default=[])  # type: ignore # extracted will be a MutableMapping, given input data structure
            if isinstance(extracted, list):
                results = extracted
            elif extracted:
                raise ValueError(f"field_path should always point towards a list field in the response body for property_history streams")

            for result in results:
                properties_with_history = result.get("propertiesWithHistory")
                primary_key = result.get("id")
                additional_keys = (
                    {additional_key: result.get(additional_key) for additional_key in self.additional_keys} if self.additional_keys else {}
                )

                if properties_with_history:
                    for property_name, value_dict in properties_with_history.items():
                        if property_name == "hs_lastmodifieddate":
                            # Skipping the lastmodifieddate since it only returns the value
                            # when one field of a record was changed no matter which
                            # field was changed. It therefore creates overhead, since for
                            # every changed property there will be the date it was changed in itself
                            # and a change in the lastmodifieddate field.
                            continue
                        for version in value_dict:
                            version["property"] = property_name
                            version[self.entity_primary_key] = primary_key
                            yield version | additional_keys


@dataclass
class AddFieldsFromEndpointTransformation(RecordTransformation):
    """
    Makes request to provided endpoint and updates record with retrieved data.

    requester: Requester
    record_selector: HttpSelector
    """

    requester: Requester
    record_selector: HttpSelector

    def transform(
        self,
        record: Dict[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        additional_data_response = self.requester.send_request(
            stream_slice=StreamSlice(partition={"parent_id": record["id"]}, cursor_slice={})
        )
        additional_data = self.record_selector.select_records(response=additional_data_response, stream_state={}, records_schema={})

        for data in additional_data:
            record.update(data)


class EngagementsHttpRequester(HttpRequester):
    """
    Engagements stream uses different endpoints:
    - Engagements Recent if start_date/state is less than 30 days and API is able to return all records (<10k), or
    - Engagements All which extracts all records, but supports filter on connector side

    Recent Engagements API:
    https://legacydocs.hubspot.com/docs/methods/engagements/get-recent-engagements

    Important: This endpoint returns only last 10k most recently updated records in the last 30 days.

    All Engagements API:
    https://legacydocs.hubspot.com/docs/methods/engagements/get-all-engagements

    Important:

    1. The stream is declared to use one stream slice from start date(default/config/state) to time.now(). It doesn't have step.
    Based on this we can use stream_slice["start_time"] and be sure that this is equal to value in initial state.
    Stream Slice [start_time] is used to define _use_recent_api, concurrent processing of date windows is incompatible and therefore does not support using a step
    2.The stream is declared to use 250 as page size param in pagination.
    Recent Engagements API have 100 as max param but doesn't fail is bigger value was provided and returns to 100 as default.
    3. The stream has is_client_side_incremental=true to filter Engagements All response.
    """

    recent_api_total_records_limit = 10000
    recent_api_last_days_limit = 29

    recent_api_path = "/engagements/v1/engagements/recent/modified"
    all_api_path = "/engagements/v1/engagements/paged"

    _use_recent_api = None

    def should_use_recent_api(self, stream_slice: StreamSlice) -> bool:
        if self._use_recent_api is not None:
            return self._use_recent_api

        # Recent engagements API returns records updated in the last 30 days only. If start time is older All engagements API should be used
        if int(stream_slice["start_time"]) >= int(
            DatetimeParser().format((ab_datetime_now() - timedelta(days=self.recent_api_last_days_limit)), "%ms")
        ):
            # Recent engagements API returns only 10k most recently updated records.
            # API response indicates that there are more records so All engagements API should be used
            _, response = self._http_client.send_request(
                http_method=self.get_method().value,
                url=self._join_url(self.get_url_base(), self.recent_api_path),
                headers=self._request_headers({}, stream_slice, {}, {}),
                params={"count": 250, "since": stream_slice["start_time"]},
                request_kwargs={"stream": self.stream_response},
            )
            if response.json().get("total") <= self.recent_api_total_records_limit:
                self._use_recent_api = True
        else:
            self._use_recent_api = False

        return self._use_recent_api

    def get_path(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        if self.should_use_recent_api(stream_slice):
            return self.recent_api_path
        return self.all_api_path

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        request_params = self._request_options_provider.get_request_params(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )
        if self.should_use_recent_api(stream_slice):
            request_params.update({"since": stream_slice["start_time"]})
        return request_params
