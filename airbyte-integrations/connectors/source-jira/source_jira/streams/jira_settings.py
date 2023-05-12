#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import requests

from .base import JiraStream


class JiraSettings(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-jira-settings/#api-rest-api-3-application-properties-get
    """

    skip_http_status_codes = [
        # No permission
        requests.codes.FORBIDDEN
    ]

    def path(self, **kwargs) -> str:
        return "application-properties"
