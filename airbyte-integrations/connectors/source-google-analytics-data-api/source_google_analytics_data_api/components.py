#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from itertools import islice
from typing import Any, Iterable, List, MutableMapping

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor


@dataclass
class CombinedExtractor(RecordExtractor):
    """
    Extractor that merges the output of multiple sub-extractors into a single record.
    This extractor takes a list of `RecordExtractor` instances (`extractors`), each of which
    independently extracts records from the response. For each response, the extractor:
    1. Invokes each sub-extractor to generate iterables of records.
    2. Zips the results together, so that the first record from each extractor is combined,
       the second from each, and so on.
    3. Merges each group of records into a single dictionary using `dict.update()`.
    The result is a sequence of dictionaries where each dictionary contains the merged keys
    and values from the corresponding records across all extractors.
    Example:
        keys_extractor -> yields: [{"name": "Alice", "age": 30}]
        extra_data_extractor -> yields: [{"country": "US"}]
        CombinedExtractor(extractors=[keys_extractor, extra_data_extractor]) ->
            yields: [{"name": "Alice", "age": 30, "country": "US"}]
    """

    extractors: List[RecordExtractor]

    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[Any, Any]]:
        extractors_records = [extractor.extract_records(response) for extractor in self.extractors]

        for records in zip(*extractors_records):
            merged = {}
            for record in records:
                merged.update(record)  # merge all fields
            yield merged


@dataclass
class KeyValueExtractor(RecordExtractor):
    """
    Extractor that combines keys and values from two separate extractors.

    The `keys_extractor` and `values_extractor` extract records independently
    from the response. Their outputs are zipped together to form key-value mappings.

    Each key from `keys_extractor` should correspond to a key in the resulting dictionary,
    and each value from `values_extractor` is the value for that key.

    Example:
      keys_extractor -> yields: ["name", "age"]
      values_extractor -> yields: ["Alice", 30]
      result: { "name": "Alice", "age": 30 }
    """

    keys_extractor: RecordExtractor
    values_extractor: RecordExtractor

    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[Any, Any]]:
        keys = list(self.keys_extractor.extract_records(response))
        values = self.values_extractor.extract_records(response)

        yield dict(zip(keys, values))
