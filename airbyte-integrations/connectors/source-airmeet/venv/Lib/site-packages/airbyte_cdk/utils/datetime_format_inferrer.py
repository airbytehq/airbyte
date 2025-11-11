#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, Optional

from airbyte_cdk.models import AirbyteRecordMessage
from airbyte_cdk.sources.declarative.datetime.datetime_parser import DatetimeParser


class DatetimeFormatInferrer:
    """
    This class is used to detect toplevel fields in records that might be datetime values, along with the used format.
    """

    def __init__(self) -> None:
        self._parser = DatetimeParser()
        self._datetime_candidates: Optional[Dict[str, str]] = None
        self._formats = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%d %H:%M:%S.%f%z",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%s",
            "%ms",
            "%d/%m/%Y %H:%M",
            "%Y-%m",
            "%d-%m-%Y",
        ]
        self._timestamp_heuristic_ranges = [
            range(1_000_000_000, 2_000_000_000),
            range(1_000_000_000_000, 2_000_000_000_000),
        ]

    def _can_be_datetime(self, value: Any) -> bool:
        """Checks if the value can be a datetime.
        This is the case if the value is a string or an integer between 1_000_000_000 and 2_000_000_000 for seconds
        or between 1_000_000_000_000 and 2_000_000_000_000 for milliseconds.
        This is separate from the format check for performance reasons"""
        if isinstance(value, (str, int)):
            try:
                value_as_int = int(value)
                for timestamp_range in self._timestamp_heuristic_ranges:
                    if value_as_int in timestamp_range:
                        return True
            except ValueError:
                # given that it's not parsable as an int, it can represent a datetime with one of the self._formats
                return True
        return False

    def _matches_format(self, value: Any, format: str) -> bool:
        """Checks if the value matches the format"""
        try:
            self._parser.parse(value, format)
            return True
        except ValueError:
            return False

    def _initialize(self, record: AirbyteRecordMessage) -> None:
        """Initializes the internal state of the class"""
        self._datetime_candidates = {}
        for field_name, field_value in record.data.items():
            if not self._can_be_datetime(field_value):
                continue
            for format in self._formats:
                if self._matches_format(field_value, format):
                    self._datetime_candidates[field_name] = format
                    break

    def _validate(self, record: AirbyteRecordMessage) -> None:
        """Validates that the record is consistent with the inferred datetime formats"""
        if self._datetime_candidates:
            for candidate_field_name in list(self._datetime_candidates.keys()):
                candidate_field_format = self._datetime_candidates[candidate_field_name]
                current_value = record.data.get(candidate_field_name, None)
                if (
                    current_value is None
                    or not self._can_be_datetime(current_value)
                    or not self._matches_format(current_value, candidate_field_format)
                ):
                    self._datetime_candidates.pop(candidate_field_name)

    def accumulate(self, record: AirbyteRecordMessage) -> None:
        """Analyzes the record and updates the internal state of candidate datetime fields"""
        self._initialize(record) if self._datetime_candidates is None else self._validate(record)

    def get_inferred_datetime_formats(self) -> Dict[str, str]:
        """
        Returns the list of candidate datetime fields - the keys are the field names and the values are the inferred datetime formats.
        For these fields the format was consistent across all visited records.
        """
        return self._datetime_candidates or {}
