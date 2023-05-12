#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional

from .base import JiraStream


class Avatars(JiraStream):
    """
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-avatars/#api-rest-api-3-avatar-type-system-get
    """

    extract_field = "system"
    avatar_types = ("issuetype", "project", "user")

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        return f"avatar/{stream_slice['avatar_type']}/system"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        for avatar_type in self.avatar_types:
            yield {"avatar_type": avatar_type}
