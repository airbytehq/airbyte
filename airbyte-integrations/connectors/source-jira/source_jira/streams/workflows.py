#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import requests

from .base import JiraStream


class Workflows(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflows/#api-rest-api-3-workflow-search-get
    """

    extract_field = "values"
    skip_http_status_codes = [
        # Only Jira administrators can access workflows.
        requests.codes.FORBIDDEN
    ]

    def path(self, **kwargs) -> str:
        return "workflow/search"
