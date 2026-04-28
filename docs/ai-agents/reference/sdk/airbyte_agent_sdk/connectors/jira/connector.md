---
id: airbyte_agent_sdk-connectors-jira-connector
title: airbyte_agent_sdk.connectors.jira.connector
---

Module airbyte_agent_sdk.connectors.jira.connector
==================================================
Jira connector.

Classes
-------

<a id="IssueCommentsQuery"></a>

`IssueCommentsQuery(connector: JiraConnector)`
:   Query class for IssueComments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: IssueCommentsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.jira.models.AirbyteSearchResult[IssueCommentsSearchData]`
    :   Search issue_comments records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (IssueCommentsSearchFilter):
        - author: The ID of the user who created the comment
        - body: The comment text in Atlassian Document Format
        - created: The date and time at which the comment was created
        - id: The ID of the comment
        - issue_id: Id of the related issue
        - jsd_public: Whether the comment is visible in Jira Service Desk
        - properties: A list of comment properties
        - rendered_body: The rendered version of the comment
        - self: The URL of the comment
        - update_author: The ID of the user who updated the comment last
        - updated: The date and time at which the comment was updated last
        - visibility: The group or role to which this item is visible
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            IssueCommentsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, body: IssueCommentsCreateParamsBody, issue_id_or_key: str, visibility: IssueCommentsCreateParamsVisibility | None = None, properties: list[dict[str, Any]] | None = None, expand: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.jira.models.IssueComment`
    :   Adds a comment to an issue
        
        Args:
            body: Comment content in Atlassian Document Format (ADF)
            visibility: Restrict comment visibility to a group or role
            properties: Custom properties for the comment
            issue_id_or_key: The issue ID or key (e.g., "PROJ-123" or "10000")
            expand: Expand options for the returned comment
            **kwargs: Additional parameters
        
        Returns:
            IssueComment

    `delete(self, issue_id_or_key: str, comment_id: str, **kwargs) ‑> dict[str, typing.Any]`
    :   Deletes a comment from an issue
        
        Args:
            issue_id_or_key: The issue ID or key (e.g., "PROJ-123" or "10000")
            comment_id: The comment ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `get(self, issue_id_or_key: str, comment_id: str, expand: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.jira.models.IssueComment`
    :   Retrieve a single comment by its ID
        
        Args:
            issue_id_or_key: The issue ID or key (e.g., "PROJ-123" or "10000")
            comment_id: The comment ID
            expand: Comma-separated list of additional fields to include (renderedBody, properties)
            **kwargs: Additional parameters
        
        Returns:
            IssueComment

    `list(self, issue_id_or_key: str, start_at: int | None = None, max_results: int | None = None, order_by: str | None = None, expand: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.jira.models.JiraExecuteResultWithMeta[list[IssueComment], IssueCommentsListResultMeta]`
    :   Retrieve all comments for a specific issue
        
        Args:
            issue_id_or_key: The issue ID or key (e.g., "PROJ-123" or "10000")
            start_at: The index of the first item to return in a page of results (page offset)
            max_results: The maximum number of items to return per page
            order_by: Order the results by created date (+ for ascending, - for descending)
            expand: Comma-separated list of additional fields to include (renderedBody, properties)
            **kwargs: Additional parameters
        
        Returns:
            IssueCommentsListResult

    `update(self, body: IssueCommentsUpdateParamsBody, issue_id_or_key: str, comment_id: str, visibility: IssueCommentsUpdateParamsVisibility | None = None, notify_users: bool | None = None, expand: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.jira.models.IssueComment`
    :   Updates a comment on an issue
        
        Args:
            body: Updated comment content in Atlassian Document Format (ADF)
            visibility: Restrict comment visibility to a group or role
            issue_id_or_key: The issue ID or key (e.g., "PROJ-123" or "10000")
            comment_id: The comment ID
            notify_users: Whether a notification email about the comment update is sent. Default is true.
            expand: Expand options for the returned comment
            **kwargs: Additional parameters
        
        Returns:
            IssueComment

<a id="IssueFieldsQuery"></a>

