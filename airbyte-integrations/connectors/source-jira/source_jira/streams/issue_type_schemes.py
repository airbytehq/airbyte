#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import requests

from .base import JiraStream


class IssueTypeSchemes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-type-schemes/#api-rest-api-3-issuetypescheme-get
    """

    extract_field = "values"
    skip_http_status_codes = [
        # Only Jira administrators can access issue type schemes.
        requests.codes.FORBIDDEN
    ]

    def path(self, **kwargs) -> str:
        return "issuetypescheme"
