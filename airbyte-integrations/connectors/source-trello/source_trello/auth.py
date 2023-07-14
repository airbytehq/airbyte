#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_token import AbstractHeaderAuthenticator


class TrelloAuthenticator(AbstractHeaderAuthenticator):
    """
    https://developer.atlassian.com/cloud/trello/guides/rest-api/authorization/#passing-token-and-key-in-api-requests
    """

    def __init__(self, apiKey: str, apiToken: str):
        self.apiKey = apiKey
        self.apiToken = apiToken

    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> str:
        return f'OAuth oauth_consumer_key="{self.apiKey}", oauth_token="{self.apiToken}"'
