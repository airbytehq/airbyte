#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass

import requests

from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.types import Record


@dataclass
class WrappingDpathExtractor(DpathExtractor):
    """
    Record extractor that wraps the extracted value into a dict, with the value being set to the key `data`.
    This is done because the actual shape of the data is dynamic, so by wrapping everything into a `data` object
    it can be specified as a generic object in the schema.

    Note that this will cause fields to not be normalized in the destination.
    """

    def extract_records(self, response: requests.Response) -> list[Record]:
        records = super().extract_records(response)
        return [{"data": record} for record in records]
