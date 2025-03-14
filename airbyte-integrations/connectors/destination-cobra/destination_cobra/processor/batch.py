# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import List

from airbyte_cdk import AirbyteRecordMessage


class Batch:
    def __init__(self):
        self._records = []

    def get(self) -> List[AirbyteRecordMessage]:
        return self._records

    def add(self, record: AirbyteRecordMessage) -> None:
        if self.is_full():
            raise ValueError("Batch is already full")
        self._records.append(record)

    def is_full(self) -> bool:
        """
        There are a lot of limitations defined in https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/salesforce_app_limits_platform_bulkapi.htm but we only check for some of these today. We will increase coverage as we face issues.
        """
        return len(self._records) >= 10_000

    def is_empty(self) -> bool:
        return len(self._records) != 0
