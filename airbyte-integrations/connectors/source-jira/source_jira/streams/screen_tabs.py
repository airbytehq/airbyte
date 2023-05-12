#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re
from typing import Any, Iterable, Mapping, Optional

from ..utils import read_full_refresh
from .base import JiraStream
from .screens import Screens


class ScreenTabs(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-tabs/#api-rest-api-3-screens-screenid-tabs-get
    """

    raise_on_http_errors = False
    use_cache = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screens_stream = Screens(authenticator=self.authenticator, domain=self._domain, projects=self._projects)

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        return f"screens/{stream_slice['screen_id']}/tabs"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        for screen in read_full_refresh(self.screens_stream):
            yield from self.read_tab_records(stream_slice={"screen_id": screen["id"]}, **kwargs)

    def read_tab_records(self, stream_slice: Mapping[str, Any], **kwargs) -> Iterable[Mapping[str, Any]]:
        screen_id = stream_slice["screen_id"]
        for screen_tab in super().read_records(stream_slice={"screen_id": screen_id}, **kwargs):
            """
            For some projects jira creates screens automatically, which does not present in UI, but exist in screens stream.
            We receive 400 error "Screen with id {screen_id} does not exist" for tabs by these screens.
            """
            bad_request_reached = re.match(r"Screen with id \d* does not exist", screen_tab.get("errorMessages", [""])[0])
            if bad_request_reached:
                self.logger.info("Could not get screen tab for %s screen id. Reason: %s", screen_id, screen_tab["errorMessages"][0])
                return
            yield screen_tab
