#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import re
from typing import Any, Mapping, MutableMapping, Optional, Union
from urllib.parse import parse_qsl, urlparse

import pendulum as pdm

from .exceptions import ShopifyBulkExceptions


# default end line tag
END_OF_FILE: str = "<end_of_file>"
BULK_PARENT_KEY: str = "__parentId"


class BulkTools:
    @staticmethod
    def camel_to_snake(camel_case: str) -> str:
        snake_case = []
        for char in camel_case:
            if char.isupper():
                snake_case.append("_" + char.lower())
            else:
                snake_case.append(char)
        return "".join(snake_case).lstrip("_")

    @staticmethod
    def filename_from_url(job_result_url: str) -> str:
        """
        Example of `job_result_url` (str) :
            https://storage.googleapis.com/shopify-tiers-assets-prod-us-east1/<some_hashed_sum>?
                GoogleAccessId=assets-us-prod%40shopify-tiers.iam.gserviceaccount.com&
                Expires=1705508208&
                Signature=<some_long_signature>%3D%3D&
                response-content-disposition=attachment%3B+filename%3D%22bulk-4147374162109.jsonl%22%3B+filename%2A%3DUTF-8%27%27bulk-4147374162109.jsonl&
                response-content-type=application%2Fjsonl

        Output:
            (str): bulk-4147374162109.jsonl
        """
        # Regular expression pattern to extract the filename
        filename_pattern = r'filename\*?=(?:UTF-8\'\')?"([^"]+)"'
        parsed_url = dict(parse_qsl(urlparse(job_result_url).query))
        match = re.search(filename_pattern, parsed_url.get("response-content-disposition", ""))
        if match:
            return match.group(1)
        else:
            raise ShopifyBulkExceptions.BulkJobResultUrlError(
                f"Could not extract the `filename` from `result_url` provided, details: {job_result_url}",
            )

    @staticmethod
    def shop_name_from_url(url: str) -> str:
        match = re.search(r"https://(.*?)(\.myshopify)", url)
        if match:
            return match.group(1)
        else:
            # safety net, if there is an error parsing url,
            # on no match is found
            return url

    @staticmethod
    def _datetime_str_to_rfc3339(value: str) -> str:
        return pdm.parse(value).to_rfc3339_string()

    @staticmethod
    def from_iso8601_to_rfc3339(record: Mapping[str, Any], field: str) -> Optional[str]:
        """
        Converts date-time as follows:
            Input: "2023-01-01T15:00:00Z"
            Output: "2023-01-01T15:00:00+00:00"
        If the value of the `field` is `None` we return it `as is`.
        """
        # some fields that expected to be resolved as ids, might not be populated for the particular `RECORD`,
        # we should return `None` to make the field `null` in the output as the result of the transformation.
        target_value = record.get(field)
        return BulkTools._datetime_str_to_rfc3339(target_value) if target_value else record.get(field)

    def fields_names_to_snake_case(self, dict_input: Optional[Mapping[str, Any]] = None) -> Optional[MutableMapping[str, Any]]:
        # transforming record field names from camel to snake case, leaving the `__parent_id` relation in place
        if dict_input:
            # the `None` type check is required, to properly handle nested missing entities (return None)
            return {self.camel_to_snake(k) if dict_input and k != BULK_PARENT_KEY else k: v for k, v in dict_input.items()}

    @staticmethod
    def resolve_str_id(
        str_input: Optional[str] = None, output_type: Optional[Union[int, str, float]] = int
    ) -> Optional[Union[int, str, float]]:
        # some fields that expected to be resolved as ids, might not be populated for the particular `RECORD`,
        # we should return `None` to make the field `null` in the output as the result of the transformation.
        if str_input:
            return output_type(re.search(r"\d+", str_input).group())
        else:
            return None
