# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import base64
from typing import Optional

from airbyte_cdk.test.mock_http import HttpRequest
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


class JiraRequestBuilder:
    """
    Builder for creating HTTP requests for Jira API endpoints.

    This builder helps create clean, reusable request definitions for tests
    instead of manually constructing HttpRequest objects each time.

    Example usage:
        request = (
            JiraRequestBuilder.projects_endpoint("domain.atlassian.net", "email@test.com", "api_token")
            .with_max_results(50)
            .build()
        )
    """

    BASE_URL_V3 = "https://{domain}/rest/api/3"
    BASE_URL_V1 = "https://{domain}/rest/agile/1.0"

    @classmethod
    def projects_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /project/search endpoint."""
        return cls("project/search", domain, email, api_token, api_version="v3")

    @classmethod
    def users_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /users/search endpoint."""
        return cls("users/search", domain, email, api_token, api_version="v3")

    @classmethod
    def boards_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /board endpoint (agile API v1)."""
        return cls("board", domain, email, api_token, api_version="v1")

    @classmethod
    def filters_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /filter/search endpoint."""
        return cls("filter/search", domain, email, api_token, api_version="v3")

    @classmethod
    def issues_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /search/jql endpoint."""
        return cls("search/jql", domain, email, api_token, api_version="v3")

    @classmethod
    def application_roles_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /applicationrole endpoint."""
        return cls("applicationrole", domain, email, api_token, api_version="v3")

    @classmethod
    def dashboards_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /dashboard endpoint."""
        return cls("dashboard", domain, email, api_token, api_version="v3")

    @classmethod
    def groups_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /group/bulk endpoint."""
        return cls("group/bulk", domain, email, api_token, api_version="v3")

    @classmethod
    def issue_fields_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /field endpoint."""
        return cls("field", domain, email, api_token, api_version="v3")

    @classmethod
    def issue_field_configurations_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /fieldconfiguration endpoint."""
        return cls("fieldconfiguration", domain, email, api_token, api_version="v3")

    @classmethod
    def issue_link_types_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issueLinkType endpoint."""
        return cls("issueLinkType", domain, email, api_token, api_version="v3")

    @classmethod
    def issue_navigator_settings_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /settings/columns endpoint."""
        return cls("settings/columns", domain, email, api_token, api_version="v3")

    @classmethod
    def issue_notification_schemes_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /notificationscheme endpoint."""
        return cls("notificationscheme", domain, email, api_token, api_version="v3")

    @classmethod
    def issue_priorities_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /priority/search endpoint."""
        return cls("priority/search", domain, email, api_token, api_version="v3")

    @classmethod
    def issue_resolutions_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /resolution/search endpoint."""
        return cls("resolution/search", domain, email, api_token, api_version="v3")

    @classmethod
    def issue_security_schemes_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issuesecurityschemes endpoint."""
        return cls("issuesecurityschemes", domain, email, api_token, api_version="v3")

    @classmethod
    def issue_types_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issuetype endpoint."""
        return cls("issuetype", domain, email, api_token, api_version="v3")

    @classmethod
    def issue_type_schemes_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issuetypescheme endpoint."""
        return cls("issuetypescheme", domain, email, api_token, api_version="v3")

    @classmethod
    def issue_type_screen_schemes_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issuetypescreenscheme endpoint."""
        return cls("issuetypescreenscheme", domain, email, api_token, api_version="v3")

    @classmethod
    def jira_settings_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /application-properties endpoint."""
        return cls("application-properties", domain, email, api_token, api_version="v3")

    @classmethod
    def labels_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /label endpoint."""
        return cls("label", domain, email, api_token, api_version="v3")

    @classmethod
    def permissions_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /permissions endpoint."""
        return cls("permissions", domain, email, api_token, api_version="v3")

    @classmethod
    def permission_schemes_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /permissionscheme endpoint."""
        return cls("permissionscheme", domain, email, api_token, api_version="v3")

    @classmethod
    def project_categories_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /projectCategory endpoint."""
        return cls("projectCategory", domain, email, api_token, api_version="v3")

    @classmethod
    def project_roles_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /role endpoint."""
        return cls("role", domain, email, api_token, api_version="v3")

    @classmethod
    def project_types_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /project/type endpoint."""
        return cls("project/type", domain, email, api_token, api_version="v3")

    @classmethod
    def screens_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /screens endpoint."""
        return cls("screens", domain, email, api_token, api_version="v3")

    @classmethod
    def screen_schemes_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /screenscheme endpoint."""
        return cls("screenscheme", domain, email, api_token, api_version="v3")

    @classmethod
    def time_tracking_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /configuration/timetracking/list endpoint."""
        return cls("configuration/timetracking/list", domain, email, api_token, api_version="v3")

    @classmethod
    def workflows_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /workflow/search endpoint."""
        return cls("workflow/search", domain, email, api_token, api_version="v3")

    @classmethod
    def workflow_schemes_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /workflowscheme endpoint."""
        return cls("workflowscheme", domain, email, api_token, api_version="v3")

    @classmethod
    def workflow_statuses_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /status endpoint."""
        return cls("status", domain, email, api_token, api_version="v3")

    @classmethod
    def workflow_status_categories_endpoint(cls, domain: str, email: str, api_token: str) -> "JiraRequestBuilder":
        """Create a request builder for the /statuscategory endpoint."""
        return cls("statuscategory", domain, email, api_token, api_version="v3")

    @classmethod
    def avatars_endpoint(cls, domain: str, email: str, api_token: str, avatar_type: str) -> "JiraRequestBuilder":
        """Create a request builder for the /avatar/{type}/system endpoint."""
        return cls(f"avatar/{avatar_type}/system", domain, email, api_token, api_version="v3")

    @classmethod
    def sprints_endpoint(cls, domain: str, email: str, api_token: str, board_id: int) -> "JiraRequestBuilder":
        """Create a request builder for the /board/{boardId}/sprint endpoint (agile API v1)."""
        return cls(f"board/{board_id}/sprint", domain, email, api_token, api_version="v1")

    @classmethod
    def board_issues_endpoint(cls, domain: str, email: str, api_token: str, board_id: int) -> "JiraRequestBuilder":
        """Create a request builder for the /board/{boardId}/issue endpoint (agile API v1)."""
        return cls(f"board/{board_id}/issue", domain, email, api_token, api_version="v1")

    @classmethod
    def sprint_issues_endpoint(cls, domain: str, email: str, api_token: str, sprint_id: int) -> "JiraRequestBuilder":
        """Create a request builder for the /sprint/{sprintId}/issue endpoint (agile API v1)."""
        return cls(f"sprint/{sprint_id}/issue", domain, email, api_token, api_version="v1")

    @classmethod
    def filter_sharing_endpoint(cls, domain: str, email: str, api_token: str, filter_id: int) -> "JiraRequestBuilder":
        """Create a request builder for the /filter/{id}/permission endpoint."""
        return cls(f"filter/{filter_id}/permission", domain, email, api_token, api_version="v3")

    @classmethod
    def issue_comments_endpoint(cls, domain: str, email: str, api_token: str, issue_id_or_key: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issue/{issueIdOrKey}/comment endpoint."""
        return cls(f"issue/{issue_id_or_key}/comment", domain, email, api_token, api_version="v3")

    @classmethod
    def issue_worklogs_endpoint(cls, domain: str, email: str, api_token: str, issue_id_or_key: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issue/{issueIdOrKey}/worklog endpoint."""
        return cls(f"issue/{issue_id_or_key}/worklog", domain, email, api_token, api_version="v3")

    @classmethod
    def issue_watchers_endpoint(cls, domain: str, email: str, api_token: str, issue_id_or_key: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issue/{issueIdOrKey}/watchers endpoint."""
        return cls(f"issue/{issue_id_or_key}/watchers", domain, email, api_token, api_version="v3")

    @classmethod
    def issue_votes_endpoint(cls, domain: str, email: str, api_token: str, issue_id_or_key: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issue/{issueIdOrKey}/votes endpoint."""
        return cls(f"issue/{issue_id_or_key}/votes", domain, email, api_token, api_version="v3")

    @classmethod
    def issue_remote_links_endpoint(cls, domain: str, email: str, api_token: str, issue_id_or_key: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issue/{issueIdOrKey}/remotelink endpoint."""
        return cls(f"issue/{issue_id_or_key}/remotelink", domain, email, api_token, api_version="v3")

    @classmethod
    def issue_transitions_endpoint(cls, domain: str, email: str, api_token: str, issue_id_or_key: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issue/{issueIdOrKey}/transitions endpoint."""
        return cls(f"issue/{issue_id_or_key}/transitions", domain, email, api_token, api_version="v3")

    @classmethod
    def issue_properties_endpoint(cls, domain: str, email: str, api_token: str, issue_id_or_key: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issue/{issueIdOrKey}/properties endpoint."""
        return cls(f"issue/{issue_id_or_key}/properties", domain, email, api_token, api_version="v3")

    @classmethod
    def issue_changelogs_endpoint(cls, domain: str, email: str, api_token: str, issue_id_or_key: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issue/{issueIdOrKey}/changelog endpoint."""
        return cls(f"issue/{issue_id_or_key}/changelog", domain, email, api_token, api_version="v3")

    @classmethod
    def project_components_endpoint(cls, domain: str, email: str, api_token: str, project_id_or_key: str) -> "JiraRequestBuilder":
        """Create a request builder for the /project/{projectIdOrKey}/component endpoint."""
        return cls(f"project/{project_id_or_key}/component", domain, email, api_token, api_version="v3")

    @classmethod
    def project_email_endpoint(cls, domain: str, email: str, api_token: str, project_id: str) -> "JiraRequestBuilder":
        """Create a request builder for the /project/{projectId}/email endpoint."""
        return cls(f"project/{project_id}/email", domain, email, api_token, api_version="v3")

    @classmethod
    def project_permission_schemes_endpoint(cls, domain: str, email: str, api_token: str, project_id_or_key: str) -> "JiraRequestBuilder":
        """Create a request builder for the /project/{projectKeyOrId}/securitylevel endpoint."""
        return cls(f"project/{project_id_or_key}/securitylevel", domain, email, api_token, api_version="v3")

    @classmethod
    def project_versions_endpoint(cls, domain: str, email: str, api_token: str, project_id_or_key: str) -> "JiraRequestBuilder":
        """Create a request builder for the /project/{projectIdOrKey}/version endpoint."""
        return cls(f"project/{project_id_or_key}/version", domain, email, api_token, api_version="v3")

    @classmethod
    def project_avatars_endpoint(cls, domain: str, email: str, api_token: str, project_id_or_key: str) -> "JiraRequestBuilder":
        """Create a request builder for the /project/{projectIdOrKey}/avatars endpoint."""
        return cls(f"project/{project_id_or_key}/avatars", domain, email, api_token, api_version="v3")

    @classmethod
    def screen_tabs_endpoint(cls, domain: str, email: str, api_token: str, screen_id: int) -> "JiraRequestBuilder":
        """Create a request builder for the /screens/{screenId}/tabs endpoint."""
        return cls(f"screens/{screen_id}/tabs", domain, email, api_token, api_version="v3")

    @classmethod
    def screen_tab_fields_endpoint(cls, domain: str, email: str, api_token: str, screen_id: int, tab_id: int) -> "JiraRequestBuilder":
        """Create a request builder for the /screens/{screenId}/tabs/{tabId}/fields endpoint."""
        return cls(f"screens/{screen_id}/tabs/{tab_id}/fields", domain, email, api_token, api_version="v3")

    @classmethod
    def issue_custom_field_contexts_endpoint(cls, domain: str, email: str, api_token: str, field_id: str) -> "JiraRequestBuilder":
        """Create a request builder for the /field/{fieldId}/context endpoint."""
        return cls(f"field/{field_id}/context", domain, email, api_token, api_version="v3")

    @classmethod
    def issue_custom_field_options_endpoint(
        cls, domain: str, email: str, api_token: str, field_id: str, context_id: int
    ) -> "JiraRequestBuilder":
        """Create a request builder for the /field/{fieldId}/context/{contextId}/option endpoint."""
        return cls(f"field/{field_id}/context/{context_id}/option", domain, email, api_token, api_version="v3")

    @classmethod
    def users_groups_detailed_endpoint(cls, domain: str, email: str, api_token: str, account_id: str) -> "JiraRequestBuilder":
        """Create a request builder for the /user/groups endpoint."""
        builder = cls("user/groups", domain, email, api_token, api_version="v3")
        builder._query_params["accountId"] = account_id
        return builder

    def __init__(self, resource: str, domain: str, email: str, api_token: str, api_version: str = "v3"):
        """
        Initialize the request builder.

        Args:
            resource: The API resource path (e.g., 'project/search', 'board')
            domain: The Jira domain (e.g., 'domain.atlassian.net')
            email: The email for authentication
            api_token: The API token for authentication
            api_version: API version ('v3' for REST API, 'v1' for Agile API)
        """
        self._resource = resource
        self._domain = domain
        self._email = email
        self._api_token = api_token
        self._api_version = api_version
        self._max_results: Optional[int] = None
        self._start_at: Optional[int] = None
        self._query_params: dict = {}
        self._any_query_params = False

    def with_max_results(self, max_results: int) -> "JiraRequestBuilder":
        """Set the maxResults query parameter for pagination."""
        self._max_results = max_results
        return self

    def with_start_at(self, start_at: int) -> "JiraRequestBuilder":
        """Set the startAt query parameter for pagination."""
        self._start_at = start_at
        return self

    def with_query_param(self, key: str, value: str) -> "JiraRequestBuilder":
        """Add a custom query parameter."""
        self._query_params[key] = value
        return self

    def with_any_query_params(self) -> "JiraRequestBuilder":
        """Allow any query parameters (useful for dynamic/unpredictable params)."""
        self._any_query_params = True
        return self

    def with_expand(self, expand: str) -> "JiraRequestBuilder":
        """Set the expand query parameter."""
        self._query_params["expand"] = expand
        return self

    def with_jql(self, jql: str) -> "JiraRequestBuilder":
        """Set the jql query parameter for issue searches."""
        self._query_params["jql"] = jql
        return self

    def with_fields(self, fields: str) -> "JiraRequestBuilder":
        """Set the fields query parameter for issue searches."""
        self._query_params["fields"] = fields
        return self

    def _get_base_url(self) -> str:
        """Get the base URL based on API version."""
        if self._api_version == "v1":
            return self.BASE_URL_V1.format(domain=self._domain)
        return self.BASE_URL_V3.format(domain=self._domain)

    def _get_auth_header(self) -> str:
        """Generate the Basic auth header value."""
        credentials = f"{self._email}:{self._api_token}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    def build(self) -> HttpRequest:
        """
        Build and return the HttpRequest object.

        Returns:
            HttpRequest configured with the URL, query params, and headers
        """
        if self._any_query_params:
            return HttpRequest(
                url=f"{self._get_base_url()}/{self._resource}",
                query_params=ANY_QUERY_PARAMS,
                headers={"Authorization": self._get_auth_header()},
            )

        query_params = dict(self._query_params)

        if self._max_results is not None:
            query_params["maxResults"] = str(self._max_results)
        if self._start_at is not None:
            query_params["startAt"] = str(self._start_at)

        return HttpRequest(
            url=f"{self._get_base_url()}/{self._resource}",
            query_params=query_params if query_params else None,
            headers={"Authorization": self._get_auth_header()},
        )
