#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional

from ..utils import read_full_refresh
from .base import JiraStream
from .filters import Filters


class FilterSharing(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-filter-sharing/#api-rest-api-3-filter-id-permission-get
    """

    def __init__(self, render_fields: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.filters_stream = Filters(authenticator=self.authenticator, domain=self._domain, projects=self._projects)

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        return f"filter/{stream_slice['filter_id']}/permission"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        for filters in read_full_refresh(self.filters_stream):
            yield from super().read_records(stream_slice={"filter_id": filters["id"]}, **kwargs)
