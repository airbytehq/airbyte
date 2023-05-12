#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional

from ..utils import read_full_refresh
from .base import StartDateJiraStream
from .issues import Issues


class IssueWatchers(StartDateJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-watchers/#api-rest-api-3-issue-issueidorkey-watchers-get

    extract_field is commented for the same reason as issue_voters.
    """

    # extract_field = "watchers"
    primary_key = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.issues_stream = Issues(
            authenticator=self.authenticator,
            domain=self._domain,
            projects=self._projects,
            start_date=self._start_date,
        )

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        return f"issue/{stream_slice['key']}/watchers"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        for issue in read_full_refresh(self.issues_stream):
            yield from super().read_records(stream_slice={"key": issue["key"]}, **kwargs)
