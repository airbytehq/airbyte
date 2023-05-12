#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import requests

from .base import JiraStream


class Screens(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screens/#api-rest-api-3-screens-get
    """

    extract_field = "values"
    use_cache = True
    skip_http_status_codes = [
        # Only Jira administrators can manage screens.
        requests.codes.FORBIDDEN
    ]

    def path(self, **kwargs) -> str:
        return "screens"
