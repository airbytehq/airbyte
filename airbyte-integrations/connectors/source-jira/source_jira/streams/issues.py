#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, MutableMapping, Optional

from ..utils import read_full_refresh
from .base import IncrementalJiraStream
from .issue_fields import IssueFields
from .projects import Projects


class Issues(IncrementalJiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-get
    """

    cursor_field = "updated"
    extract_field = "issues"
    use_cache = False  # disable caching due to OOM errors in kubernetes

    def __init__(self, expand_changelog: bool = False, render_fields: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._expand_changelog = expand_changelog
        self._render_fields = render_fields
        self._project_ids = []
        self.issue_fields_stream = IssueFields(authenticator=self.authenticator, domain=self._domain, projects=self._projects)
        self.projects_stream = Projects(authenticator=self.authenticator, domain=self._domain, projects=self._projects)

    def path(self, **kwargs) -> str:
        return "search"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any],
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params["fields"] = "*all"
        jql_parts = [self.jql_compare_date(stream_state)]
        if self._project_ids:
            project_ids = ", ".join([f"'{project_id}'" for project_id in self._project_ids])
            jql_parts.append(f"project in ({project_ids})")
        params["jql"] = " and ".join([p for p in jql_parts if p])
        expand = []
        if self._expand_changelog:
            expand.append("changelog")
        if self._render_fields:
            expand.append("renderedFields")
        if expand:
            params["expand"] = ",".join(expand)
        return params

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        self._project_ids = []
        if self._projects:
            self._project_ids = self.get_project_ids()
            if not self._project_ids:
                return
        yield from super().read_records(**kwargs)

    def transform(self, record: MutableMapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record["projectId"] = record["fields"]["project"]["id"]
        record["projectKey"] = record["fields"]["project"]["key"]
        record["created"] = record["fields"]["created"]
        record["updated"] = record["fields"]["updated"]
        return record

    def get_project_ids(self):
        return [project["id"] for project in read_full_refresh(self.projects_stream)]
