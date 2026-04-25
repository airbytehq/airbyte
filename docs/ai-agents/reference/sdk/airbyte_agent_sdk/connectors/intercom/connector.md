---
id: airbyte_agent_sdk-connectors-intercom-connector
title: airbyte_agent_sdk.connectors.intercom.connector
---

Module airbyte_agent_sdk.connectors.intercom.connector
======================================================
Intercom connector.

Classes
-------

<a id="AdminsQuery"></a>

`AdminsQuery(connector: IntercomConnector)`
:   Query class for Admins entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.intercom.models.Admin`
    :   Get a single admin by ID
        
        Args:
            id: Admin ID
            **kwargs: Additional parameters
        
        Returns:
            Admin

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResult[list[Admin]]`
    :   Returns a list of all admins in the workspace
        
        Returns:
            AdminsListResult

<a id="CompaniesQuery"></a>

`CompaniesQuery(connector: IntercomConnector)`
:   Query class for Companies entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CompaniesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchResult[CompaniesSearchData]`
    :   Search companies records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CompaniesSearchFilter):
        - app_id: The ID of the application associated with the company
        - company_id: The unique identifier of the company
        - created_at: The date and time when the company was created
        - custom_attributes: Custom attributes specific to the company
        - id: The ID of the company
        - industry: The industry in which the company operates
        - monthly_spend: The monthly spend of the company
        - name: The name of the company
        - plan: Details of the company's subscription plan
        - remote_created_at: The remote date and time when the company was created
        - segments: Segments associated with the company
        - session_count: The number of sessions related to the company
        - size: The size of the company
        - tags: Tags associated with the company
        - type_: The type of the company
        - updated_at: The date and time when the company was last updated
        - user_count: The number of users associated with the company
        - website: The website of the company
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CompaniesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, company_id: str, name: str | None = None, plan: str | None = None, monthly_spend: float | None = None, size: int | None = None, website: str | None = None, industry: str | None = None, custom_attributes: dict[str, Any] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.intercom.models.Company`
    :   Create a new company or update an existing one by company_id
        
        Args:
            company_id: A unique identifier for the company from your system
            name: The name of the company
            plan: The name of the plan the company is on
            monthly_spend: The monthly spend of the company
            size: The number of employees in the company
            website: The URL of the company website
            industry: The industry the company operates in
            custom_attributes: Custom attributes for the company
            **kwargs: Additional parameters
        
        Returns:
            Company

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.intercom.models.Company`
    :   Get a single company by ID
        
        Args:
            id: Company ID
            **kwargs: Additional parameters
        
        Returns:
            Company

    `list(self, per_page: int | None = None, starting_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResultWithMeta[list[Company], CompaniesListResultMeta]`
    :   Returns a paginated list of companies
        
        Args:
            per_page: Number of companies to return per page
            starting_after: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            CompaniesListResult

    `update(self, name: str | None = None, plan: str | None = None, monthly_spend: float | None = None, size: int | None = None, website: str | None = None, industry: str | None = None, custom_attributes: dict[str, Any] | None = None, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.intercom.models.Company`
    :   Update an existing company by ID
        
        Args:
            name: The name of the company
            plan: The name of the plan the company is on
            monthly_spend: The monthly spend of the company
            size: The number of employees in the company
            website: The URL of the company website
            industry: The industry the company operates in
            custom_attributes: Custom attributes for the company
            id: Company ID
            **kwargs: Additional parameters
        
        Returns:
            Company

<a id="ContactsQuery"></a>

`ContactsQuery(connector: IntercomConnector)`
:   Query class for Contacts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ContactsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchResult[ContactsSearchData]`
    :   Search contacts records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ContactsSearchFilter):
        - android_app_name: The name of the Android app associated with the contact.
        - android_app_version: The version of the Android app associated with the contact.
        - android_device: The device used by the contact for Android.
        - android_last_seen_at: The date and time when the contact was last seen on Android.
        - android_os_version: The operating system version of the Android device.
        - android_sdk_version: The SDK version of the Android device.
        - avatar: URL pointing to the contact's avatar image.
        - browser: The browser used by the contact.
        - browser_language: The language preference set in the contact's browser.
        - browser_version: The version of the browser used by the contact.
        - companies: Companies associated with the contact.
        - created_at: The date and time when the contact was created.
        - custom_attributes: Custom attributes defined for the contact.
        - email: The email address of the contact.
        - external_id: External identifier for the contact.
        - has_hard_bounced: Flag indicating if the contact has hard bounced.
        - id: The unique identifier of the contact.
        - ios_app_name: The name of the iOS app associated with the contact.
        - ios_app_version: The version of the iOS app associated with the contact.
        - ios_device: The device used by the contact for iOS.
        - ios_last_seen_at: The date and time when the contact was last seen on iOS.
        - ios_os_version: The operating system version of the iOS device.
        - ios_sdk_version: The SDK version of the iOS device.
        - language_override: Language override set for the contact.
        - last_contacted_at: The date and time when the contact was last contacted.
        - last_email_clicked_at: The date and time when the contact last clicked an email.
        - last_email_opened_at: The date and time when the contact last opened an email.
        - last_replied_at: The date and time when the contact last replied.
        - last_seen_at: The date and time when the contact was last seen overall.
        - location: Location details of the contact.
        - marked_email_as_spam: Flag indicating if the contact's email was marked as spam.
        - name: The name of the contact.
        - notes: Notes associated with the contact.
        - opted_in_subscription_types: Subscription types the contact opted into.
        - opted_out_subscription_types: Subscription types the contact opted out from.
        - os: Operating system of the contact's device.
        - owner_id: The unique identifier of the contact's owner.
        - phone: The phone number of the contact.
        - referrer: Referrer information related to the contact.
        - role: Role or position of the contact.
        - signed_up_at: The date and time when the contact signed up.
        - sms_consent: Consent status for SMS communication.
        - social_profiles: Social profiles associated with the contact.
        - tags: Tags associated with the contact.
        - type_: Type of contact.
        - unsubscribed_from_emails: Flag indicating if the contact unsubscribed from emails.
        - unsubscribed_from_sms: Flag indicating if the contact unsubscribed from SMS.
        - updated_at: The date and time when the contact was last updated.
        - utm_campaign: Campaign data from UTM parameters.
        - utm_content: Content data from UTM parameters.
        - utm_medium: Medium data from UTM parameters.
        - utm_source: Source data from UTM parameters.
        - utm_term: Term data from UTM parameters.
        - workspace_id: The unique identifier of the workspace associated with the contact.
        
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

    `create(self, role: str, external_id: str | None = None, email: str | None = None, phone: str | None = None, name: str | None = None, avatar: str | None = None, signed_up_at: int | None = None, last_seen_at: int | None = None, owner_id: int | None = None, unsubscribed_from_emails: bool | None = None, custom_attributes: dict[str, Any] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.intercom.models.Contact`
    :   Create a new contact (user or lead)
        
        Args:
            role: The role of the contact (user or lead)
            external_id: A unique identifier for the contact from your system
            email: The contact's email address
            phone: The contact's phone number
            name: The contact's full name
            avatar: An image URL for the contact's avatar
            signed_up_at: Sign up timestamp (Unix)
            last_seen_at: Last seen timestamp (Unix)
            owner_id: The ID of the admin assigned as owner
            unsubscribed_from_emails: Whether the contact is unsubscribed from emails
            custom_attributes: Custom attributes for the contact
            **kwargs: Additional parameters
        
        Returns:
            Contact

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.intercom.models.Contact`
    :   Get a single contact by ID
        
        Args:
            id: Contact ID
            **kwargs: Additional parameters
        
        Returns:
            Contact

    `list(self, per_page: int | None = None, starting_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResultWithMeta[list[Contact], ContactsListResultMeta]`
    :   Returns a paginated list of contacts in the workspace
        
        Args:
            per_page: Number of contacts to return per page
            starting_after: Cursor for pagination - get contacts after this ID
            **kwargs: Additional parameters
        
        Returns:
            ContactsListResult

    `update(self, role: str | None = None, external_id: str | None = None, email: str | None = None, phone: str | None = None, name: str | None = None, avatar: str | None = None, signed_up_at: int | None = None, last_seen_at: int | None = None, owner_id: int | None = None, unsubscribed_from_emails: bool | None = None, custom_attributes: dict[str, Any] | None = None, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.intercom.models.Contact`
    :   Update an existing contact by ID
        
        Args:
            role: The role of the contact (user or lead)
            external_id: A unique identifier for the contact from your system
            email: The contact's email address
            phone: The contact's phone number
            name: The contact's full name
            avatar: An image URL for the contact's avatar
            signed_up_at: Sign up timestamp (Unix)
            last_seen_at: Last seen timestamp (Unix)
            owner_id: The ID of the admin assigned as owner
            unsubscribed_from_emails: Whether the contact is unsubscribed from emails
            custom_attributes: Custom attributes for the contact
            id: Contact ID
            **kwargs: Additional parameters
        
        Returns:
            Contact

<a id="ConversationsQuery"></a>

`ConversationsQuery(connector: IntercomConnector)`
:   Query class for Conversations entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ConversationsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchResult[ConversationsSearchData]`
    :   Search conversations records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ConversationsSearchFilter):
        - admin_assignee_id: The ID of the administrator assigned to the conversation
        - ai_agent: Data related to AI Agent involvement in the conversation
        - ai_agent_participated: Indicates whether AI Agent participated in the conversation
        - assignee: The assigned user responsible for the conversation.
        - contacts: List of contacts involved in the conversation.
        - conversation_message: The main message content of the conversation.
        - conversation_rating: Ratings given to the conversation by the customer and teammate.
        - created_at: The timestamp when the conversation was created
        - custom_attributes: Custom attributes associated with the conversation
        - customer_first_reply: Timestamp indicating when the customer first replied.
        - customers: List of customers involved in the conversation
        - first_contact_reply: Timestamp indicating when the first contact replied.
        - id: The unique ID of the conversation
        - linked_objects: Linked objects associated with the conversation
        - open: Indicates if the conversation is open or closed
        - priority: The priority level of the conversation
        - read: Indicates if the conversation has been read
        - redacted: Indicates if the conversation is redacted
        - sent_at: The timestamp when the conversation was sent
        - sla_applied: Service Level Agreement details applied to the conversation.
        - snoozed_until: Timestamp until the conversation is snoozed
        - source: Source details of the conversation.
        - state: The state of the conversation (e.g., new, in progress)
        - statistics: Statistics related to the conversation.
        - tags: Tags applied to the conversation.
        - team_assignee_id: The ID of the team assigned to the conversation
        - teammates: List of teammates involved in the conversation.
        - title: The title of the conversation
        - topics: Topics associated with the conversation.
        - type_: The type of the conversation
        - updated_at: The timestamp when the conversation was last updated
        - user: The user related to the conversation.
        - waiting_since: Timestamp since waiting for a response
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ConversationsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.intercom.models.Conversation`
    :   Get a single conversation by ID
        
        Args:
            id: Conversation ID
            **kwargs: Additional parameters
        
        Returns:
            Conversation

    `list(self, per_page: int | None = None, starting_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResultWithMeta[list[Conversation], ConversationsListResultMeta]`
    :   Returns a paginated list of conversations
        
        Args:
            per_page: Number of conversations to return per page
            starting_after: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            ConversationsListResult

<a id="IntercomConnector"></a>

`IntercomConnector(auth_config: IntercomAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Intercom API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new intercom connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., IntercomAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = IntercomConnector(auth_config=IntercomAuthConfig(access_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = IntercomConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = IntercomConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'IntercomAuthConfig'", name: str | None = None, replication_config: "'IntercomReplicationConfig' | None" = None, source_template_id: str | None = None)`
    :   Create a new hosted connector on Airbyte Cloud.
        
        This factory method:
        1. Creates a source on Airbyte Cloud with the provided credentials
        2. Returns a connector configured with the new connector_id
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials and workspace_name.
                Optionally include organization_id for multi-org request routing.
            auth_config: Typed auth config (same as local mode)
            name: Optional source name (defaults to connector name + workspace_name)
            replication_config: Typed replication settings.
                Required for connectors with x-airbyte-replication-config (REPLICATION mode sources).
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            A IntercomConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await IntercomConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=IntercomAuthConfig(access_token="..."),
            )
        
            # With replication config (required for this connector):
            connector = await IntercomConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=IntercomAuthConfig(access_token="..."),
                replication_config=IntercomReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @IntercomConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @IntercomConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await IntercomConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.intercom.models.IntercomCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            IntercomCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'create', 'get', 'update', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
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

<a id="InternalArticlesQuery"></a>

`InternalArticlesQuery(connector: IntercomConnector)`
:   Query class for InternalArticles entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, title: str, owner_id: int, author_id: int, body: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.intercom.models.InternalArticle`
    :   Create a new internal article in the workspace
        
        Args:
            title: The title of the article
            body: The content of the article in HTML
            owner_id: The ID of the owner of the article
            author_id: The ID of the author of the article
            **kwargs: Additional parameters
        
        Returns:
            InternalArticle

<a id="NotesQuery"></a>

`NotesQuery(connector: IntercomConnector)`
:   Query class for Notes entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, body: str, contact_id: str, admin_id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.intercom.models.Note`
    :   Create a note on an existing contact
        
        Args:
            body: The body of the note in HTML format
            admin_id: The ID of the admin creating the note
            contact_id: Contact ID to add note to
            **kwargs: Additional parameters
        
        Returns:
            Note

<a id="SegmentsQuery"></a>

`SegmentsQuery(connector: IntercomConnector)`
:   Query class for Segments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.intercom.models.Segment`
    :   Get a single segment by ID
        
        Args:
            id: Segment ID
            **kwargs: Additional parameters
        
        Returns:
            Segment

    `list(self, include_count: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResult[list[Segment]]`
    :   Returns a list of all segments in the workspace
        
        Args:
            include_count: Include count of contacts in each segment
            **kwargs: Additional parameters
        
        Returns:
            SegmentsListResult

<a id="TagsQuery"></a>

`TagsQuery(connector: IntercomConnector)`
:   Query class for Tags entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, name: str, **kwargs) ‑> airbyte_agent_sdk.connectors.intercom.models.Tag`
    :   Create a new tag or update an existing one
        
        Args:
            name: The name of the tag
            **kwargs: Additional parameters
        
        Returns:
            Tag

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.intercom.models.Tag`
    :   Get a single tag by ID
        
        Args:
            id: Tag ID
            **kwargs: Additional parameters
        
        Returns:
            Tag

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResult[list[Tag]]`
    :   Returns a list of all tags in the workspace
        
        Returns:
            TagsListResult

<a id="TeamsQuery"></a>

`TeamsQuery(connector: IntercomConnector)`
:   Query class for Teams entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TeamsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchResult[TeamsSearchData]`
    :   Search teams records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TeamsSearchFilter):
        - admin_ids: Array of user IDs representing the admins of the team.
        - id: Unique identifier for the team.
        - name: Name of the team.
        - type_: Type of team (e.g., 'internal', 'external').
        
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

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.intercom.models.Team`
    :   Get a single team by ID
        
        Args:
            id: Team ID
            **kwargs: Additional parameters
        
        Returns:
            Team

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResult[list[Team]]`
    :   Returns a list of all teams in the workspace
        
        Returns:
            TeamsListResult