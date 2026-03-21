# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Optional

from airbyte_cdk.test.mock_http import HttpRequest


class ZendeskChatRequestBuilder:
    """
    Builder for creating HTTP requests for Zendesk Chat API endpoints.
    """

    @classmethod
    def accounts_endpoint(cls, subdomain: str, access_token: str) -> "ZendeskChatRequestBuilder":
        return cls("account", subdomain, access_token)

    @classmethod
    def agents_endpoint(cls, subdomain: str, access_token: str) -> "ZendeskChatRequestBuilder":
        return cls("agents", subdomain, access_token)

    @classmethod
    def agent_timeline_endpoint(cls, subdomain: str, access_token: str) -> "ZendeskChatRequestBuilder":
        return cls("incremental/agent_timeline", subdomain, access_token)

    @classmethod
    def bans_endpoint(cls, subdomain: str, access_token: str) -> "ZendeskChatRequestBuilder":
        return cls("bans", subdomain, access_token)

    @classmethod
    def chats_endpoint(cls, subdomain: str, access_token: str) -> "ZendeskChatRequestBuilder":
        return cls("incremental/chats", subdomain, access_token)

    @classmethod
    def departments_endpoint(cls, subdomain: str, access_token: str) -> "ZendeskChatRequestBuilder":
        return cls("departments", subdomain, access_token)

    @classmethod
    def goals_endpoint(cls, subdomain: str, access_token: str) -> "ZendeskChatRequestBuilder":
        return cls("goals", subdomain, access_token)

    @classmethod
    def roles_endpoint(cls, subdomain: str, access_token: str) -> "ZendeskChatRequestBuilder":
        return cls("roles", subdomain, access_token)

    @classmethod
    def routing_settings_endpoint(cls, subdomain: str, access_token: str) -> "ZendeskChatRequestBuilder":
        return cls("routing_settings/account", subdomain, access_token)

    @classmethod
    def shortcuts_endpoint(cls, subdomain: str, access_token: str) -> "ZendeskChatRequestBuilder":
        return cls("shortcuts", subdomain, access_token)

    @classmethod
    def skills_endpoint(cls, subdomain: str, access_token: str) -> "ZendeskChatRequestBuilder":
        return cls("skills", subdomain, access_token)

    @classmethod
    def triggers_endpoint(cls, subdomain: str, access_token: str) -> "ZendeskChatRequestBuilder":
        return cls("triggers", subdomain, access_token)

    def __init__(self, resource: str, subdomain: str, access_token: str):
        self._resource = resource
        self._subdomain = subdomain
        self._access_token = access_token
        self._query_params: dict = {}

    def with_query_param(self, key: str, value: str) -> "ZendeskChatRequestBuilder":
        self._query_params[key] = value
        return self

    def with_limit(self, limit: int) -> "ZendeskChatRequestBuilder":
        self._query_params["limit"] = str(limit)
        return self

    def with_since_id(self, since_id: int) -> "ZendeskChatRequestBuilder":
        self._query_params["since_id"] = str(since_id)
        return self

    def with_start_time(self, start_time: int) -> "ZendeskChatRequestBuilder":
        self._query_params["start_time"] = str(start_time)
        return self

    def with_fields(self, fields: str) -> "ZendeskChatRequestBuilder":
        self._query_params["fields"] = fields
        return self

    def build(self) -> HttpRequest:
        url = f"https://{self._subdomain}.zendesk.com/api/v2/chat/{self._resource}"
        return HttpRequest(
            url=url,
            query_params=self._query_params if self._query_params else None,
            headers={"Authorization": f"Bearer {self._access_token}"},
        )
