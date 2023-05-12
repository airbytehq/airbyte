#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests

from ..utils import read_full_refresh
from .base import JiraStream
from .projects import Projects


class ProjectEmail(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-email/#api-rest-api-3-project-projectid-email-get
    """

    primary_key = "projectId"
    skip_http_status_codes = [
        # You cannot edit the configuration of this project.
        requests.codes.FORBIDDEN
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.projects_stream = Projects(authenticator=self.authenticator, domain=self._domain, projects=self._projects)

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        return f"project/{stream_slice['project_id']}/email"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        for project in read_full_refresh(self.projects_stream):
            yield from super().read_records(stream_slice={"project_id": project["id"]}, **kwargs)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record["projectId"] = stream_slice["project_id"]
        return record
