#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List, Mapping

from ..utils import read_full_refresh
from .base import JiraStream


class IssueFields(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-fields/#api-rest-api-3-field-get
    """

    use_cache = True

    def path(self, **kwargs) -> str:
        return "field"

    def field_ids_by_name(self) -> Mapping[str, List[str]]:
        results = {}
        for f in read_full_refresh(self):
            results.setdefault(f["name"], []).append(f["id"])
        return results