`IssueFieldsQuery(connector: JiraConnector)`
:   Query class for IssueFields entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, start_at: int | None = None, max_results: int | None = None, type: list[str] | None = None, id: list[str] | None = None, query: str | None = None, order_by: str | None = None, expand: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.jira.models.JiraExecuteResult[IssueFieldSearchResults]`
    :   Search and filter issue fields with query parameters
        
        Args:
            start_at: The index of the first item to return in a page of results (page offset)
            max_results: The maximum number of items to return per page (max 100)
            type: The type of fields to search for (custom, system, or both)
            id: List of field IDs to search for
            query: String to match against field names, descriptions, and field IDs (case insensitive)
            order_by: Order the results by a field (contextsCount, lastUsed, name, screensCount)
            expand: Comma-separated list of additional fields to include (searcherKey, screensCount, contextsCount, isLocked, lastUsed)
            **kwargs: Additional parameters
        
        Returns:
            IssueFieldsApiSearchResult

    `context_store_search(self, query: IssueFieldsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.jira.models.AirbyteSearchResult[IssueFieldsSearchData]`
    :   Search issue_fields records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (IssueFieldsSearchFilter):
        - clause_names: The names that can be used to reference the field in an advanced search
        - custom: Whether the field is a custom field
        - id: The ID of the field
        - key: The key of the field
        - name: The name of the field
        - navigable: Whether the field can be used as a column on the issue navigator
        - orderable: Whether the content of the field can be used to order lists
        - schema_: The data schema for the field
        - scope: The scope of the field
        - searchable: Whether the content of the field can be searched
        - untranslated_name: The untranslated name of the field
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            IssueFieldsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.jira.models.JiraExecuteResult[list[IssueField]]`
    :   Returns a list of all custom and system fields
        
        Returns:
            IssueFieldsListResult

<a id="IssueWorklogsQuery"></a>

`IssueWorklogsQuery(connector: JiraConnector)`
:   Query class for IssueWorklogs entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: IssueWorklogsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.jira.models.AirbyteSearchResult[IssueWorklogsSearchData]`
    :   Search issue_worklogs records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (IssueWorklogsSearchFilter):
        - author: Details of the user who created the worklog
        - comment: A comment about the worklog in Atlassian Document Format
        - created: The datetime on which the worklog was created
        - id: The ID of the worklog record
        - issue_id: The ID of the issue this worklog is for
        - properties: Details of properties for the worklog
        - self: The URL of the worklog item
        - started: The datetime on which the worklog effort was started
        - time_spent: The time spent working on the issue as days, hours, or minutes
        - time_spent_seconds: The time in seconds spent working on the issue
        - update_author: Details of the user who last updated the worklog
        - updated: The datetime on which the worklog was last updated
        - visibility: Details about any restrictions in the visibility of the worklog
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            IssueWorklogsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, issue_id_or_key: str, worklog_id: str, expand: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.jira.models.Worklog`
    :   Retrieve a single worklog by its ID
        
        Args:
            issue_id_or_key: The issue ID or key (e.g., "PROJ-123" or "10000")
            worklog_id: The worklog ID
            expand: Comma-separated list of additional fields to include (properties)
            **kwargs: Additional parameters
        
        Returns:
            Worklog

    `list(self, issue_id_or_key: str, start_at: int | None = None, max_results: int | None = None, expand: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.jira.models.JiraExecuteResultWithMeta[list[Worklog], IssueWorklogsListResultMeta]`
    :   Retrieve all worklogs for a specific issue
        
        Args:
            issue_id_or_key: The issue ID or key (e.g., "PROJ-123" or "10000")
            start_at: The index of the first item to return in a page of results (page offset)
            max_results: The maximum number of items to return per page
            expand: Comma-separated list of additional fields to include (properties)
            **kwargs: Additional parameters
        
        Returns:
            IssueWorklogsListResult

<a id="IssuesAssigneeQuery"></a>

`IssuesAssigneeQuery(connector: JiraConnector)`
:   Query class for IssuesAssignee entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `update(self, issue_id_or_key: str, account_id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Assigns an issue to a user. Use accountId to specify the assignee. Use null to unassign the issue. Use "-1" to set to automatic (project default).
        
        Args:
            account_id: The account ID of the user to assign the issue to. Use null to unassign the issue. Use "-1" to set to automatic (project default assignee).
            issue_id_or_key: The issue ID or key (e.g., "PROJ-123" or "10000")
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

<a id="IssuesQuery"></a>

`IssuesQuery(connector: JiraConnector)`
:   Query class for Issues entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, jql: str | None = None, next_page_token: str | None = None, max_results: int | None = None, fields: str | None = None, expand: str | None = None, properties: str | None = None, fields_by_keys: bool | None = None, fail_fast: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.jira.models.JiraExecuteResultWithMeta[list[Issue], IssuesApiSearchResultMeta]`
    :   Retrieve issues based on JQL query with pagination support.
        
        IMPORTANT: This endpoint requires a bounded JQL query. A bounded query must include a search restriction that limits the scope of the search. Examples of valid restrictions include: project (e.g., "project = MYPROJECT"), assignee (e.g., "assignee = currentUser()"), reporter, issue key, sprint, or date-based filters combined with a project restriction. An unbounded query like "order by key desc" will be rejected with a 400 error. Example bounded query: "project = MYPROJECT AND updated >= -7d ORDER BY created DESC".
        
        
                Args:
                    jql: JQL query string to filter issues
                    next_page_token: The token for a page to fetch that is not the first page. The first page has a nextPageToken of null. Use the `nextPageToken` to fetch the next page of issues. The `nextPageToken` field is not included in the response for the last page, indicating there is no next page.
                    max_results: The maximum number of items to return per page. To manage page size, API may return fewer items per page where a large number of fields or properties are requested. The greatest number of items returned per page is achieved when requesting `id` or `key` only. It returns max 5000 issues.
                    fields: A comma-separated list of fields to return for each issue. By default, all navigable fields are returned. To get a list of all fields, use the Get fields operation.
                    expand: A comma-separated list of parameters to expand. This parameter accepts multiple values, including `renderedFields`, `names`, `schema`, `transitions`, `operations`, `editmeta`, `changelog`, and `versionedRepresentations`.
                    properties: A comma-separated list of issue property keys. To get a list of all issue property keys, use the Get issue operation. A maximum of 5 properties can be requested.
                    fields_by_keys: Whether the fields parameter contains field keys (true) or field IDs (false). Default is false.
                    fail_fast: Fail the request early if all field data cannot be retrieved. Default is false.
                    **kwargs: Additional parameters
        
                Returns:
                    IssuesApiSearchResult

    `context_store_search(self, query: IssuesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.jira.models.AirbyteSearchResult[IssuesSearchData]`
    :   Search issues records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (IssuesSearchFilter):
        - changelog: Details of changelogs associated with the issue
        - created: The timestamp when the issue was created
        - editmeta: The metadata for the fields on the issue that can be amended
        - expand: Expand options that include additional issue details in the response
        - fields: Details of various fields associated with the issue
        - fields_to_include: Specify the fields to include in the fetched issues data
        - id: The unique ID of the issue
        - key: The unique key of the issue
        - names: The ID and name of each field present on the issue
        - operations: The operations that can be performed on the issue
        - project_id: The ID of the project containing the issue
        - project_key: The key of the project containing the issue
        - properties: Details of the issue properties identified in the request
        - rendered_fields: The rendered value of each field present on the issue
        - schema_: The schema describing each field present on the issue
        - self: The URL of the issue details
        - transitions: The transitions that can be performed on the issue
        - updated: The timestamp when the issue was last updated
        - versioned_representations: The versions of each field on the issue
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            IssuesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, fields: IssuesCreateParamsFields, update: dict[str, Any] | None = None, update_history: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.jira.models.IssueCreateResponse`
    :   Creates an issue or a sub-task from a JSON representation
        
        Args:
            fields: The issue fields to set
            update: Additional update operations to perform
            update_history: Whether the action taken is added to the user's Recent history
            **kwargs: Additional parameters
        
        Returns:
            IssueCreateResponse

    `delete(self, issue_id_or_key: str, delete_subtasks: bool | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Deletes an issue. An issue cannot be deleted if it has one or more subtasks unless deleteSubtasks is true.
        
        Args:
            issue_id_or_key: The issue ID or key (e.g., "PROJ-123" or "10000")
            delete_subtasks: Whether to delete the issue's subtasks. Default is false.
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `get(self, issue_id_or_key: str, fields: str | None = None, expand: str | None = None, properties: str | None = None, fields_by_keys: bool | None = None, update_history: bool | None = None, fail_fast: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.jira.models.Issue`
    :   Retrieve a single issue by its ID or key
        
        Args:
            issue_id_or_key: The issue ID or key (e.g., "PROJ-123" or "10000")
            fields: A comma-separated list of fields to return for the issue. By default, all navigable and Jira default fields are returned. Use it to retrieve a subset of fields.
            expand: A comma-separated list of parameters to expand. This parameter accepts multiple values, including `renderedFields`, `names`, `schema`, `transitions`, `operations`, `editmeta`, `changelog`, and `versionedRepresentations`.
            properties: A comma-separated list of issue property keys. To get a list of all issue property keys, use the Get issue operation. A maximum of 5 properties can be requested.
            fields_by_keys: Whether the fields parameter contains field keys (true) or field IDs (false). Default is false.
            update_history: Whether the action taken is added to the user's Recent history. Default is false.
            fail_fast: Fail the request early if all field data cannot be retrieved. Default is false.
            **kwargs: Additional parameters
        
        Returns:
            Issue

    `update(self, issue_id_or_key: str, fields: IssuesUpdateParamsFields | None = None, update: dict[str, Any] | None = None, transition: IssuesUpdateParamsTransition | None = None, notify_users: bool | None = None, override_screen_security: bool | None = None, override_editable_flag: bool | None = None, return_issue: bool | None = None, expand: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.jira.models.Issue`
    :   Edits an issue. Issue properties may be updated as part of the edit. Only fields included in the request body are updated.
        
        Args:
            fields: The issue fields to update
            update: Additional update operations to perform
            transition: Transition the issue to a new status
            issue_id_or_key: The issue ID or key (e.g., "PROJ-123" or "10000")
            notify_users: Whether a notification email about the issue update is sent to all watchers. Default is true.
            override_screen_security: Whether screen security is overridden to enable hidden fields to be edited.
            override_editable_flag: Whether the issue's edit metadata is overridden.
            return_issue: Whether the updated issue is returned.
            expand: Expand options when returning the updated issue.
            **kwargs: Additional parameters
        
        Returns:
            Issue

<a id="JiraConnector"></a>

`JiraConnector(auth_config: JiraAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, subdomain: str | None = None)`
:   Type-safe Jira API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new jira connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., JiraAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)            subdomain: Your Jira Cloud subdomain
    Examples:
        # Local mode (direct API calls)
        connector = JiraConnector(auth_config=JiraAuthConfig(username="...", password="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = JiraConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = JiraConnector(
            auth_config=AirbyteAuthConfig(
                workspace_name="user-123",
                organization_id="00000000-0000-0000-0000-000000000123",
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789"
            )
        )

    ### Class variables

    `connector_name`
    :   The type of the None singleton.

    `connector_version`
    :   The type of the None singleton.

    `sdk_version`
    :   The type of the None singleton.

    ### Static methods

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'JiraAuthConfig'", name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None) ‑> airbyte_agent_sdk.connectors.jira.connector.JiraConnector`
    :   Create a new hosted connector on Airbyte Cloud.
        
        This factory method:
        1. Creates a source on Airbyte Cloud with the provided credentials
        2. Returns a connector configured with the new connector_id
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials and workspace_name.
                Optionally include organization_id for multi-org request routing.
            auth_config: Typed auth config (same as local mode)
            name: Optional source name (defaults to connector name + workspace_name)
            replication_config: Optional replication settings dict.
                Required for connectors with x-airbyte-replication-config (REPLICATION mode sources).
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            A JiraConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await JiraConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=JiraAuthConfig(username="...", password="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @JiraConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @JiraConnector.tool_utils(update_docstring=False, max_output_chars=None)
            async def execute(entity: str, action: str, params: dict):
                ...
        
        Args:
            update_docstring: When True, append connector capabilities to __doc__.
            max_output_chars: Max serialized output size before raising. Use None to disable.

    ### Instance variables

    `connector_id: str | None`
    :   Get the connector/source ID (only available in hosted mode).
        
        Returns:
            The connector ID if in hosted mode, None if in local mode.
        
        Example:
            connector = await JiraConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.jira.models.JiraCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            JiraCheckResult with status ("healthy" or "unhealthy") and optional error message
        
        Example:
            result = await connector.check()
            if result.status == "healthy":
                print("Connection verified!")
            else:
                print(f"Check failed: \{result.error\}")

    `close(self)`
    :   Close the connector and release resources.

    `entity_schema(self, entity: str) ‑> dict[str, typing.Any] | None`
    :   Get the JSON schema for an entity.
        
        Args:
            entity: Entity name (e.g., "contacts", "companies")
        
        Returns:
            JSON schema dict describing the entity structure, or None if not found.
        
        Example:
            schema = connector.entity_schema("contacts")
            if schema:
                print(f"Contact properties: \{list(schema.get('properties', \{\}).keys())\}")

    `execute(self, entity: str, action: "Literal['api_search', 'create', 'get', 'update', 'delete', 'list', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
    :   Execute an entity operation with full type safety.
        
        This is the recommended interface for blessed connectors as it:
        - Uses the same signature as non-blessed connectors
        - Provides full IDE autocomplete for entity/action/params
        - Makes migration from generic to blessed connectors seamless
        
        Args:
            entity: Entity name (e.g., "customers")
            action: Operation action (e.g., "create", "get", "list")
            params: Operation parameters (typed based on entity+action)
        
        Returns:
            Typed response based on the operation
        
        Example:
            customer = await connector.execute(
                entity="customers",
                action="get",
                params=\{"id": "cus_123"\}
            )

    `list_entities(self) ‑> list[dict[str, typing.Any]]`
    :   Get structured data about available entities, actions, and parameters.
        
        Returns a list of entity descriptions with:
        - entity_name: Name of the entity (e.g., "contacts", "deals")
        - description: Entity description from the first endpoint
        - available_actions: List of actions (e.g., ["list", "get", "create"])
        - parameters: Dict mapping action -> list of parameter dicts
        
        Example:
            entities = connector.list_entities()
            for entity in entities:
                print(f"\{entity['entity_name']\}: \{entity['available_actions']\}")

<a id="ProjectsQuery"></a>

`ProjectsQuery(connector: JiraConnector)`
:   Query class for Projects entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, start_at: int | None = None, max_results: int | None = None, order_by: str | None = None, id: list[int] | None = None, keys: list[str] | None = None, query: str | None = None, type_key: str | None = None, category_id: int | None = None, action: str | None = None, expand: str | None = None, status: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.jira.models.JiraExecuteResultWithMeta[list[Project], ProjectsApiSearchResultMeta]`
    :   Search and filter projects with advanced query parameters
        
        Args:
            start_at: The index of the first item to return in a page of results (page offset)
            max_results: The maximum number of items to return per page (max 100)
            order_by: Order the results by a field (prefix with + for ascending, - for descending)
            id: Filter by project IDs (up to 50)
            keys: Filter by project keys (up to 50)
            query: Filter using a literal string (matches project key or name, case insensitive)
            type_key: Filter by project type (comma-separated)
            category_id: Filter by project category ID
            action: Filter by user permission (view, browse, edit, create)
            expand: Comma-separated list of additional fields (description, projectKeys, lead, issueTypes, url, insight)
            status: EXPERIMENTAL - Filter by project status
            **kwargs: Additional parameters
        
        Returns:
            ProjectsApiSearchResult

    `context_store_search(self, query: ProjectsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.jira.models.AirbyteSearchResult[ProjectsSearchData]`
    :   Search projects records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ProjectsSearchFilter):
        - archived: Whether the project is archived
        - archived_by: The user who archived the project
        - archived_date: The date when the project was archived
        - assignee_type: The default assignee when creating issues for this project
        - avatar_urls: The URLs of the project's avatars
        - components: List of the components contained in the project
        - deleted: Whether the project is marked as deleted
        - deleted_by: The user who marked the project as deleted
        - deleted_date: The date when the project was marked as deleted
        - description: A brief description of the project
        - email: An email address associated with the project
        - entity_id: The unique identifier of the project entity
        - expand: Expand options that include additional project details in the response
        - favourite: Whether the project is selected as a favorite
        - id: The ID of the project
        - insight: Insights about the project
        - is_private: Whether the project is private
        - issue_type_hierarchy: The issue type hierarchy for the project
        - issue_types: List of the issue types available in the project
        - key: The key of the project
        - lead: The username of the project lead
        - name: The name of the project
        - permissions: User permissions on the project
        - project_category: The category the project belongs to
        - project_type_key: The project type of the project
        - properties: Map of project properties
        - retention_till_date: The date when the project is deleted permanently
        - roles: The name and self URL for each role defined in the project
        - self: The URL of the project details
        - simplified: Whether the project is simplified
        - style: The type of the project
        - url: A link to information about this project
        - uuid: Unique ID for next-gen projects
        - versions: The versions defined in the project
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ProjectsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, project_id_or_key: str, expand: str | None = None, properties: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.jira.models.Project`
    :   Retrieve a single project by its ID or key
        
        Args:
            project_id_or_key: The project ID or key (e.g., "PROJ" or "10000")
            expand: Comma-separated list of additional fields to include (description, projectKeys, lead, issueTypes, url, insight)
            properties: A comma-separated list of project property keys to return. To get a list of all project property keys, use Get project property keys.
            **kwargs: Additional parameters
        
        Returns:
            Project

<a id="UsersQuery"></a>

`UsersQuery(connector: JiraConnector)`
:   Query class for Users entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, query: str | None = None, start_at: int | None = None, max_results: int | None = None, account_id: str | None = None, property: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.jira.models.JiraExecuteResult[list[User]]`
    :   Search for users using a query string
        
        Args:
            query: A query string to search for users (matches display name, email, account ID)
            start_at: The index of the first item to return in a page of results (page offset)
            max_results: The maximum number of items to return per page (max 1000)
            account_id: Filter by account IDs (supports multiple values)
            property: Property key to filter users
            **kwargs: Additional parameters
        
        Returns:
            UsersApiSearchResult

    `context_store_search(self, query: UsersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.jira.models.AirbyteSearchResult[UsersSearchData]`
    :   Search users records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (UsersSearchFilter):
        - account_id: The account ID of the user, uniquely identifying the user across all Atlassian products
        - account_type: The user account type (atlassian, app, or customer)
        - active: Indicates whether the user is active
        - application_roles: The application roles assigned to the user
        - avatar_urls: The avatars of the user
        - display_name: The display name of the user
        - email_address: The email address of the user
        - expand: Options to include additional user details in the response
        - groups: The groups to which the user belongs
        - key: Deprecated property
        - locale: The locale of the user
        - name: Deprecated property
        - self: The URL of the user
        - time_zone: The time zone specified in the user's profile
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            UsersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, account_id: str, expand: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.jira.models.User`
    :   Retrieve a single user by their account ID
        
        Args:
            account_id: The account ID of the user
            expand: Comma-separated list of additional fields to include (groups, applicationRoles)
            **kwargs: Additional parameters
        
        Returns:
            User

    `list(self, start_at: int | None = None, max_results: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.jira.models.JiraExecuteResult[list[User]]`
    :   Returns a paginated list of users
        
        Args:
            start_at: The index of the first item to return in a page of results (page offset)
            max_results: The maximum number of items to return per page (max 1000)
            **kwargs: Additional parameters
        
        Returns:
            UsersListResult