# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from functools import cached_property
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

from airbyte_cdk.sources.declarative.extractors.record_filter import (
    RecordFilter,
)
from airbyte_cdk.sources.declarative.transformations import (
    RecordTransformation,
)
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState


@dataclass
class DuplicatedRecordsFilter(RecordFilter):
    """
    Filter duplicated records based on the "Id" field.
    This can happen when we use predicates that could match the same record
    multiple times.

    e.g.
    With one record like:
    {"type":"RECORD","record":{"stream":"accounts","data":{"Id":151049662,
    "Name":"Airbyte Plumbing"},"emitted_at":1748277607993}}
    account_names in config:
    [
        {
          "name": "Airbyte",
          "operator": "Contains"
        },
        {
          "name": "Plumbing",
          "operator": "Contains"
        }
    ],
    will return the same record twice, once for each predicate.
    """

    CONFIG_PREDICATES = "account_names"

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self._seen_keys = set()

    @cached_property
    def _using_predicates(self) -> bool:
        """
        Indicates whether the connection uses predicates.
        :return: True if the connector uses predicates, False otherwise
        """
        predicates = self.config.get(self.CONFIG_PREDICATES)
        return bool(predicates and isinstance(predicates, list) and predicates)

    def filter_records(
        self, records: List[Mapping[str, Any]], stream_state: StreamState, stream_slice: Optional[StreamSlice] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        for record in records:
            if not self._using_predicates:
                yield record
            else:
                key = record["Id"]
                if key not in self._seen_keys:
                    self._seen_keys.add(key)
                    yield record


@dataclass
class BingAdsCampaignsRecordTransformer(RecordTransformation):
    """
    Transform the Settings field in Campaigns records
    by wrapping Details arrays in TargetSettingDetail
    structure. For settings without Details, keep the original
    structure.
    """

    def transform(
        self,
        record: MutableMapping[str, Any],
        config: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        """
        Transform the Settings field in the record.

        For settings with Details, wrap the Details array in
        TargetSettingDetail. For settings without Details, keep the original
        structure.
        """
        settings = record.get("Settings")

        if not settings or not isinstance(settings, list) or len(settings) == 0:
            # Keep original value (None, empty list, etc.)
            return

        transformed_settings = []

        for setting in settings:
            if not isinstance(setting, dict):
                # Keep non-dict settings as-is
                transformed_settings.append(setting)
                continue

            if "Details" in setting and setting["Details"] is not None:
                # Wrap Details in TargetSettingDetail only if Details is not None
                transformed_setting = {"Type": setting.get("Type"), "Details": {"TargetSettingDetail": setting["Details"]}}
                # Add any other properties that might exist
                for key, value in setting.items():
                    if key not in ["Type", "Details"]:
                        transformed_setting[key] = value
                transformed_settings.append(transformed_setting)
            else:
                # Keep setting as-is (no Details to wrap or Details is None)
                transformed_settings.append(setting)

        # Wrap the transformed settings in the expected structure
        record["Settings"] = {"Setting": transformed_settings}

        # Transform BiddingScheme field - convert all integer values to floats
        bidding_scheme = record.get("BiddingScheme")
        if bidding_scheme and isinstance(bidding_scheme, dict):
            self._convert_integers_to_floats(bidding_scheme)

    def _convert_integers_to_floats(self, obj):
        """
        Recursively convert integer values to floats in a dictionary.
        """
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, dict):
                    self._convert_integers_to_floats(value)
                elif isinstance(value, (int, float)) and value == int(value):
                    obj[key] = float(value)
