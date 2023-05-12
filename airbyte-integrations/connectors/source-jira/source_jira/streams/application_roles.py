#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import requests

from .base import JiraStream


class ApplicationRoles(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-application-roles/#api-rest-api-3-applicationrole-get
    """

    primary_key = "key"
    skip_http_status_codes = [
        # Application access permissions can only be edited or viewed by administrators.
        requests.codes.FORBIDDEN
    ]

    def path(self, **kwargs) -> str:
        return "applicationrole"
