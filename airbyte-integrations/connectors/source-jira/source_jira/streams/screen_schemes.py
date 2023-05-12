#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import requests

from .base import JiraStream


class ScreenSchemes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-schemes/#api-rest-api-3-screenscheme-get
    """

    extract_field = "values"
    skip_http_status_codes = [
        # Only Jira administrators can access screen schemes.
        requests.codes.FORBIDDEN
    ]

    def path(self, **kwargs) -> str:
        return "screenscheme"
