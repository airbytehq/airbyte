#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from .base import JiraStream


class PermissionSchemes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-permission-schemes/#api-rest-api-3-permissionscheme-get
    """

    extract_field = "permissionSchemes"

    def path(self, **kwargs) -> str:
        return "permissionscheme"
