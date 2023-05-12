#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, MutableMapping

from .base import JiraStream


class Boards(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/software/rest/api-group-other-operations/#api-agile-1-0-board-get
    """

    extract_field = "values"
    use_cache = True
    api_v1 = True

    def path(self, **kwargs) -> str:
        return "board"

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        for board in super().read_records(**kwargs):
            location = board.get("location", {})
            if not self._projects or location.get("projectKey") in self._projects:
                yield board

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        location = record.get("location")
        if location:
            record["projectId"] = str(location.get("projectId"))
            record["projectKey"] = location.get("projectKey")
        return record
