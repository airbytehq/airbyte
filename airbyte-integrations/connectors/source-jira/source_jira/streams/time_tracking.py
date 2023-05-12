#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import requests

from .base import JiraStream


class TimeTracking(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-time-tracking/#api-rest-api-3-configuration-timetracking-list-get
    """

    primary_key = "key"
    skip_http_status_codes = [
        # This resource is only available to administrators
        requests.codes.FORBIDDEN
    ]

    def path(self, **kwargs) -> str:
        return "configuration/timetracking/list"
