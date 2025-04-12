# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Callable

from office365.sharepoint.client_context import ClientContext

from source_microsoft_sharepoint.sharepoint_client import SourceMicrosoftSharePointClient
from source_microsoft_sharepoint.spec import SourceMicrosoftSharePointSpec
from source_microsoft_sharepoint.utils import get_site_prefix


class SharepointBaseReader:
    """
    Base class with common methods for SharePoint readers.
    """

    def __init__(self):
        self._auth_client = None
        self._one_drive_client = None
        self._config = None
        self._site_url = None
        self._root_site_prefix = None

    @property
    def config(self) -> SourceMicrosoftSharePointSpec:
        return self._config

    @config.setter
    def config(self, value: SourceMicrosoftSharePointSpec):
        """
        The FileBasedSource reads and parses configuration from a file, then sets this configuration in its StreamReader. While it only
        uses keys from its abstract configuration, concrete StreamReader implementations may need additional keys for third-party
        authentication. Therefore, subclasses of AbstractFileBasedStreamReader should verify that the value in their config setter
        matches the expected config type for their StreamReader.
        """
        assert isinstance(value, SourceMicrosoftSharePointSpec)
        self._config = value

    @property
    def auth_client(self):
        # Lazy initialization of the auth_client
        if self._auth_client is None:
            self._auth_client = SourceMicrosoftSharePointClient(self._config)
        return self._auth_client

    @property
    def one_drive_client(self):
        # Lazy initialization of the one_drive_client
        if self._one_drive_client is None:
            self._one_drive_client = self.auth_client.client
        return self._one_drive_client

    def _set_sites_info(self):
        self._site_url, self._root_site_prefix = get_site_prefix(self.one_drive_client)

    @property
    def site_url(self) -> str:
        if not self._site_url:
            self._set_sites_info()
        return self._site_url

    @property
    def root_site_prefix(self) -> str:
        if not self._root_site_prefix:
            self._set_sites_info()
        return self._root_site_prefix

    def get_token_response_object(self, tenant_prefix: str) -> Callable:
        """
        When building a ClientContext using with_access_token() method,
        the token_func param is expected to be a method/callable that returns a TokenResponse object.
        tenant_prefix is used to determine the scope of the access token.
        return: A callable that returns a TokenResponse object.
        """
        return self.auth_client.get_token_response_object_wrapper(tenant_prefix=tenant_prefix)

    def _get_client_context(self) -> ClientContext:
        """
        Creates a ClientContext for the specified SharePoint site URL.
        """
        client_context = ClientContext(self.site_url).with_access_token(
            token_func=self.get_token_response_object(tenant_prefix=self.root_site_prefix)
        )
        return client_context
