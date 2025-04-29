#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional

from airbyte_cdk.sources.declarative.extractors.http_selector import HttpSelector
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.requesters.requester import Requester
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
