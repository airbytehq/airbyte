#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass, field, InitVar
from typing import Any, List, Mapping

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor


@dataclass
class DedupingAccountsExtractor(RecordExtractor):
    """
    A record extractor to match deduplication behavior from the Python-based accounts stream
    Records are deduplicated based on the "Id" field.
    """

    # Required parameters that come from the declarative framework
    config: Optional[Config] = None
    parameters: InitVar[Mapping[str, Any]] = field(default_factory=dict)

    # Optional parameters with default values
    field_path: List[str] = field(default_factory=lambda: ["Accounts"])
    primary_key: str = "Id"

    # Fields not passed as parameters
    _seen_ids: set = field(default_factory=set, init=False)
    _dpath_extractor: DpathExtractor = field(init=False)

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        """Initialize after dataclass initialization"""
        self._dpath_extractor = DpathExtractor(
            field_path=self.field_path,
            config=self.config,
            parameters=parameters
        )

    def extract_records(self, response: Any) -> List[Mapping[str, Any]]:
        """
        Extract records from the response and deduplicate based on primary key.
        """
        # Use the standard extractor to get all records
        all_records = self._dpath_extractor.extract_records(response)

        # Filter out duplicates
        unique_records = []
        for record in all_records:
            record_id = record.get(self.primary_key)
            if record_id not in self._seen_ids:
                self._seen_ids.add(record_id)
                unique_records.append(record)

        return unique_records