#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from .base import JiraStream


class IssueResolutions(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-resolutions/#api-rest-api-3-resolution-search-get
    """

    extract_field = "values"

    def path(self, **kwargs) -> str:
        return "resolution/search"
