# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http import HttpRequest
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


class SentryRequestBuilder:
    """Builder for creating Sentry API requests"""

    def __init__(self, resource: str, organization: str, project: str, auth_token: str):
        self._resource = resource
        self._organization = organization
        self._project = project
        self._auth_token = auth_token
        self._hostname = "sentry.io"
        self._query_params = ANY_QUERY_PARAMS

    @classmethod
    def events_endpoint(cls, organization: str, project: str, auth_token: str):
        return cls("events", organization, project, auth_token)

    @classmethod
    def issues_endpoint(cls, organization: str, project: str, auth_token: str):
        return cls("issues", organization, project, auth_token)

    @classmethod
    def projects_endpoint(cls, organization: str, auth_token: str):
        return cls("projects", organization, "", auth_token)

    @classmethod
    def project_detail_endpoint(cls, organization: str, project: str, auth_token: str):
        return cls("project_detail", organization, project, auth_token)

    @classmethod
    def releases_endpoint(cls, organization: str, project: str, auth_token: str):
        return cls("releases", organization, project, auth_token)

    def with_query_params(self, query_params: dict):
        """Set specific query parameters for the request"""
        self._query_params = query_params
        return self

    def build(self) -> HttpRequest:
        # Build URL based on resource type
        if self._resource == "projects":
            # Projects endpoint: /api/0/projects/
            url = f"https://{self._hostname}/api/0/projects/"
        elif self._resource == "releases":
            # Releases endpoint: /api/0/organizations/{org}/releases/
            url = f"https://{self._hostname}/api/0/organizations/{self._organization}/releases/"
        elif self._resource == "project_detail":
            # Project detail endpoint: /api/0/projects/{org}/{project}/
            url = f"https://{self._hostname}/api/0/projects/{self._organization}/{self._project}/"
        else:
            # Events and issues endpoints: /api/0/projects/{org}/{project}/{resource}/
            url = f"https://{self._hostname}/api/0/projects/{self._organization}/{self._project}/{self._resource}/"

        return HttpRequest(url=url, query_params=self._query_params, headers={"Authorization": f"Bearer {self._auth_token}"})
