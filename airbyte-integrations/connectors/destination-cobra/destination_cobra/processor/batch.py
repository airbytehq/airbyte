# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Iterable, List

from airbyte_cdk import AirbyteRecordMessage


class CsvSizeEstimator:
    _BREAKLINE_SIZE_IN_BYTES = 1  # assumes LF and not CRLF

    def __init__(self) -> None:
        self._headers = set()
        self._records_in_bytes = 0

    def add(self, record: AirbyteRecordMessage) -> None:
        self._headers.update(record.data.keys())
        self._records_in_bytes += self._size_in_bytes(record.data.values()) + self._BREAKLINE_SIZE_IN_BYTES

    def get_size(self) -> int:
        return self._size_in_bytes(self._headers) + self._records_in_bytes

    @staticmethod
    def _size_in_bytes(values: Iterable[Any]) -> int:
        return len(",".join([str(value) for value in values]).encode("utf-8"))


class Batch:
    def __init__(self, max_batch_size_in_bytes: int):
        self._records = []
        self._max_batch_size_in_bytes = max_batch_size_in_bytes
        self._size_estimator = CsvSizeEstimator()

    def get(self) -> List[AirbyteRecordMessage]:
        return self._records

    def add(self, record: AirbyteRecordMessage) -> None:
        if self.is_full():
            raise ValueError("Batch is already full")
        self._records.append(record)
        self._size_estimator.add(record)

    def is_full(self) -> bool:
        """
        There are a lot of limitations defined in https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/salesforce_app_limits_platform_bulkapi.htm but we only check for some of these today. We will increase coverage as we face issues.

        Also note that this is not very exact because is_full is evaluated before adding a record and therefore the addition of the record could break the 100 MB limit. That being said, the Salesforce API documentation seems to allow for a bit a wiggle room so I imagine this would only be an issue with very big records.
        """
        return self._size_estimator.get_size() >= self._max_batch_size_in_bytes

    def is_empty(self) -> bool:
        return len(self._records) == 0
