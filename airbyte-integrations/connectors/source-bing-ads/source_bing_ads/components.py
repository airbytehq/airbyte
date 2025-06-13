# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import cached_property
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional

from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState


PARENT_SLICE_KEY: str = "parent_slice"


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
    Transform Campaigns records from Bing Ads API to ensure consistent data structure and types.

    This transformer handles two main transformations:

    Settings field transformations:
    1. For settings with Details, wrap the Details array in TargetSettingDetail structure:
       {"Details": {"TargetSettingDetail": original_details}}
    2. For settings without Details or with null Details, preserve the original structure
    3. Convert empty lists ([]) to null for backward compatibility
    4. Convert string values to integers for keys ending with "Id" (when valid integers)
    5. Convert PageFeedIds lists to object format: {"long": [int_values]}
    6. Wrap all transformed settings in {"Setting": transformed_settings}

    BiddingScheme field transformations:
    1. Recursively convert all integer values to floats to ensure consistent numeric type handling

    Example Settings transformation:
    Input:  {"Settings": [{"Type": "Target", "Details": [...], "PageFeedIds": ["123", "456"]}]}
    Output: {"Settings": {"Setting": [{"Type": "Target",
                                      "Details": {"TargetSettingDetail": [...]},
                                      "PageFeedIds": {"long": [123, 456]}}]}}

    Example BiddingScheme transformation:
    Input:  {"BiddingScheme": {"MaxCpc": {"Amount": 5}}}
    Output: {"BiddingScheme": {"MaxCpc": {"Amount": 5.0}}}
    """

    def transform(
        self,
        record: MutableMapping[str, Any],
        config: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        """
        Transform the record by converting the Settings and BiddingScheme properties.

        Args:
            record: The campaign record to transform (modified in-place)
            config: Optional configuration (unused)
            stream_state: Optional stream state (unused)
            stream_slice: Optional stream slice (unused)
        """
        settings = record.get("Settings")
        bidding_scheme = record.get("BiddingScheme")

        if settings:
            self._transform_settings_property(record, settings)

        if bidding_scheme:
            self._transform_bidding_scheme_property(bidding_scheme)

    def _transform_settings_property(self, record: MutableMapping[str, Any], settings: Any) -> None:
        """
        Transform the Settings property of a campaign record.
        Converts the Settings list into the expected nested structure and applies
        value transformations to individual setting properties.
        Args:
            record: The campaign record containing the Settings (modified in-place)
            settings: The Settings value from the record
        """
        if not isinstance(settings, list) or len(settings) == 0:
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
                transformed_setting = {
                    "Type": setting.get("Type"),
                    "Details": {"TargetSettingDetail": setting["Details"]},
                }
                # Add any other properties that might exist
                for key, value in setting.items():
                    if key not in ["Type", "Details"]:
                        transformed_setting[key] = self._transform_setting_value(key, value)
                transformed_settings.append(transformed_setting)
            else:
                # Keep setting as-is (no Details to wrap or Details is None)
                # But still convert empty lists to null and string IDs to integers
                transformed_setting = {}
                for key, value in setting.items():
                    transformed_setting[key] = self._transform_setting_value(key, value)
                transformed_settings.append(transformed_setting)

        # Wrap the transformed settings in the expected structure
        record["Settings"] = {"Setting": transformed_settings}

    def _transform_setting_value(self, key: str, value: Any) -> Any:
        """
        Transform individual setting values based on key name and value type.
        Applies specific transformations:
        - Empty lists become null
        - PageFeedIds lists become {"long": [int_values]} objects
        - String values for keys ending with "Id" become integers (when valid)
        Args:
            key: The setting property name
            value: The setting property value
        Returns:
            The transformed value
        """
        # Convert empty lists to null for backward compatibility
        if isinstance(value, list) and len(value) == 0:
            return None
        elif key == "PageFeedIds":
            # Convert PageFeedIds list to object with long array
            return self._convert_page_feed_id_lists(value)
        else:
            # Convert string IDs to integers
            return self._convert_id_strings_to_integers(key, value)

    def _transform_bidding_scheme_property(self, bidding_scheme: Any) -> None:
        """
        Transform the BiddingScheme property of a campaign record.
        Recursively converts all integer values to floats for consistent numeric handling.
        """
        if bidding_scheme and isinstance(bidding_scheme, dict):
            self._convert_integers_to_floats(bidding_scheme)

    def _convert_integers_to_floats(self, obj: MutableMapping[str, Any]) -> None:
        """
        Recursively convert integer values to floats in a dictionary.
        This ensures consistent numeric type handling across all BiddingScheme values.
        Only converts values that are whole numbers (int or float with no decimal part).
        """
        if not isinstance(obj, dict):
            return

        for key, value in obj.items():
            if isinstance(value, dict):
                self._convert_integers_to_floats(value)
                continue

            # Convert any whole numbers to float type
            if isinstance(value, (int, float)) and value == int(value):
                obj[key] = float(value)

    def _convert_id_strings_to_integers(self, key: str, value: Any) -> Any:
        """
        Convert string values to integers for keys ending with "Id".
        Only converts if the string represents a valid integer. If conversion fails,
        the original string value is preserved.
        """
        if key.endswith("Id") and isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                # If conversion fails, return original value
                return value
        return value

    def _convert_page_feed_id_lists(self, value: Any) -> Any:
        """
        Convert PageFeedIds from list of strings to object with long array of integers.
        This transformation is required for compatibility with the expected API format.
        If any string cannot be converted to an integer, the original value is returned.
        Example:
            Input:  ["8246337222870", "1234567890"]
            Output: {"long": [8246337222870, 1234567890]}
        """
        if isinstance(value, list) and len(value) > 0:
            try:
                # Convert string IDs to integers
                long_values = [int(id_str) for id_str in value if isinstance(id_str, str)]
                return {"long": long_values}
            except ValueError:
                # If conversion fails, return original value
                return value
        return value


@dataclass
class BulkDatetimeToRFC3339(RecordTransformation):
    """
    Bing Ads Bulk API provides datetime fields in custom format with milliseconds: "04/27/2023 18:00:14.970"
    Return datetime in RFC3339 format: "2023-04-27T18:00:14.970+00:00"
    """

    def transform(
        self,
        record: MutableMapping[str, Any],
        config: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        original_value = record["Modified Time"]
        record["Modified Time"] = (
            datetime.strptime(original_value, "%m/%d/%Y %H:%M:%S.%f").replace(tzinfo=timezone.utc).isoformat(timespec="milliseconds")
        )


@dataclass
class LightSubstreamPartitionRouter(SubstreamPartitionRouter):
    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        For migration to manifest connector we needed to migrate legacy state to per partition
        but regular SubstreamPartitionRouter will include the parent_slice in the partition that
        LegacyToPerPartitionStateMigration can't add in transformed state.
        Then, we remove the parent_slice.

        e.g.
        super().stream_slices() = [
            StreamSlice(partition={"parent_slice": {"user_id": 1, "parent_slice": {}}, "account_id": 1}, cursor_slice={}, extra_fields=None),
            StreamSlice(partition={"parent_slice": {"user_id": 2, "parent_slice": {}}, "account_id": 2}, cursor_slice={}, extra_fields=None)            ]
        Router yields: [
            StreamSlice(partition={"account_id": 1}, cursor_slice={}, extra_fields=None),
            StreamSlice(partition={"account_id": 2}, cursor_slice={}, extra_fields=None),
        ]
        """
        stream_slices = super().stream_slices()
        for stream_slice in stream_slices:
            stream_slice_partition: Dict[str, Any] = dict(stream_slice.partition)
            partition_keys = list(stream_slice_partition.keys())
            if PARENT_SLICE_KEY in partition_keys:
                partition_keys.remove(PARENT_SLICE_KEY)
                stream_slice_partition.pop(PARENT_SLICE_KEY, None)
            if len(partition_keys) != 1:
                raise ValueError(f"SubstreamDedupPartitionRouter expects a single partition key-value pair. Got {stream_slice_partition}")

            yield StreamSlice(
                partition=stream_slice_partition,
                cursor_slice=stream_slice.cursor_slice,
                extra_fields=stream_slice.extra_fields,
            )
