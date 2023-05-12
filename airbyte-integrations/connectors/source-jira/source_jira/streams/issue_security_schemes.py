#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import requests

from .base import JiraStream


class IssueSecuritySchemes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-security-schemes/#api-rest-api-3-issuesecurityschemes-get
    """

    extract_field = "issueSecuritySchemes"
    skip_http_status_codes = [
        # You need to be a Jira administrator to perform this operation
        requests.codes.FORBIDDEN
    ]

    def path(self, **kwargs) -> str:
        return "issuesecurityschemes"
