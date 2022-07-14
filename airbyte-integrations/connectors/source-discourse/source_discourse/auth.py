#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, Mapping

from requests.auth import AuthBase


class DiscourseAuthenticator(AuthBase):
    def __init__(self, api_key, api_username):
        self.api_key = api_key
        self.username = api_username

    def __call__(self, request):
        request.headers.update(self.get_auth_header())
        return request

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"Api-Key": self.api_key, "Api-Username": self.username}
