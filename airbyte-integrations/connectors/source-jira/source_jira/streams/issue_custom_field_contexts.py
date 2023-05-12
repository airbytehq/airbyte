#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional

import requests

from ..utils import read_full_refresh
from .base import JiraStream
from .issue_fields import IssueFields


class IssueCustomFieldContexts(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-custom-field-contexts/#api-rest-api-3-field-fieldid-context-get
    """

    extract_field = "values"
    skip_http_status_codes = [
        # https://community.developer.atlassian.com/t/get-custom-field-contexts-not-found-returned/48408/2
        # /rest/api/3/field/{fieldId}/context - can return 404 if project style is not "classic"
        requests.codes.NOT_FOUND,
        # Only Jira administrators can access custom field contexts.
        requests.codes.FORBIDDEN,
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.issue_fields_stream = IssueFields(authenticator=self.authenticator, domain=self._domain, projects=self._projects)

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        return f"field/{stream_slice['field_id']}/context"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        for field in read_full_refresh(self.issue_fields_stream):
            if field.get("custom", False):
                yield from super().read_records(stream_slice={"field_id": field["id"]}, **kwargs)
