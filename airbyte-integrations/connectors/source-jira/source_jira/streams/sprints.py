#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional

from ..utils import read_full_refresh
from .base import JiraStream
from .boards import Boards


class Sprints(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/#api-rest-agile-1-0-board-boardid-sprint-get
    """

    extract_field = "values"
    use_cache = True
    api_v1 = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.boards_stream = Boards(authenticator=self.authenticator, domain=self._domain, projects=self._projects)

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        return f"board/{stream_slice['board_id']}/sprint"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        available_board_types = ["scrum", "simple"]
        for board in read_full_refresh(self.boards_stream):
            if board["type"] in available_board_types:
                yield from super().read_records(stream_slice={"board_id": board["id"]}, **kwargs)
