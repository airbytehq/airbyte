#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import re
from typing import Any, Mapping
from urllib.parse import parse_qsl, urlparse

import pendulum as pdm

from .exceptions import ShopifyBulkExceptions
from .query import PARENT_KEY


class BulkTools:
    @staticmethod
    def camel_to_snake(camel_case: str):
        snake_case = []
        for char in camel_case:
            if char.isupper():
                snake_case.append("_" + char.lower())
            else:
                snake_case.append(char)
        return "".join(snake_case).lstrip("_")

    @staticmethod
    def filename_from_url(job_result_url: str) -> str:
        # Regular expression pattern to extract the filename
        filename_pattern = r'filename\*?=(?:UTF-8\'\')?"([^"]+)"'
        parsed_url = dict(parse_qsl(urlparse(job_result_url).query))
        match = re.search(filename_pattern, parsed_url.get("response-content-disposition")).group(1)
        if match:
            return match
        else:
            raise ShopifyBulkExceptions.BulkJobResultUrlError(
                f"Could not extract the `filename` from `result_url` provided, details: {job_result_url}",
            )

    @staticmethod
    def from_iso8601_to_rfc3339(record: Mapping[str, Any], field: str) -> Mapping[str, Any]:
        """
        Converts date-time as follows:
            Input: "2023-01-01T15:00:00Z"
            Output: "2023-01-01T15:00:00+00:00"
        If the value of the `field` is `None` we return it `as is`.
        """
        target_value = record.get(field)
        return pdm.parse(target_value).to_rfc3339_string() if target_value else record.get(field)

    def fields_names_to_snake_case(self, record: Mapping[str, Any]) -> Mapping[str, Any]:
        # transforming record field names from camel to snake case,
        # leaving the `__parent_id` relation in place.
        return {self.camel_to_snake(k) if k != PARENT_KEY else k: v for k, v in record.items()}
