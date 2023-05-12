#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from .base import JiraStream


class Dashboards(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-dashboards/#api-rest-api-3-dashboard-get
    """

    extract_field = "dashboards"

    def path(self, **kwargs) -> str:
        return "dashboard"
