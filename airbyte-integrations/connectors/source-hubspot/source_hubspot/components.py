#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Union

import dpath
import requests

from airbyte_cdk.sources.declarative.decoders import Decoder, JsonDecoder
from airbyte_cdk.sources.declarative.extractors.http_selector import HttpSelector
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.requesters.requester import Requester
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState


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

    def __init__(self, cursor_field, config: Config):
        self.cursor_field = cursor_field
        self.config = config

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        # if start date wasn't provided in the config default date will be used
        start_date = self.config.get("start_date", "2006-06-01T00:00:00.000Z")
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
