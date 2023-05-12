#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import requests

from .base import JiraStream


class IssueTypeScreenSchemes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-type-screen-schemes/#api-rest-api-3-issuetypescreenscheme-get
    """

    extract_field = "values"
    skip_http_status_codes = [
        # Only Jira administrators can access issue type screen schemes.
        requests.codes.FORBIDDEN
    ]

    def path(self, **kwargs) -> str:
        return "issuetypescreenscheme"
