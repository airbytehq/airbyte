#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from dataclasses import InitVar, dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Union

import dpath
import requests

from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState


class NewtoLegacyFieldTransformation(RecordTransformation):
    """
    Implements a custom transformation which adds the legacy field equivalent of v2 fields for streams which contain Deals and Contacts entities.

    This custom implmentation was developed in lieu of the AddFields component due to the dynamic-nature of the record properties for the HubSpot source. Each

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


@dataclass
class ListFieldToSingleRecordByPkExtractor(DpathExtractor):
    pk_field_path: List[Union[InterpolatedString, str]] = None
    related_field_path: List[Union[InterpolatedString, str]] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self._pk_field_path = [InterpolatedString.create(path, parameters=parameters) for path in self.pk_field_path]
        for path_index in range(len(self.pk_field_path)):
            if isinstance(self.pk_field_path[path_index], str):
                self._pk_field_path[path_index] = InterpolatedString.create(self.pk_field_path[path_index], parameters=parameters)

        self._related_field_path = [InterpolatedString.create(path, parameters=parameters) for path in self.related_field_path]
        for path_index in range(len(self.related_field_path)):
            if isinstance(self.related_field_path[path_index], str):
                self._related_field_path[path_index] = InterpolatedString.create(self.related_field_path[path_index], parameters=parameters)

    def extract_records(
        self,
        response: requests.Response,
    ) -> Iterable[Mapping[str, Any]]:
        pk_field_path = [path.eval(self.config) for path in self._pk_field_path]
        related_field_path = [path.eval(self.config) for path in self._related_field_path]

        for record in super().extract_records(response):
            pk_field_value = dpath.get(record, pk_field_path, default="")
            related_field_values = dpath.get(record, related_field_path, default=[])

            for related_field_value in related_field_values:
                updated_record = record.copy()
                updated_record = dpath.new(updated_record, pk_field_path, pk_field_value)
                updated_record = dpath.new(updated_record, related_field_path, related_field_value)
                updated_record = dpath.new(updated_record, related_field_path + pk_field_path, pk_field_value)
                yield updated_record


@dataclass
class UnnestFields(RecordTransformation):
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    field_path: List[Union[InterpolatedString, str]]

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._field_path = [InterpolatedString.create(path, parameters=parameters) for path in self.field_path]
        for path_index in range(len(self.field_path)):
            if isinstance(self.field_path[path_index], str):
                self._field_path[path_index] = InterpolatedString.create(self.field_path[path_index], parameters=parameters)

    def transform(
        self,
        record: Dict[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        field_path = [path.eval(self.config) for path in self._field_path]
        field_value = dpath.get(record, field_path, default={})

        updated_values = {}

        for key, value in field_value.items():
            updated_values[f"{field_path[0]}_{key}"] = value

        record.update(updated_values)
