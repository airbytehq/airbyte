#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, MutableMapping, Optional

import pendulum

from ..utils import read_incremental
from .base import IncrementalJiraStream, StartDateJiraStream
from .issues import Issues


class UpdatedIssueWorklogs(IncrementalJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-worklogs/#api-rest-api-3-worklog-updated-get
    """

    extract_field = "values"
    primary_key = "worklogId"
    cursor_field = "updatedTime"

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        return "worklog/updated"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        since = self.get_starting_point(stream_state)
        if since:
            return {"since": int(since.float_timestamp * 1000)}

    def read_records(
        self, stream_slice: Optional[Mapping[str, Any]] = None, stream_state: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        start_point = self.get_starting_point(stream_state=stream_state)
        cursor_value = None
        for record in super(StartDateJiraStream, self).read_records(stream_slice=stream_slice, stream_state=stream_state, **kwargs):
            if isinstance(record[self.cursor_field], str):
                cursor_value = pendulum.parse(record[self.cursor_field])
            if isinstance(record[self.cursor_field], int):
                cursor_value = pendulum.from_timestamp(record[self.cursor_field] / 1000)
            if not start_point or cursor_value >= start_point:
                yield record


class AllIssueWorklogs(IncrementalJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-worklogs/#api-rest-api-3-worklog-list-post
    AllIssueWorklogs Stream is used in case no project in config, to skip syncing of all related to project issues and retrieving worklog by issue.
    Instead, we get all updated worklogs and sync them, without retrieving big amount of issues.
    """

    cursor_field = "updated"
    http_method = "POST"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.updated_issue_worklogs = UpdatedIssueWorklogs(
            authenticator=self.authenticator,
            domain=self._domain,
            projects=self._projects,
            start_date=self._start_date,
        )

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Accept": "application/json", "Content-Type": "application/json"}

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        return "worklog/list"

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        worklogs_ids = [worklog["worklogId"] for worklog in read_incremental(self.updated_issue_worklogs, stream_state=stream_state)]
        return {"ids": worklogs_ids}

    def read_records(
        self, stream_slice: Optional[Mapping[str, Any]] = None, stream_state: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        return super().read_records(stream_slice=stream_slice, stream_state=stream_state, **kwargs)


class IssueWorklogs(IncrementalJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-worklogs/#api-rest-api-3-issue-issueidorkey-worklog-get
    IssueWorklogs Stream is used in case when we have projects in config.
    """

    extract_field = "worklogs"
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
        return f"issue/{stream_slice['key']}/worklog"

    def read_records(
        self, stream_slice: Optional[Mapping[str, Any]] = None, stream_state: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        for issue in read_incremental(self.issues_stream, stream_state=stream_state):
            stream_slice = {"key": issue["key"]}
            yield from super().read_records(stream_slice=stream_slice, stream_state=stream_state, **kwargs)
