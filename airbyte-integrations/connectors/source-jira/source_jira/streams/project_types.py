#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from .base import JiraStream


class ProjectTypes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-types/#api-rest-api-3-project-type-get
    """

    primary_key = None

    def path(self, **kwargs) -> str:
        return "project/type"
