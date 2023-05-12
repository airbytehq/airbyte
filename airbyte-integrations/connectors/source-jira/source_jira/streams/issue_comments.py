#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional

from source_jira.streams.base import IncrementalJiraStream
from source_jira.streams.issues import Issues

from ..utils import read_incremental


class IssueComments(IncrementalJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-get
    """

    extract_field = "comments"
    cursor_field = "updated"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.issues_stream = Issues(
            authenticator=self.authenticator,
            domain=self._domain,
            projects=self._projects,
            start_date=self._start_date,
        )

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        return f"issue/{stream_slice['key']}/comment"

    def read_records(
        self, stream_slice: Optional[Mapping[str, Any]] = None, stream_state: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        for issue in read_incremental(self.issues_stream, stream_state=stream_state):
            stream_slice = {"key": issue["key"]}
            yield from super().read_records(stream_slice=stream_slice, stream_state=stream_state, **kwargs)
