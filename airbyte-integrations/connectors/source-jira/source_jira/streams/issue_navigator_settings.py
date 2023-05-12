#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import requests

from .base import JiraStream


class IssueNavigatorSettings(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-navigator-settings/#api-rest-api-3-settings-columns-get
    """

    primary_key = None
    skip_http_status_codes = [
        # You need Administrator permission to perform this operation.
        requests.codes.FORBIDDEN
    ]

    def path(self, **kwargs) -> str:
        return "settings/columns"
