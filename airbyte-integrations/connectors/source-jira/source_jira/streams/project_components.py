#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional

from ..utils import read_full_refresh
from .base import JiraStream
from .projects import Projects


class ProjectComponents(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-components/#api-rest-api-3-project-projectidorkey-component-get
    """

    extract_field = "values"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.projects_stream = Projects(authenticator=self.authenticator, domain=self._domain, projects=self._projects)

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        return f"project/{stream_slice['key']}/component"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        for project in read_full_refresh(self.projects_stream):
            yield from super().read_records(stream_slice={"key": project["key"]}, **kwargs)
