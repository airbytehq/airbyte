#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


class WebflowAuthMixin:
    """
    Mixin class for providing additional HTTP header for specifying the "accept-version"
    """

    def __init__(self, *, accept_version_header: str = "accept-version", accept_version: str, **kwargs):
        super().__init__(**kwargs)
        self.accept_version = accept_version
        self.accept_version_header = accept_version_header

    def get_auth_header(self) -> Mapping[str, Any]:
        return {**super().get_auth_header(), self.accept_version_header: self.accept_version}


class WebflowTokenAuthenticator(WebflowAuthMixin, TokenAuthenticator):
    """
    Authentication class information
    https://docs.developers.webflow.com/reference/authorization
    """
