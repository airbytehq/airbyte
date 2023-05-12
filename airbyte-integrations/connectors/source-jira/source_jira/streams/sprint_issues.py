#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, MutableMapping, Optional

from ..utils import read_full_refresh
from .base import IncrementalJiraStream
from .issue_fields import IssueFields
from .sprints import Sprints


class SprintIssues(IncrementalJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/software/rest/api-group-sprint/#api-rest-agile-1-0-sprint-sprintid-issue-get
    """

    cursor_field = "updated"
    extract_field = "issues"
    api_v1 = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sprints_stream = Sprints(authenticator=self.authenticator, domain=self._domain, projects=self._projects)
        self.issue_fields_stream = IssueFields(authenticator=self.authenticator, domain=self._domain, projects=self._projects)

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        return f"sprint/{stream_slice['sprint_id']}/issue"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any],
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params["fields"] = stream_slice["fields"]
        jql = self.jql_compare_date(stream_state)
        if jql:
            params["jql"] = jql
        return params

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        fields = self.get_fields()
        for sprint in read_full_refresh(self.sprints_stream):
            stream_slice = {"sprint_id": sprint["id"], "fields": fields}
            yield from super().read_records(stream_slice=stream_slice, **kwargs)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record["issueId"] = record["id"]
        record["id"] = "-".join([str(stream_slice["sprint_id"]), record["id"]])
        record["sprintId"] = stream_slice["sprint_id"]
        record["created"] = record["fields"]["created"]
        record["updated"] = record["fields"]["updated"]
        return record

    def get_fields(self):
        fields = ["key", "status", "created", "updated"]
        field_ids_by_name = self.issue_fields_stream.field_ids_by_name()
        for name in ["Story Points", "Story point estimate"]:
            if name in field_ids_by_name:
                fields.extend(field_ids_by_name[name])
        return fields
