---
id: airbyte_agent_sdk-connectors-pylon-connector
title: airbyte_agent_sdk.connectors.pylon.connector
---

Module airbyte_agent_sdk.connectors.pylon.connector
===================================================
Pylon connector.

Classes
-------

<a id="AccountsQuery"></a>

`AccountsQuery(connector: PylonConnector)`
:   Query class for Accounts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AccountsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult[AccountsSearchData]`
    :   Search accounts records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AccountsSearchFilter):
        - id: Unique identifier for the account
        - name: Name of the account (customer organization)
        - domain: Primary domain associated with the account
        - primary_domain: Canonical primary domain for the account
        - type_: Classification of the account (e.g. customer, prospect)
        - is_disabled: Whether the account has been disabled
        - created_at: Timestamp when the account was created, in ISO 8601 format
        - latest_customer_activity_time: Timestamp of the most recent activity from this account, in ISO 8601 format
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AccountsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, name: str, domains: list[str] | None = None, primary_domain: str | None = None, owner_id: str | None = None, logo_url: str | None = None, tags: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.AccountResponse`
    :   Create a new account
        
        Args:
            name: The name of the account
            domains: The domains of the account (e.g. stripe.com)
            primary_domain: Must be in the list of domains. If there are any domains, there must be exactly one primary domain.
            owner_id: The ID of the owner of the account
            logo_url: The logo URL of the account. Must be a square .png, .jpg or .jpeg.
            tags: Tags to associate with the account
            **kwargs: Additional parameters
        
        Returns:
            AccountResponse

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.Account`
    :   Get a single account by ID
        
        Args:
            id: The ID of the account
            **kwargs: Additional parameters
        
        Returns:
            Account

    `list(self, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta[list[Account], AccountsListResultMeta]`
    :   Get a list of accounts
        
        Args:
            cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            AccountsListResult

    `update(self, name: str | None = None, domains: list[str] | None = None, primary_domain: str | None = None, owner_id: str | None = None, logo_url: str | None = None, is_disabled: bool | None = None, tags: list[str] | None = None, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.AccountResponse`
    :   Update an existing account by ID
        
        Args:
            name: The name of the account
            domains: Domains of the account. Must specify one domain as primary.
            primary_domain: Must be in the list of domains. If there are any domains, there must be exactly one primary domain.
            owner_id: The ID of the owner of the account. If empty string is passed in, the owner will be removed.
            logo_url: Logo URL of the account
            is_disabled: Whether the account is disabled
            tags: Tags to associate with the account
            id: The ID of the account to update
            **kwargs: Additional parameters
        
        Returns:
            AccountResponse

<a id="ArticlesQuery"></a>

`ArticlesQuery(connector: PylonConnector)`
:   Query class for Articles entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, title: str, body_html: str, author_user_id: str, kb_id: str, slug: str | None = None, is_published: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.ArticleResponse`
    :   Create a new article in a knowledge base
        
        Args:
            title: The title of the article
            body_html: The HTML body of the article
            author_user_id: The ID of the user attributed as the author
            slug: The slug of the article
            is_published: Whether the article should be published
            kb_id: The ID of the knowledge base
            **kwargs: Additional parameters
        
        Returns:
            ArticleResponse

    `update(self, kb_id: str, article_id: str, title: str | None = None, body_html: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.ArticleResponse`
    :   Update an existing article in a knowledge base
        
        Args:
            title: The title of the article
            body_html: The HTML body of the article
            kb_id: The ID of the knowledge base
            article_id: The ID of the article to update
            **kwargs: Additional parameters
        
        Returns:
            ArticleResponse

<a id="CollectionsQuery"></a>

`CollectionsQuery(connector: PylonConnector)`
:   Query class for Collections entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, title: str, kb_id: str, description: str | None = None, slug: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.CollectionResponse`
    :   Create a new collection in a knowledge base
        
        Args:
            title: The title of the collection
            description: The description of the collection
            slug: The slug of the collection
            kb_id: The ID of the knowledge base
            **kwargs: Additional parameters
        
        Returns:
            CollectionResponse

<a id="ContactsQuery"></a>

`ContactsQuery(connector: PylonConnector)`
:   Query class for Contacts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ContactsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult[ContactsSearchData]`
    :   Search contacts records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ContactsSearchFilter):
        - id: Unique identifier for the contact
        - name: Full name of the contact
        - email: Primary email address of the contact
        - primary_phone_number: Primary phone number of the contact
        - portal_role: Role the contact has in the customer portal
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ContactsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, name: str, email: str | None = None, account_id: str | None = None, avatar_url: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.ContactResponse`
    :   Create a new contact
        
        Args:
            name: The name of the contact
            email: The email address of the contact
            account_id: The ID of the account to associate this contact with
            avatar_url: The URL of the contact's avatar
            **kwargs: Additional parameters
        
        Returns:
            ContactResponse

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.Contact`
    :   Get a single contact by ID
        
        Args:
            id: The ID of the contact
            **kwargs: Additional parameters
        
        Returns:
            Contact

    `list(self, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta[list[Contact], ContactsListResultMeta]`
    :   Get a list of contacts
        
        Args:
            cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            ContactsListResult

    `update(self, name: str | None = None, email: str | None = None, account_id: str | None = None, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.ContactResponse`
    :   Update an existing contact by ID
        
        Args:
            name: The name of the contact
            email: The email address of the contact
            account_id: The ID of the account to associate this contact with
            id: The ID of the contact to update
            **kwargs: Additional parameters
        
        Returns:
            ContactResponse

<a id="CustomFieldsQuery"></a>

`CustomFieldsQuery(connector: PylonConnector)`
:   Query class for CustomFields entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CustomFieldsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult[CustomFieldsSearchData]`
    :   Search custom_fields records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CustomFieldsSearchFilter):
        - id: Unique identifier for the custom field
        - label: Display label of the custom field
        - slug: URL-safe identifier for the custom field
        - type_: Data type of the custom field (e.g. text, select)
        - object_type: Type of object this custom field applies to (e.g. issue, account)
        - is_read_only: Whether the custom field is read-only
        - created_at: Timestamp when the custom field was created, in ISO 8601 format
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CustomFieldsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.CustomField`
    :   Get a custom field by its ID
        
        Args:
            id: The ID of the custom field
            **kwargs: Additional parameters
        
        Returns:
            CustomField

    `list(self, object_type: str, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta[list[CustomField], CustomFieldsListResultMeta]`
    :   Get all custom fields for a given object type
        
        Args:
            object_type: The object type of the custom fields. Can be "account", "issue", or "contact".
            cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            CustomFieldsListResult

<a id="IssueAssignmentsQuery"></a>

`IssueAssignmentsQuery(connector: PylonConnector)`
:   Query class for IssueAssignments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `update(self, assignee_id: str | None = None, team_id: str | None = None, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.IssueResponse`
    :   Assign an issue to a user or team, or remove the current assignment.
        
        Args:
            assignee_id: The ID of the user to assign the issue to. Pass an empty string to unassign.
            team_id: The ID of the team to assign the issue to. Pass an empty string to remove team assignment.
            id: The ID of the issue to assign
            **kwargs: Additional parameters
        
        Returns:
            IssueResponse

<a id="IssueNotesQuery"></a>

`IssueNotesQuery(connector: PylonConnector)`
:   Query class for IssueNotes entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, body_html: str, thread_id: str | None = None, message_id: str | None = None, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.IssueNoteResponse`
    :   Create an internal note on an issue
        
        Args:
            body_html: The HTML content of the note
            thread_id: The ID of the thread to add the note to
            message_id: The ID of the message to add the note to
            id: The ID of the issue to add a note to
            **kwargs: Additional parameters
        
        Returns:
            IssueNoteResponse

<a id="IssueRepliesQuery"></a>

`IssueRepliesQuery(connector: PylonConnector)`
:   Query class for IssueReplies entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, body_html: str, message_id: str, user_id: str | None = None, contact_id: str | None = None, attachment_urls: list[str] | None = None, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.IssueReplyResponse`
    :   Sends a customer-facing reply on an issue, visible to the requester.
        
        Args:
            body_html: The body of the reply message in HTML
            message_id: The ID of the message to reply to
            user_id: Optional user ID to post the message as. Only one of user_id or contact_id can be provided.
            contact_id: Optional contact ID to post the message as. Only one of user_id or contact_id can be provided.
            attachment_urls: An array of attachment URLs to attach to this reply
            id: The ID of the issue to reply to
            **kwargs: Additional parameters
        
        Returns:
            IssueReplyResponse

<a id="IssueStatusesQuery"></a>

`IssueStatusesQuery(connector: PylonConnector)`
:   Query class for IssueStatuses entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `update(self, state: str, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.IssueResponse`
    :   Transition an issue to a new status (new, waiting_on_you, waiting_on_customer, on_hold, closed, or a custom status slug).
        
        Args:
            state: The target state for the issue (new, waiting_on_you, waiting_on_customer, on_hold, closed, or a custom status slug)
            id: The ID of the issue to update status for
            **kwargs: Additional parameters
        
        Returns:
            IssueResponse

<a id="IssueThreadsQuery"></a>

`IssueThreadsQuery(connector: PylonConnector)`
:   Query class for IssueThreads entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, name: str | None = None, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.IssueThreadResponse`
    :   Create a new thread on an issue
        
        Args:
            name: The name of the thread
            id: The ID of the issue to create a thread on
            **kwargs: Additional parameters
        
        Returns:
            IssueThreadResponse

<a id="IssuesQuery"></a>

`IssuesQuery(connector: PylonConnector)`
:   Query class for Issues entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: IssuesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult[IssuesSearchData]`
    :   Search issues records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (IssuesSearchFilter):
        - id: Unique identifier for the issue
        - title: Title of the issue
        - state: Current state of the issue (e.g. new, in_progress, closed)
        - source: Channel the issue originated from (e.g. email, slack)
        - type_: Type classification of the issue
        - number: Human-readable issue number within the workspace
        - created_at: Timestamp when the issue was created, in ISO 8601 format
        - latest_message_time: Timestamp of the most recent message on the issue, in ISO 8601 format
        - resolution_time: Timestamp when the issue was resolved, in ISO 8601 format
        - snoozed_until_time: Timestamp the issue is snoozed until, in ISO 8601 format
        - customer_portal_visible: Whether the issue is visible in the customer portal
        
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

    `create(self, title: str, body_html: str, priority: str | None = None, requester_email: str | None = None, requester_name: str | None = None, account_id: str | None = None, assignee_id: str | None = None, team_id: str | None = None, tags: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.IssueResponse`
    :   Create a new issue
        
        Args:
            title: The title of the issue
            body_html: The HTML content of the body of the issue
            priority: The priority of the issue (urgent, high, medium, low)
            requester_email: The email of the requester
            requester_name: The full name of the requester
            account_id: The account that this issue belongs to
            assignee_id: The user the issue should be assigned to
            team_id: The ID of the team this issue should be assigned to
            tags: Tags to associate with the issue
            **kwargs: Additional parameters
        
        Returns:
            IssueResponse

    `delete(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.DeleteIssueResponse`
    :   Permanently deletes an issue by ID. This action cannot be undone.
        
        Args:
            id: The ID of the issue to delete
            **kwargs: Additional parameters
        
        Returns:
            DeleteIssueResponse

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.Issue`
    :   Get a single issue by ID
        
        Args:
            id: The ID of the issue
            **kwargs: Additional parameters
        
        Returns:
            Issue

    `list(self, start_time: str, end_time: str, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta[list[Issue], IssuesListResultMeta]`
    :   Get a list of issues within a time range
        
        Args:
            start_time: The start time (RFC3339) of the time range to get issues for.
            end_time: The end time (RFC3339) of the time range to get issues for.
            cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            IssuesListResult

    `update(self, state: str | None = None, assignee_id: str | None = None, team_id: str | None = None, account_id: str | None = None, tags: list[str] | None = None, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.IssueResponse`
    :   Update an existing issue by ID
        
        Args:
            state: The state of the issue (open, snoozed, closed)
            assignee_id: The user the issue should be assigned to
            team_id: The ID of the team this issue should be assigned to
            account_id: The account that this issue belongs to
            tags: Tags to associate with the issue
            id: The ID of the issue to update
            **kwargs: Additional parameters
        
        Returns:
            IssueResponse

<a id="MeQuery"></a>

`MeQuery(connector: PylonConnector)`
:   Query class for Me entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.User`
    :   Get the currently authenticated user
        
        Returns:
            User

<a id="MessagesQuery"></a>

`MessagesQuery(connector: PylonConnector)`
:   Query class for Messages entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: MessagesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult[MessagesSearchData]`
    :   Search messages records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (MessagesSearchFilter):
        - id: Unique identifier for the message
        - timestamp: Timestamp the message was posted, in ISO 8601 format
        - is_private: Whether the message is an internal note (not visible to the customer)
        - source: Channel the message was sent through (e.g. email, slack)
        - thread_id: Identifier of the thread this message belongs to
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            MessagesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, id: str | None = None, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta[list[Message], MessagesListResultMeta]`
    :   Returns all messages on an issue (customer-facing replies and internal notes)
        
        Args:
            id: The ID of the issue to fetch messages for
            cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            MessagesListResult

<a id="MilestonesQuery"></a>

`MilestonesQuery(connector: PylonConnector)`
:   Query class for Milestones entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, name: str, project_id: str, due_date: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.MilestoneResponse`
    :   Create a new milestone
        
        Args:
            name: The name of the milestone
            project_id: The project ID for the milestone
            due_date: The due date of the milestone (RFC3339)
            **kwargs: Additional parameters
        
        Returns:
            MilestoneResponse

    `update(self, name: str | None = None, due_date: str | None = None, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.MilestoneResponse`
    :   Update an existing milestone by ID
        
        Args:
            name: The name of the milestone
            due_date: The due date of the milestone (RFC3339)
            id: The ID of the milestone to update
            **kwargs: Additional parameters
        
        Returns:
            MilestoneResponse

<a id="ProjectsQuery"></a>

`ProjectsQuery(connector: PylonConnector)`
:   Query class for Projects entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, name: str, account_id: str, description_html: str | None = None, start_date: str | None = None, end_date: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.ProjectResponse`
    :   Create a new project
        
        Args:
            name: The name of the project
            account_id: The account ID for the project
            description_html: The HTML description of the project
            start_date: The start date of the project (RFC3339)
            end_date: The end date of the project (RFC3339)
            **kwargs: Additional parameters
        
        Returns:
            ProjectResponse

    `update(self, name: str | None = None, description_html: str | None = None, is_archived: bool | None = None, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.ProjectResponse`
    :   Update an existing project by ID
        
        Args:
            name: The name of the project
            description_html: The HTML description of the project
            is_archived: Whether the project is archived
            id: The ID of the project to update
            **kwargs: Additional parameters
        
        Returns:
            ProjectResponse

<a id="PylonConnector"></a>

`PylonConnector(auth_config: PylonAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Pylon API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new pylon connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., PylonAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = PylonConnector(auth_config=PylonAuthConfig(api_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = PylonConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = PylonConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'PylonAuthConfig'", name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None) ‑> airbyte_agent_sdk.connectors.pylon.connector.PylonConnector`
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
            A PylonConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await PylonConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=PylonAuthConfig(api_token="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000, framework: FrameworkName | None = None, internal_retries: int = 0, should_internal_retry: Callable[[Exception, tuple[Any, ...], dict[str, Any]], bool] | None = None, exhausted_runtime_failure_message: Callable[[Exception, tuple[Any, ...], dict[str, Any]], str | None] | None = None) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Composes :func:`airbyte_agent_sdk.translation.translate_exceptions` for
        runtime wrapping (sync/async branch + output-size check + framework
        signal translation + optional internal retry loop), and adds
        connector-specific docstring augmentation on top of it.
        
        Usage:
            @mcp.tool()
            @PylonConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @PylonConnector.tool_utils(update_docstring=False, max_output_chars=None)
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @PylonConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
            async def execute(entity: str, action: str, params: dict):
                ...
        
        Args:
            update_docstring: When True, append connector capabilities to __doc__.
            max_output_chars: Max serialized output size before raising. Use None to disable.
            framework: One of ``"pydantic_ai" | "langchain" | "openai_agents" | "mcp"``.
                Defaults to None → auto-detect by attempting each framework's canonical
                import in order. Explicit always wins.
            internal_retries: How many transient runtime failures (429/5xx, network,
                timeout) to retry silently before surfacing. Default 0. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.
            should_internal_retry: Optional predicate ``(error, args, kwargs) -> bool``
                further restricting which retryable errors are safe for this specific
                tool. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.
            exhausted_runtime_failure_message: Optional callback
                ``(error, args, kwargs) -> str | None``. Invoked after internal retries
                are exhausted OR were skipped via ``should_internal_retry`` returning
                False. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.

    ### Instance variables

    `connector_id: str | None`
    :   Get the connector/source ID (only available in hosted mode).
        
        Returns:
            The connector ID if in hosted mode, None if in local mode.
        
        Example:
            connector = await PylonConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.pylon.models.PylonCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            PylonCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'create', 'get', 'update', 'delete', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
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

<a id="TagsQuery"></a>

`TagsQuery(connector: PylonConnector)`
:   Query class for Tags entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TagsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult[TagsSearchData]`
    :   Search tags records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TagsSearchFilter):
        - id: Unique identifier for the tag
        - value: Display value of the tag
        - object_type: Type of object this tag applies to (e.g. issue, account)
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TagsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, value: str, object_type: str, hex_color: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.TagResponse`
    :   Create a new tag
        
        Args:
            value: The tag value
            object_type: The object type (issue, account, contact)
            hex_color: The hex color code of the tag
            **kwargs: Additional parameters
        
        Returns:
            TagResponse

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.Tag`
    :   Get a tag by its ID
        
        Args:
            id: The ID of the tag
            **kwargs: Additional parameters
        
        Returns:
            Tag

    `list(self, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta[list[Tag], TagsListResultMeta]`
    :   Get all tags
        
        Args:
            cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            TagsListResult

    `update(self, value: str | None = None, hex_color: str | None = None, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.TagResponse`
    :   Update an existing tag by ID
        
        Args:
            value: The tag value
            hex_color: The hex color code of the tag
            id: The ID of the tag to update
            **kwargs: Additional parameters
        
        Returns:
            TagResponse

<a id="TasksQuery"></a>

`TasksQuery(connector: PylonConnector)`
:   Query class for Tasks entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, title: str, body_html: str | None = None, status: str | None = None, assignee_id: str | None = None, project_id: str | None = None, milestone_id: str | None = None, due_date: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.TaskResponse`
    :   Create a new task
        
        Args:
            title: The title of the task
            body_html: The body HTML of the task
            status: The status of the task (not_started, in_progress, completed)
            assignee_id: The assignee ID for the task
            project_id: The project ID for the task
            milestone_id: The milestone ID for the task
            due_date: The due date for the task (RFC3339)
            **kwargs: Additional parameters
        
        Returns:
            TaskResponse

    `update(self, title: str | None = None, body_html: str | None = None, status: str | None = None, assignee_id: str | None = None, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.TaskResponse`
    :   Update an existing task by ID
        
        Args:
            title: The title of the task
            body_html: The body HTML of the task
            status: The status of the task (not_started, in_progress, completed)
            assignee_id: The assignee ID for the task
            id: The ID of the task to update
            **kwargs: Additional parameters
        
        Returns:
            TaskResponse

<a id="TeamsQuery"></a>

`TeamsQuery(connector: PylonConnector)`
:   Query class for Teams entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TeamsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult[TeamsSearchData]`
    :   Search teams records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TeamsSearchFilter):
        - id: Unique identifier for the team
        - name: Name of the team
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TeamsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, name: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.TeamResponse`
    :   Create a new team
        
        Args:
            name: The name of the team
            **kwargs: Additional parameters
        
        Returns:
            TeamResponse

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.Team`
    :   Get a single team by ID
        
        Args:
            id: The ID of the team
            **kwargs: Additional parameters
        
        Returns:
            Team

    `list(self, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta[list[Team], TeamsListResultMeta]`
    :   Get a list of teams
        
        Args:
            cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            TeamsListResult

    `update(self, name: str | None = None, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.TeamResponse`
    :   Update an existing team by ID
        
        Args:
            name: The name of the team
            id: The ID of the team to update
            **kwargs: Additional parameters
        
        Returns:
            TeamResponse

<a id="TicketFormsQuery"></a>

`TicketFormsQuery(connector: PylonConnector)`
:   Query class for TicketForms entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TicketFormsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult[TicketFormsSearchData]`
    :   Search ticket_forms records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TicketFormsSearchFilter):
        - id: Unique identifier for the ticket form
        - name: Display name of the ticket form
        - slug: URL-safe identifier for the ticket form
        - is_public: Whether the ticket form is publicly accessible
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TicketFormsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta[list[TicketForm], TicketFormsListResultMeta]`
    :   Get a list of ticket forms
        
        Args:
            cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            TicketFormsListResult

<a id="UserRolesQuery"></a>

`UserRolesQuery(connector: PylonConnector)`
:   Query class for UserRoles entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: UserRolesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult[UserRolesSearchData]`
    :   Search user_roles records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (UserRolesSearchFilter):
        - id: Unique identifier for the user role
        - name: Display name of the user role
        - slug: URL-safe identifier for the user role
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            UserRolesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta[list[UserRole], UserRolesListResultMeta]`
    :   Get a list of all user roles
        
        Args:
            cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            UserRolesListResult

<a id="UsersQuery"></a>

`UsersQuery(connector: PylonConnector)`
:   Query class for Users entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: UsersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult[UsersSearchData]`
    :   Search users records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (UsersSearchFilter):
        - id: Unique identifier for the user
        - name: Full name of the user
        - email: Primary email address of the user
        - role_id: Identifier of the user's role
        - status: Current status of the user (e.g. active, disabled)
        
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

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.User`
    :   Get a single user by ID
        
        Args:
            id: The ID of the user
            **kwargs: Additional parameters
        
        Returns:
            User

    `list(self, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta[list[User], UsersListResultMeta]`
    :   Get a list of users
        
        Args:
            cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            UsersListResult