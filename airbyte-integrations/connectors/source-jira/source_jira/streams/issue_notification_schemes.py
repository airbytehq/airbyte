#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from .base import JiraStream


class IssueNotificationSchemes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-notification-schemes/#api-rest-api-3-notificationscheme-get
    """

    extract_field = "values"

    def path(self, **kwargs) -> str:
        return "notificationscheme"
