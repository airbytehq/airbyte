#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, MutableMapping, Optional

from ..utils import read_full_refresh
from .base import JiraStream
from .users import Users


class UsersGroupsDetailed(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-users/#api-rest-api-3-user-get
    """

    primary_key = "accountId"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.users_stream = Users(authenticator=self.authenticator, domain=self._domain, projects=self._projects)

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        return "user"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any],
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params["accountId"] = stream_slice["accountId"]
        params["expand"] = "groups,applicationRoles"
        return params

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        for user in read_full_refresh(self.users_stream):
            yield from super().read_records(stream_slice={"accountId": user["accountId"]}, **kwargs)
