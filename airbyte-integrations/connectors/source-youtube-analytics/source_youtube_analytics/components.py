#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import csv
import io
from typing import List

import requests
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.types import Record


class ReportsExtractor(RecordExtractor):
    def extract_records(self, response: requests.Response) -> List[Record]:  # type: ignore
        fp = io.StringIO(response.text)
        reader = csv.DictReader(fp)
        for record in reader:
            yield record
