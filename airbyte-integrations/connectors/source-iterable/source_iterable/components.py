#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

import requests

from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor


@dataclass
class EventsRecordExtractor(DpathExtractor):
    common_fields = ("itblInternal", "_type", "createdAt", "email")

    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        jsonl_records = super().extract_records(response=response)
        for record_dict in jsonl_records:
            record_dict_common_fields = {}
            for field in self.common_fields:
                record_dict_common_fields[field] = record_dict.pop(field, None)
            yield {**record_dict_common_fields, "data": record_dict}
