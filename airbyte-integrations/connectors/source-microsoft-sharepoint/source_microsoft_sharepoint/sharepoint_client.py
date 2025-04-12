#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


from msal import ConfidentialClientApplication
from office365.graph_client import GraphClient
from office365.runtime.auth.token_response import TokenResponse

from airbyte_cdk import AirbyteTracedException, FailureType
from source_microsoft_sharepoint.spec import SourceMicrosoftSharePointSpec


class SourceMicrosoftSharePointClient:
    """
    Client to interact with Microsoft SharePoint.
    """

    def __init__(self, config: SourceMicrosoftSharePointSpec):
        self.config = config
        self._client = None
        self._msal_app = ConfidentialClientApplication(
            self.config.credentials.client_id,
            authority=f"https://login.microsoftonline.com/{self.config.credentials.tenant_id}",
            client_credential=self.config.credentials.client_secret,
        )

    @property
    def client(self):
        """Initializes and returns a GraphClient instance."""
        if not self.config:
            raise ValueError("Configuration is missing; cannot create the Office365 graph client.")
        if not self._client:
            self._client = GraphClient(self._get_access_token)
        return self._client

    @staticmethod
    def _get_scope(tenant_prefix: str = None):
        """
        Returns the scope for the access token.
        We use admin site to retrieve objects like Sites.
        """
        if tenant_prefix:
            admin_site_url = f"https://{tenant_prefix}-admin.sharepoint.com"
            return [f"{admin_site_url}/.default"]
        return ["https://graph.microsoft.com/.default"]

    def _get_access_token(self, tenant_prefix: str = None):
        """Retrieves an access token for SharePoint access."""
        scope = self._get_scope(tenant_prefix)
        refresh_token = self.config.credentials.refresh_token if hasattr(self.config.credentials, "refresh_token") else None

        if refresh_token:
            result = self._msal_app.acquire_token_by_refresh_token(refresh_token, scopes=scope)
        else:
            result = self._msal_app.acquire_token_for_client(scopes=scope)

        if "access_token" not in result:
            error_description = result.get("error_description", "No error description provided.")
            message = f"Failed to acquire access token. Error: {result.get('error')}. Error description: {error_description}."
            raise AirbyteTracedException(message=message, failure_type=FailureType.config_error)

        return result

    @property
    def access_token(self):
        """
        Provides an access token/credentials for the client.
        """
        return self._get_access_token()["access_token"]

    def get_token_response_object_wrapper(self, tenant_prefix: str):
        def get_token_response_object():
            token = self._get_access_token(tenant_prefix=tenant_prefix)
            return TokenResponse.from_json(token)

        return get_token_response_object
