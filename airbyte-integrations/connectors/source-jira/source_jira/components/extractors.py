# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, List, Mapping, Union

import dpath.util
import requests
from airbyte_cdk.sources.declarative.extractors import DpathExtractor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from requests_cache import Response


class LabelsRecordExtractor(DpathExtractor):
    """
    A custom record extractor is needed to handle cases when records are represented as list of strings insted of dictionaries.
    Example:
        -> ["label 1", "label 2", ..., "label n"]
        <- [{"label": "label 1"}, {"label": "label 2"}, ..., {"label": "label n"}]
    """

    def extract_records(self, response: Response) -> List[Mapping[str, Any]]:
        records = super().extract_records(response)
        return [{"label": record} for record in records]


class SingleRecordExtractor(DpathExtractor):
    """
    A custom record extractor is needed to handle cases when records are represented as dictionaries instead of list of dictionaries.
    Example:
        -> {"key 1": "value 1", "key 2": "value 2", "key n": "value n", ...}
        <- [{"key 1": "value 1", "key 2": "value 2", "key n": "value n", ...}]
    """

    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        response_body = [self.decoder.decode(response)]
        if len(self.field_path) == 0:
            extracted = response_body
        else:
            path = [path.eval(self.config) for path in self.field_path]
            if "*" in path:
                extracted = dpath.util.values(response_body, path)
            else:
                extracted = dpath.util.get(response_body, path, default=[])
        if isinstance(extracted, list):
            return extracted
        elif extracted:
            return [extracted]
        else:
            return []


class UnionListsRecordExtractor(DpathExtractor):
    """
    A custom record extractor is needed to handle cases when records are represented as values of multiple keys instead of list of dictionaries.
    Example:
        -> {"key 1": [{}, {}, ...], "key 2": [{}, {}, ...], "key n": [{}, {}, ...], ...}
        <- [{}, {}, ..., {}, {}, ..., {}, {}, ...,]
    """

    field_path: Union[InterpolatedString, str]

    def __post_init__(self, parameters: Mapping[str, Any]):
        if isinstance(self.field_path, str):
            self.field_path = InterpolatedString.create(self.field_path, parameters=parameters)

    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        response_body = self.decoder.decode(response)
        path = self.field_path.eval(self.config)
        extracted = dpath.util.values(response_body, path)
        if isinstance(extracted, list):
            return extracted
        elif extracted:
            return [extracted]
        else:
            return []
