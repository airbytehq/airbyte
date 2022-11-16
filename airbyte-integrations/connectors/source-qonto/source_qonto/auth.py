#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_token import AbstractHeaderAuthenticator


class QontoApiKeyAuthenticator(AbstractHeaderAuthenticator):
    """
    QontoApiKeyAuthenticator sets a request header on the HTTP requests sent.

    The header is of the form:
    `"Authorization": "<api-key>"`

    For example,
    `QontoApiKeyAuthenticator("my-organization", "3564f")`
    will result in the following header set on the HTTP request
    `"Authorization": "my-organization:3564f"`

    Attributes:
        organization_slug (str): Organization slug to use in the header
        secret_key (str): Secret key to use in the header
    """

    def __init__(self, organization_slug: str, secret_key: str):
        super().__init__()
        self.organization_slug = organization_slug
        self.secret_key = secret_key

    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> str:
        return f"{self.organization_slug}:{self.secret_key}"
