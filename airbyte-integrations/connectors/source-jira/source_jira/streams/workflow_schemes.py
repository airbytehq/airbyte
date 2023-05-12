#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import requests

from .base import JiraStream


class WorkflowSchemes(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflow-schemes/#api-rest-api-3-workflowscheme-get
    """

    extract_field = "values"
    skip_http_status_codes = [
        # Only Jira administrators can access workflow scheme associations.
        requests.codes.FORBIDDEN
    ]

    def path(self, **kwargs) -> str:
        return "workflowscheme"
