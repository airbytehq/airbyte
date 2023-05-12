#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Iterable, Mapping

import requests

from .base import JiraStream


class Permissions(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-permissions/#api-rest-api-3-permissions-get
    """

    extract_field = "permissions"
    primary_key = "key"
    skip_http_status_codes = [
        # You need to have Administer permissions to view this resource
        requests.codes.FORBIDDEN
    ]

    def path(self, **kwargs) -> str:
        return "permissions"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        records = response_json.get(self.extract_field, {}).values()
        yield from records
