# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http import HttpRequest
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


class JiraRequestBuilder:
    """
    Builder for creating HTTP requests for Jira API endpoints.

    This builder helps create clean, reusable request definitions for tests
    instead of manually constructing HttpRequest objects each time.

    Example usage:
        request = (
            JiraRequestBuilder.application_roles_endpoint("domain.atlassian.net")
            .build()
        )
    """

    API_V3_BASE = "https://{domain}/rest/api/3"
    AGILE_V1_BASE = "https://{domain}/rest/agile/1.0"

    @classmethod
    def application_roles_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /applicationrole endpoint."""
        return cls(domain, "applicationrole", api_version="v3")

    @classmethod
    def avatars_endpoint(cls, domain: str, avatar_type: str) -> "JiraRequestBuilder":
        """Create a request builder for the /avatar/{type}/system endpoint."""
        return cls(domain, f"avatar/{avatar_type}/system", api_version="v3")

    @classmethod
    def boards_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /board endpoint (Agile API)."""
        return cls(domain, "board", api_version="agile")

    @classmethod
    def dashboards_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /dashboard endpoint."""
        return cls(domain, "dashboard", api_version="v3")

    @classmethod
    def filters_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /filter/search endpoint."""
        return cls(domain, "filter/search", api_version="v3")

    @classmethod
    def filter_sharing_endpoint(cls, domain: str, filter_id: str) -> "JiraRequestBuilder":
        """Create a request builder for the /filter/{id}/permission endpoint."""
        return cls(domain, f"filter/{filter_id}/permission", api_version="v3")

    @classmethod
    def groups_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /group/bulk endpoint."""
        return cls(domain, "group/bulk", api_version="v3")

    @classmethod
    def issue_fields_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /field endpoint."""
        return cls(domain, "field", api_version="v3")

    @classmethod
    def issue_field_configurations_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /fieldconfiguration endpoint."""
        return cls(domain, "fieldconfiguration", api_version="v3")

    @classmethod
    def issue_custom_field_contexts_endpoint(cls, domain: str, field_id: str) -> "JiraRequestBuilder":
        """Create a request builder for the /field/{fieldId}/context endpoint."""
        return cls(domain, f"field/{field_id}/context", api_version="v3")

    @classmethod
    def issue_custom_field_options_endpoint(cls, domain: str, field_id: str, context_id: str) -> "JiraRequestBuilder":
        """Create a request builder for the /field/{fieldId}/context/{contextId}/option endpoint."""
        return cls(domain, f"field/{field_id}/context/{context_id}/option", api_version="v3")

    @classmethod
    def issue_link_types_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issueLinkType endpoint."""
        return cls(domain, "issueLinkType", api_version="v3")

    @classmethod
    def issue_navigator_settings_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /settings/columns endpoint."""
        return cls(domain, "settings/columns", api_version="v3")

    @classmethod
    def issue_notification_schemes_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /notificationscheme endpoint."""
        return cls(domain, "notificationscheme", api_version="v3")

    @classmethod
    def issue_priorities_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /priority/search endpoint."""
        return cls(domain, "priority/search", api_version="v3")

    @classmethod
    def issue_resolutions_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /resolution/search endpoint."""
        return cls(domain, "resolution/search", api_version="v3")

    @classmethod
    def issue_security_schemes_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issuesecurityschemes endpoint."""
        return cls(domain, "issuesecurityschemes", api_version="v3")

    @classmethod
    def issue_types_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issuetype endpoint."""
        return cls(domain, "issuetype", api_version="v3")

    @classmethod
    def issue_type_schemes_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issuetypescheme endpoint."""
        return cls(domain, "issuetypescheme", api_version="v3")

    @classmethod
    def issue_type_screen_schemes_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issuetypescreenscheme endpoint."""
        return cls(domain, "issuetypescreenscheme", api_version="v3")

    @classmethod
    def issues_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /search/jql endpoint."""
        return cls(domain, "search/jql", api_version="v3")

    @classmethod
    def issue_changelogs_endpoint(cls, domain: str, issue_id_or_key: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issue/{issueIdOrKey}/changelog endpoint."""
        return cls(domain, f"issue/{issue_id_or_key}/changelog", api_version="v3")

    @classmethod
    def issue_comments_endpoint(cls, domain: str, issue_id_or_key: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issue/{issueIdOrKey}/comment endpoint."""
        return cls(domain, f"issue/{issue_id_or_key}/comment", api_version="v3")

    @classmethod
    def issue_properties_endpoint(cls, domain: str, issue_id_or_key: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issue/{issueIdOrKey}/properties endpoint."""
        return cls(domain, f"issue/{issue_id_or_key}/properties", api_version="v3")

    @classmethod
    def issue_property_endpoint(cls, domain: str, issue_id_or_key: str, property_key: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issue/{issueIdOrKey}/properties/{propertyKey} endpoint."""
        return cls(domain, f"issue/{issue_id_or_key}/properties/{property_key}", api_version="v3")

    @classmethod
    def issue_remote_links_endpoint(cls, domain: str, issue_id_or_key: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issue/{issueIdOrKey}/remotelink endpoint."""
        return cls(domain, f"issue/{issue_id_or_key}/remotelink", api_version="v3")

    @classmethod
    def issue_transitions_endpoint(cls, domain: str, issue_id_or_key: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issue/{issueIdOrKey}/transitions endpoint."""
        return cls(domain, f"issue/{issue_id_or_key}/transitions", api_version="v3")

    @classmethod
    def issue_votes_endpoint(cls, domain: str, issue_id_or_key: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issue/{issueIdOrKey}/votes endpoint."""
        return cls(domain, f"issue/{issue_id_or_key}/votes", api_version="v3")

    @classmethod
    def issue_watchers_endpoint(cls, domain: str, issue_id_or_key: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issue/{issueIdOrKey}/watchers endpoint."""
        return cls(domain, f"issue/{issue_id_or_key}/watchers", api_version="v3")

    @classmethod
    def issue_worklogs_endpoint(cls, domain: str, issue_id_or_key: str) -> "JiraRequestBuilder":
        """Create a request builder for the /issue/{issueIdOrKey}/worklog endpoint."""
        return cls(domain, f"issue/{issue_id_or_key}/worklog", api_version="v3")

    @classmethod
    def jira_settings_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /application-properties endpoint."""
        return cls(domain, "application-properties", api_version="v3")

    @classmethod
    def labels_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /label endpoint."""
        return cls(domain, "label", api_version="v3")

    @classmethod
    def permissions_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /permissions endpoint."""
        return cls(domain, "permissions", api_version="v3")

    @classmethod
    def permission_schemes_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /permissionscheme endpoint."""
        return cls(domain, "permissionscheme", api_version="v3")

    @classmethod
    def projects_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /project/search endpoint."""
        return cls(domain, "project/search", api_version="v3")

    @classmethod
    def project_avatars_endpoint(cls, domain: str, project_id_or_key: str) -> "JiraRequestBuilder":
        """Create a request builder for the /project/{projectIdOrKey}/avatars endpoint."""
        return cls(domain, f"project/{project_id_or_key}/avatars", api_version="v3")

    @classmethod
    def project_categories_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /projectCategory endpoint."""
        return cls(domain, "projectCategory", api_version="v3")

    @classmethod
    def project_components_endpoint(cls, domain: str, project_id_or_key: str) -> "JiraRequestBuilder":
        """Create a request builder for the /project/{projectIdOrKey}/component endpoint."""
        return cls(domain, f"project/{project_id_or_key}/component", api_version="v3")

    @classmethod
    def project_email_endpoint(cls, domain: str, project_id: str) -> "JiraRequestBuilder":
        """Create a request builder for the /project/{projectId}/email endpoint."""
        return cls(domain, f"project/{project_id}/email", api_version="v3")

    @classmethod
    def project_permission_schemes_endpoint(cls, domain: str, project_key_or_id: str) -> "JiraRequestBuilder":
        """Create a request builder for the /project/{projectKeyOrId}/securitylevel endpoint."""
        return cls(domain, f"project/{project_key_or_id}/securitylevel", api_version="v3")

    @classmethod
    def project_roles_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /role endpoint."""
        return cls(domain, "role", api_version="v3")

    @classmethod
    def project_types_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /project/type endpoint."""
        return cls(domain, "project/type", api_version="v3")

    @classmethod
    def project_versions_endpoint(cls, domain: str, project_id_or_key: str) -> "JiraRequestBuilder":
        """Create a request builder for the /project/{projectIdOrKey}/version endpoint."""
        return cls(domain, f"project/{project_id_or_key}/version", api_version="v3")

    @classmethod
    def screens_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /screens endpoint."""
        return cls(domain, "screens", api_version="v3")

    @classmethod
    def screen_tabs_endpoint(cls, domain: str, screen_id: str) -> "JiraRequestBuilder":
        """Create a request builder for the /screens/{screenId}/tabs endpoint."""
        return cls(domain, f"screens/{screen_id}/tabs", api_version="v3")

    @classmethod
    def screen_tab_fields_endpoint(cls, domain: str, screen_id: str, tab_id: str) -> "JiraRequestBuilder":
        """Create a request builder for the /screens/{screenId}/tabs/{tabId}/fields endpoint."""
        return cls(domain, f"screens/{screen_id}/tabs/{tab_id}/fields", api_version="v3")

    @classmethod
    def screen_schemes_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /screenscheme endpoint."""
        return cls(domain, "screenscheme", api_version="v3")

    @classmethod
    def sprints_endpoint(cls, domain: str, board_id: str) -> "JiraRequestBuilder":
        """Create a request builder for the /board/{boardId}/sprint endpoint (Agile API)."""
        return cls(domain, f"board/{board_id}/sprint", api_version="agile")

    @classmethod
    def sprint_issues_endpoint(cls, domain: str, sprint_id: str) -> "JiraRequestBuilder":
        """Create a request builder for the /sprint/{sprintId}/issue endpoint (Agile API)."""
        return cls(domain, f"sprint/{sprint_id}/issue", api_version="agile")

    @classmethod
    def board_issues_endpoint(cls, domain: str, board_id: str) -> "JiraRequestBuilder":
        """Create a request builder for the /board/{boardId}/issue endpoint (Agile API)."""
        return cls(domain, f"board/{board_id}/issue", api_version="agile")

    @classmethod
    def time_tracking_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /configuration/timetracking/list endpoint."""
        return cls(domain, "configuration/timetracking/list", api_version="v3")

    @classmethod
    def users_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /users/search endpoint."""
        return cls(domain, "users/search", api_version="v3")

    @classmethod
    def users_groups_detailed_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /user endpoint."""
        return cls(domain, "user", api_version="v3")

    @classmethod
    def workflows_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /workflow/search endpoint."""
        return cls(domain, "workflow/search", api_version="v3")

    @classmethod
    def workflow_schemes_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /workflowscheme endpoint."""
        return cls(domain, "workflowscheme", api_version="v3")

    @classmethod
    def workflow_statuses_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /status endpoint."""
        return cls(domain, "status", api_version="v3")

    @classmethod
    def workflow_status_categories_endpoint(cls, domain: str) -> "JiraRequestBuilder":
        """Create a request builder for the /statuscategory endpoint."""
        return cls(domain, "statuscategory", api_version="v3")

    def __init__(self, domain: str, resource: str, api_version: str = "v3"):
        """
        Initialize the request builder.

        Args:
            domain: The Jira domain (e.g., 'mycompany.atlassian.net')
            resource: The API resource path (e.g., 'applicationrole', 'project/search')
            api_version: The API version ('v3' for REST API v3, 'agile' for Agile API v1)
        """
        self._domain = domain
        self._resource = resource
        self._api_version = api_version
        self._query_params: dict = {}
        self._use_any_query_params = False

    def with_max_results(self, max_results: int) -> "JiraRequestBuilder":
        """Set the maxResults query parameter for pagination."""
        self._query_params["maxResults"] = str(max_results)
        return self

    def with_start_at(self, start_at: int) -> "JiraRequestBuilder":
        """Set the startAt query parameter for pagination."""
        self._query_params["startAt"] = str(start_at)
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
        """Set the fields query parameter."""
        self._query_params["fields"] = fields
        return self

    def with_query_param(self, key: str, value: str) -> "JiraRequestBuilder":
        """Add a custom query parameter."""
        self._query_params[key] = value
        return self

    def with_any_query_params(self) -> "JiraRequestBuilder":
        """Use ANY_QUERY_PARAMS matcher for dynamic/unpredictable parameters."""
        self._use_any_query_params = True
        return self

    def build(self) -> HttpRequest:
        """
        Build and return the HttpRequest object.

        Returns:
            HttpRequest configured with the URL and query params
        """
        if self._api_version == "agile":
            base_url = self.AGILE_V1_BASE.format(domain=self._domain)
        else:
            base_url = self.API_V3_BASE.format(domain=self._domain)

        url = f"{base_url}/{self._resource}"

        if self._use_any_query_params:
            return HttpRequest(url=url, query_params=ANY_QUERY_PARAMS)

        return HttpRequest(
            url=url,
            query_params=self._query_params if self._query_params else None,
        )
