#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
from dataclasses import dataclass
from io import StringIO
from typing import Any, Iterable, Mapping

import requests
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor


@dataclass
class CSVExtractor(RecordExtractor):
    """
    Record extractor that takes a response in, assumes it's in CSV format, and returns the array of records.

    Examples:
    ```
      extractor:
        type: CSVExtractor
    ```

    ```
      extractor:
        type: Extractor
        separator: ","
        quotechar: '"'
    ```

    Attributes:
        separator (str): Record separator in the incoming CSV.
        quotechar (str): Quotation character used in the CSV.
    """

    separator: str
    quotechar: str

    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        try:
            csv_data = StringIO(response.text)
            csv_reader = csv.reader(csv_data, delimiter=self.separator, quotechar=self.quotechar)
        except csv.Error:
            return []

        header = next(csv_reader)
        if header is None:
            yield from []
        else:
            keys = [column.strip() for column in header]
            for row in csv_reader:
                yield dict(zip(keys, row))
