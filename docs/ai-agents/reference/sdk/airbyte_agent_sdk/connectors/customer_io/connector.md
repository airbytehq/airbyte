---
id: airbyte_agent_sdk-connectors-customer_io-connector
title: airbyte_agent_sdk.connectors.customer_io.connector
---

Module airbyte_agent_sdk.connectors.customer_io.connector
=========================================================
Customer-Io connector.

Classes
-------

<a id="ActivitiesQuery"></a>

`ActivitiesQuery(connector: CustomerIoConnector)`
:   Query class for Activities entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, start: str | None = None, limit: int | None = None, type: str | None = None, name: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResultWithMeta[list[Activity], ActivitiesListResultMeta]`
    :   Returns a paginated list of activities in the workspace.
        
        Args:
            start: Pagination cursor for the next page
            limit: Maximum number of activities to return
            type: Filter by activity type
            name: Filter by event name
            **kwargs: Additional parameters
        
        Returns:
            ActivitiesListResult

<a id="BroadcastTriggerQuery"></a>

`BroadcastTriggerQuery(connector: CustomerIoConnector)`
:   Query class for BroadcastTrigger entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, campaign_id: str, data: dict[str, Any] | None = None, recipients: dict[str, Any] | None = None, ids: list[str] | None = None, emails: list[str] | None = None, per_user_data: list[dict[str, Any]] | None = None, data_file_url: str | None = None, id_ignore_missing: bool | None = None, email_ignore_missing: bool | None = None, email_add_duplicates: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.BroadcastTriggerResponse`
    :   Triggers an API-triggered broadcast campaign. The broadcast must be configured as API-triggered in the Customer.io UI. Cannot be triggered more than once every 10 seconds, with a maximum of 5 queued broadcasts per campaign. Recipients must already exist in the workspace.
        
        
        Args:
            data: Global data available as \{\{trigger.&lt;key&gt;\}\} in broadcast messages
            recipients: Filter object to define audience (overrides UI-defined recipients). Supports and/or/not/segment/attribute conditions.
            ids: List of profile IDs to target (max 10,000)
            emails: List of email addresses to target (max 10,000)
            per_user_data: Per-recipient custom data: [\{"id": "user1", "data": \{...\}\}, ...]
            data_file_url: URL to a JSON Lines file with per-user data
            id_ignore_missing: Ignore IDs that do not match existing profiles (default false)
            email_ignore_missing: Ignore emails that do not match existing profiles
            email_add_duplicates: Send to all profiles sharing an email address
            campaign_id: The broadcast campaign identifier (found in Triggering Details)
            **kwargs: Additional parameters
        
        Returns:
            BroadcastTriggerResponse

<a id="CampaignActionsQuery"></a>

`CampaignActionsQuery(connector: CustomerIoConnector)`
:   Query class for CampaignActions entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CampaignActionsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.customer_io.models.AirbyteSearchResult[CampaignActionsSearchData]`
    :   Search campaign_actions records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CampaignActionsSearchFilter):
        - bcc: BCC addresses
        - body: Action body content (HTML for emails)
        - campaign_id: Parent campaign ID
        - created: Creation timestamp (Unix)
        - deduplicate_id: Deduplication identifier
        - editor: Editor used to create the action
        - fake_bcc: Whether to use fake BCC
        - from_: From address
        - from_id: Sender identity ID
        - headers: Custom email headers as JSON
        - id: Unique action identifier
        - language: Language variant
        - layout: Layout template used
        - name: Action name
        - parent_action_id: Parent action ID for language variants
        - preheader_text: Email preheader/preview text
        - preprocessor: CSS preprocessor setting
        - recipient: Recipient address
        - recipient_environment_id: Recipient environment ID
        - reply_to: Reply-to address
        - reply_to_id: Reply-to sender identity ID
        - request_method: HTTP request method for webhook actions
        - sending_state: Sending behavior (automatic or draft)
        - subject: Email subject line
        - type_: Action type (email, webhook, twilio, push, slack, in_app, whatsapp)
        - updated: Last update timestamp (Unix)
        - url: Webhook URL (for webhook actions)
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CampaignActionsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, campaign_id: str, action_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.CampaignAction`
    :   Returns a single campaign action by ID.
        
        Args:
            campaign_id: The campaign identifier
            action_id: The action identifier
            **kwargs: Additional parameters
        
        Returns:
            CampaignAction

    `list(self, campaign_id: str, start: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResultWithMeta[list[CampaignAction], CampaignActionsListResultMeta]`
    :   Returns a paginated list of actions for a campaign.
        
        Args:
            campaign_id: The campaign identifier
            start: Pagination cursor for the next page
            **kwargs: Additional parameters
        
        Returns:
            CampaignActionsListResult

