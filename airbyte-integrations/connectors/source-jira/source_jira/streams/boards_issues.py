#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, MutableMapping, Optional

from ..utils import read_full_refresh
from .base import IncrementalJiraStream
from .boards import Boards


class BoardIssues(IncrementalJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/#api-rest-agile-1-0-board-boardid-issue-get
    """

    cursor_field = "updated"
    extract_field = "issues"
    api_v1 = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.boards_stream = Boards(authenticator=self.authenticator, domain=self._domain, projects=self._projects)

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        return f"board/{stream_slice['board_id']}/issue"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any],
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params["fields"] = ["key", "created", "updated"]
        jql = self.jql_compare_date(stream_state)
        if jql:
            params["jql"] = jql
        return params

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        for board in read_full_refresh(self.boards_stream):
            yield from super().read_records(stream_slice={"board_id": board["id"]}, **kwargs)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record["boardId"] = stream_slice["board_id"]
        record["created"] = record["fields"]["created"]
        record["updated"] = record["fields"]["updated"]
        return record