<a id="CampaignsQuery"></a>

`CampaignsQuery(connector: CustomerIoConnector)`
:   Query class for Campaigns entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CampaignsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.customer_io.models.AirbyteSearchResult[CampaignsSearchData]`
    :   Search campaigns records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CampaignsSearchFilter):
        - actions: Actions defined in this campaign
        - active: Whether the campaign is active
        - created: Creation timestamp (Unix)
        - created_by: Who created the campaign
        - date_attribute: Date attribute used for date-triggered campaigns
        - deduplicate_id: Deduplication identifier
        - event_name: Event name that triggers the campaign
        - first_started: When the campaign was first started (Unix)
        - frequency: How frequently a person can receive this campaign
        - id: Unique campaign identifier
        - msg_templates: Message templates used in the campaign
        - name: Campaign name
        - start_hour: Hour of the day to trigger
        - start_minutes: Minute of the hour to trigger
        - state: Campaign status (draft, active, stopped)
        - tags: Tags associated with the campaign
        - timezone: Timezone for trigger scheduling
        - trigger_segment_ids: Segment IDs that trigger this campaign
        - type_: Campaign trigger type
        - updated: Last update timestamp (Unix)
        - use_customer_timezone: Whether to use the customer's timezone
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CampaignsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, campaign_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.Campaign`
    :   Returns a single campaign by ID.
        
        Args:
            campaign_id: The campaign identifier
            **kwargs: Additional parameters
        
        Returns:
            Campaign

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult[list[Campaign]]`
    :   Returns a list of all campaigns in the workspace.
        
        Returns:
            CampaignsListResult

<a id="CollectionsQuery"></a>

`CollectionsQuery(connector: CustomerIoConnector)`
:   Query class for Collections entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, name: str, data: list[dict[str, Any]] | None = None, url: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Creates a new data collection with inline data or a URL source.
        
        Args:
            name: Collection name, referenced in Liquid as collection_name.property
            data: Inline collection data (array of objects). Provide either data or url, not both.
            url: URL to a CSV or JSON file containing collection data. Provide either data or url, not both.
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `get(self, collection_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.Collection`
    :   Returns a single collection by ID.
        
        Args:
            collection_id: The collection identifier
            **kwargs: Additional parameters
        
        Returns:
            Collection

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult[list[Collection]]`
    :   Returns all collections in the workspace.
        
        Returns:
            CollectionsListResult

    `update(self, collection_id: str, name: str | None = None, data: list[dict[str, Any]] | None = None, url: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Updates an existing collection's name, data, or URL source.
        
        Args:
            name: Rename the collection
            data: Replace collection data entirely (array of objects). Provide either data or url, not both.
            url: Replace the URL source for collection data. Provide either data or url, not both.
            collection_id: The collection identifier
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

<a id="CustomerIoConnector"></a>

`CustomerIoConnector(auth_config: CustomerIoAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Customer-Io API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new customer-io connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., CustomerIoAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = CustomerIoConnector(auth_config=CustomerIoAuthConfig(app_api_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = CustomerIoConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = CustomerIoConnector(
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

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000, framework: FrameworkName | None = None, internal_retries: int = 0, should_internal_retry: Callable[[Exception, tuple[Any, ...], dict[str, Any]], bool] | None = None, exhausted_runtime_failure_message: Callable[[Exception, tuple[Any, ...], dict[str, Any]], str | None] | None = None) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Composes :func:`airbyte_agent_sdk.translation.translate_exceptions` for
        runtime wrapping (sync/async branch + output-size check + framework
        signal translation + optional internal retry loop), and adds
        connector-specific docstring augmentation on top of it.
        
        Usage:
            @mcp.tool()
            @CustomerIoConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @CustomerIoConnector.tool_utils(update_docstring=False, max_output_chars=None)
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @CustomerIoConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
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

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.customer_io.models.CustomerIoCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            CustomerIoCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'get', 'create', 'update', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
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

<a id="ExportsQuery"></a>

`ExportsQuery(connector: CustomerIoConnector)`
:   Query class for Exports entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, filters: dict[str, Any], **kwargs) ‑> dict[str, typing.Any]`
    :   Triggers a new export of customer data. Use filters to select which customers to export.
        
        Args:
            filters: Audience filter conditions to select which customers to export. Uses boolean logic with "and", "or", "not" arrays of conditions, "segment" objects with an "id" field, and "attribute" objects with "field", "operator", and "value" fields. Example: \{"and": [\{"segment": \{"id": 3\}\}, \{"attribute": \{"field": "plan", "operator": "eq", "value": "premium"\}\}]\}
        
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `get(self, export_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.Export`
    :   Returns a single export by ID.
        
        Args:
            export_id: The export identifier
            **kwargs: Additional parameters
        
        Returns:
            Export

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult[list[Export]]`
    :   Returns all exports in the workspace.
        
        Returns:
            ExportsListResult

<a id="MessagesQuery"></a>

`MessagesQuery(connector: CustomerIoConnector)`
:   Query class for Messages entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, message_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.Message`
    :   Returns a single message delivery by ID. Untested because the test workspace has no message deliveries to retrieve.
        
        
        Args:
            message_id: The message delivery identifier
            **kwargs: Additional parameters
        
        Returns:
            Message

    `list(self, start: str | None = None, limit: int | None = None, type: str | None = None, metric: str | None = None, campaign_id: int | None = None, newsletter_id: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResultWithMeta[list[Message], MessagesListResultMeta]`
    :   Returns a paginated list of message deliveries.
        
        Args:
            start: Pagination cursor for the next page
            limit: Maximum number of messages to return
            type: Filter messages by channel type
            metric: Filter messages by delivery metric
            campaign_id: Filter by campaign ID
            newsletter_id: Filter by newsletter ID
            **kwargs: Additional parameters
        
        Returns:
            MessagesListResult

<a id="NewslettersQuery"></a>

`NewslettersQuery(connector: CustomerIoConnector)`
:   Query class for Newsletters entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: NewslettersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.customer_io.models.AirbyteSearchResult[NewslettersSearchData]`
    :   Search newsletters records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (NewslettersSearchFilter):
        - content_ids: Content variant IDs for this newsletter
        - created: Creation timestamp (Unix)
        - deduplicate_id: Deduplication identifier
        - id: Unique newsletter identifier
        - name: Newsletter name
        - sent_at: When the newsletter was last sent (Unix)
        - tags: Tags associated with the newsletter
        - type_: Channel type (email, webhook, twilio, push, in_app, inbox)
        - updated: Last update timestamp (Unix)
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            NewslettersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, newsletter_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.Newsletter`
    :   Returns a single newsletter by ID.
        
        Args:
            newsletter_id: The newsletter identifier
            **kwargs: Additional parameters
        
        Returns:
            Newsletter

    `list(self, start: str | None = None, limit: int | None = None, sort: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResultWithMeta[list[Newsletter], NewslettersListResultMeta]`
    :   Returns a paginated list of newsletters.
        
        Args:
            start: Pagination cursor for the next page
            limit: Maximum number of newsletters to return
            sort: Sort order
            **kwargs: Additional parameters
        
        Returns:
            NewslettersListResult

<a id="ReportingWebhooksQuery"></a>

`ReportingWebhooksQuery(connector: CustomerIoConnector)`
:   Query class for ReportingWebhooks entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, name: str, endpoint: str, events: list[str], disabled: bool | None = None, full_resolution: bool | None = None, with_content: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.ReportingWebhook`
    :   Creates a new reporting webhook to receive event notifications at the specified endpoint.
        
        Args:
            name: Webhook display name
            endpoint: The URL to receive webhook notifications
            events: Event types to report (e.g. customer_subscribed, email_sent, email_opened, email_clicked, email_bounced, email_converted, email_unsubscribed, sms_sent, sms_delivered, push_sent)
        
            disabled: Whether the webhook should be disabled initially
            full_resolution: Send all events instead of only unique events
            with_content: Include the message body in sent events
            **kwargs: Additional parameters
        
        Returns:
            ReportingWebhook

    `get(self, webhook_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.ReportingWebhook`
    :   Returns a single reporting webhook by ID.
        
        Args:
            webhook_id: The reporting webhook identifier
            **kwargs: Additional parameters
        
        Returns:
            ReportingWebhook

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult[list[ReportingWebhook]]`
    :   Returns all reporting webhooks in the workspace.
        
        Returns:
            ReportingWebhooksListResult

    `update(self, name: str, endpoint: str, events: list[str], webhook_id: str, disabled: bool | None = None, full_resolution: bool | None = None, with_content: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.ReportingWebhook`
    :   Updates an existing reporting webhook's configuration.
        
        Args:
            name: Webhook display name
            endpoint: The URL to receive webhook notifications
            events: Event types to report
            disabled: Whether the webhook is disabled
            full_resolution: Send all events instead of only unique events
            with_content: Include the message body in sent events
            webhook_id: The reporting webhook identifier
            **kwargs: Additional parameters
        
        Returns:
            ReportingWebhook

<a id="SegmentsQuery"></a>

`SegmentsQuery(connector: CustomerIoConnector)`
:   Query class for Segments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, segment: SegmentsCreateParamsSegment, **kwargs) ‑> dict[str, typing.Any]`
    :   Creates a new empty manual segment. People can be added to it separately.
        
        Args:
            segment: Parameter segment
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `get(self, segment_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.Segment`
    :   Returns a single segment by ID.
        
        Args:
            segment_id: The segment identifier
            **kwargs: Additional parameters
        
        Returns:
            Segment

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult[list[Segment]]`
    :   Returns all segments in the workspace.
        
        Returns:
            SegmentsListResult

<a id="SenderIdentitiesQuery"></a>

`SenderIdentitiesQuery(connector: CustomerIoConnector)`
:   Query class for SenderIdentities entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, sender_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.SenderIdentity`
    :   Returns a single sender identity by ID.
        
        Args:
            sender_id: The sender identity identifier
            **kwargs: Additional parameters
        
        Returns:
            SenderIdentity

    `list(self, start: str | None = None, limit: int | None = None, sort: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResultWithMeta[list[SenderIdentity], SenderIdentitiesListResultMeta]`
    :   Returns a paginated list of sender identities.
        
        Args:
            start: Pagination cursor for the next page
            limit: Maximum number of sender identities to return
            sort: Sort order
            **kwargs: Additional parameters
        
        Returns:
            SenderIdentitiesListResult

<a id="SnippetsQuery"></a>

`SnippetsQuery(connector: CustomerIoConnector)`
:   Query class for Snippets entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, name: str, value: str, **kwargs) ‑> dict[str, typing.Any]`
    :   Creates a new reusable content snippet. Returns 422 if a snippet with the same name already exists.
        
        Args:
            name: Unique snippet name (used as the liquid tag identifier)
            value: Snippet content (plain text, HTML, or Liquid)
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult[list[Snippet]]`
    :   Returns all snippets in the workspace.
        
        Returns:
            SnippetsListResult

    `update(self, name: str, value: str, **kwargs) ‑> dict[str, typing.Any]`
    :   Updates an existing snippet by name, or creates it if it does not exist (upsert behavior).
        
        Args:
            name: Snippet name to update (or create if it does not exist)
            value: New snippet content (plain text, HTML, or Liquid)
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

<a id="TransactionalEmailQuery"></a>

`TransactionalEmailQuery(connector: CustomerIoConnector)`
:   Query class for TransactionalEmail entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, to: str, identifiers: dict[str, Any], transactional_message_id: Any | None = None, message_data: dict[str, Any] | None = None, from_: str | None = None, subject: str | None = None, body: str | None = None, body_plain: str | None = None, reply_to: str | None = None, bcc: str | None = None, headers: dict[str, Any] | None = None, preheader_text: str | None = None, attachments: dict[str, Any] | None = None, disable_message_retention: bool | None = None, send_to_unsubscribed: bool | None = None, tracked: bool | None = None, queue_draft: bool | None = None, send_at: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.TransactionalSendResponse`
    :   Sends a transactional email to a single recipient. Can use a pre-built template (via transactional_message_id) or provide inline content (subject, body, from). Creates the recipient profile if it does not already exist.
        
        
        Args:
            transactional_message_id: Template ID (number) or trigger name (string). Required if not providing inline body/subject/from.
            to: Recipient email address. Supports display name format: "Name &lt;email&gt;"
            identifiers: Recipient identity. One of: \{"id": "..."\}, \{"email": "..."\}, or \{"cio_id": "..."\}
            message_data: Key-value pairs available as \{\{trigger.&lt;key&gt;\}\} in templates
            from_: Sender address (must be verified domain). Overrides template if provided.
            subject: Email subject line. Overrides template if provided.
            body: HTML email body. Overrides template if provided.
            body_plain: Plaintext email body
            reply_to: Reply-to email address
            bcc: BCC address(es), comma-separated. Max 15 total recipients.
            headers: Custom email headers (ASCII only)
            preheader_text: Email preview text
            attachments: Map of filename to base64 content: \{"file.pdf": "&lt;base64&gt;"\}. Max 2MB total.
            disable_message_retention: Do not store message body (for sensitive data)
            send_to_unsubscribed: Send even if person is unsubscribed
            tracked: Enable open and click tracking
            queue_draft: Queue as draft instead of sending immediately
            send_at: Unix timestamp for scheduled delivery (up to 90 days in the future)
            **kwargs: Additional parameters
        
        Returns:
            TransactionalSendResponse

<a id="TransactionalInboxMessageQuery"></a>

`TransactionalInboxMessageQuery(connector: CustomerIoConnector)`
:   Query class for TransactionalInboxMessage entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, transactional_message_id: Any, identifiers: dict[str, Any], message_data: dict[str, Any] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.TransactionalSendResponse`
    :   Sends a transactional in-app inbox message to a single recipient. Always requires a pre-built Inbox-type transactional message template (transactional_message_id). Messages appear in the recipient's notification inbox via the Customer.io SDK.
        
        
        Args:
            transactional_message_id: Template ID or trigger name. Must reference an Inbox-type transactional message.
            identifiers: Recipient identity. One of: \{"id": "..."\}, \{"email": "..."\}, or \{"cio_id": "..."\}
            message_data: Key-value pairs available as \{\{trigger.&lt;key&gt;\}\} in the inbox message template
            **kwargs: Additional parameters
        
        Returns:
            TransactionalSendResponse

<a id="TransactionalPushQuery"></a>

`TransactionalPushQuery(connector: CustomerIoConnector)`
:   Query class for TransactionalPush entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, identifiers: dict[str, Any], transactional_message_id: Any | None = None, to: str | None = None, message_data: dict[str, Any] | None = None, title: str | None = None, message: str | None = None, link: str | None = None, image_url: str | None = None, custom_data: dict[str, Any] | None = None, custom_payload: dict[str, Any] | None = None, sound: str | None = None, send_to_unsubscribed: bool | None = None, queue_draft: bool | None = None, disable_message_retention: bool | None = None, send_at: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.TransactionalSendResponse`
    :   Sends a transactional push notification to a single recipient. Can use a template or provide inline title and message. Requires push notifications to be configured in the workspace.
        
        
        Args:
            transactional_message_id: Template ID or trigger name. Required if not providing inline title/message.
            to: Device target: "last_used" for most recent device, or a specific device token. Defaults to all devices.
            identifiers: Recipient identity. One of: \{"id": "..."\}, \{"email": "..."\}, or \{"cio_id": "..."\}
            message_data: Key-value pairs available as \{\{trigger.&lt;key&gt;\}\} in templates
            title: Push notification title (overrides template)
            message: Push notification body (overrides template)
            link: Deep link URL
            image_url: Image URL to display in the notification
            custom_data: Custom key-value data included in the push payload
            custom_payload: Platform-specific payload overrides (iOS/Android)
            sound: Notification sound name
            send_to_unsubscribed: Send even if person is unsubscribed
            queue_draft: Queue as draft instead of sending immediately
            disable_message_retention: Do not store message content
            send_at: Unix timestamp for scheduled delivery
            **kwargs: Additional parameters
        
        Returns:
            TransactionalSendResponse

<a id="TransactionalSmsQuery"></a>

`TransactionalSmsQuery(connector: CustomerIoConnector)`
:   Query class for TransactionalSms entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, transactional_message_id: Any, to: str, identifiers: dict[str, Any], message_data: dict[str, Any] | None = None, from_: str | None = None, send_to_unsubscribed: bool | None = None, tracked: bool | None = None, queue_draft: bool | None = None, disable_message_retention: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.customer_io.models.TransactionalSendResponse`
    :   Sends a transactional SMS to a single recipient. Always requires a pre-built template (transactional_message_id). Requires Twilio integration to be configured in the workspace.
        
        
        Args:
            transactional_message_id: Template ID (number) or trigger name (string). Always required for SMS.
            to: Phone number in E.164 format (e.g. +15551234567)
            identifiers: Recipient identity. One of: \{"id": "..."\}, \{"email": "..."\}, or \{"cio_id": "..."\}
            message_data: Key-value pairs available as \{\{trigger.&lt;key&gt;\}\} in templates
            from_: Override sender phone number (must be verified in Twilio)
            send_to_unsubscribed: Send even if person is unsubscribed
            tracked: Enable link tracking
            queue_draft: Queue as draft instead of sending immediately
            disable_message_retention: Do not store message content
            **kwargs: Additional parameters
        
        Returns:
            TransactionalSendResponse