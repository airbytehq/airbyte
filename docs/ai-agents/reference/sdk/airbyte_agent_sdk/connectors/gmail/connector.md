---
id: airbyte_agent_sdk-connectors-gmail-connector
title: airbyte_agent_sdk.connectors.gmail.connector
---

Module airbyte_agent_sdk.connectors.gmail.connector
===================================================
Gmail connector.

Classes
-------

<a id="DraftsQuery"></a>

`DraftsQuery(connector: GmailConnector)`
:   Query class for Drafts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, message: DraftsCreateParamsMessage, **kwargs) ‑> airbyte_agent_sdk.connectors.gmail.models.Draft`
    :   Creates a new draft with the specified message content
        
        Args:
            message: The draft message content
            **kwargs: Additional parameters
        
        Returns:
            Draft

    `delete(self, draft_id: str, **kwargs) ‑> dict[str, typing.Any]`
    :   Immediately and permanently deletes the specified draft (does not move to trash)
        
        Args:
            draft_id: The ID of the draft to delete
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `get(self, draft_id: str, format: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gmail.models.Draft`
    :   Gets the specified draft including its message content
        
        Args:
            draft_id: The ID of the draft to retrieve
            format: The format to return the draft message in (full, metadata, minimal, raw)
            **kwargs: Additional parameters
        
        Returns:
            Draft

    `list(self, max_results: int | None = None, page_token: str | None = None, q: str | None = None, include_spam_trash: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gmail.models.GmailExecuteResultWithMeta[list[DraftRef], DraftsListResultMeta]`
    :   Lists the drafts in the user's mailbox
        
        Args:
            max_results: Maximum number of drafts to return (1-500)
            page_token: Page token to retrieve a specific page of results
            q: Gmail search query to filter drafts
            include_spam_trash: Include drafts from SPAM and TRASH in the results
            **kwargs: Additional parameters
        
        Returns:
            DraftsListResult

    `update(self, message: DraftsUpdateParamsMessage, draft_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.gmail.models.Draft`
    :   Replaces a draft's content with the specified message content
        
        Args:
            message: The draft message content
            draft_id: The ID of the draft to update
            **kwargs: Additional parameters
        
        Returns:
            Draft

<a id="DraftsSendQuery"></a>

`DraftsSendQuery(connector: GmailConnector)`
:   Query class for DraftsSend entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gmail.models.Message`
    :   Sends the specified existing draft to its recipients
        
        Args:
            id: The ID of the draft to send
            **kwargs: Additional parameters
        
        Returns:
            Message

<a id="GmailConnector"></a>

`GmailConnector(auth_config: GmailAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Gmail API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new gmail connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., GmailAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = GmailConnector(auth_config=GmailAuthConfig(access_token="...", refresh_token="...", client_id="...", client_secret="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = GmailConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = GmailConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'GmailAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: "'GmailReplicationConfig' | None" = None, source_template_id: str | None = None)`
    :   Create a new hosted connector on Airbyte Cloud.
        
        This factory method:
        1. Creates a source on Airbyte Cloud with the provided credentials
        2. Returns a connector configured with the new connector_id
        
        Supports two authentication modes:
        1. Direct credentials: Provide `auth_config` with typed credentials
        2. Server-side OAuth: Provide `server_side_oauth_secret_id` from OAuth flow
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials and workspace_name.
                Optionally include organization_id for multi-org request routing.
            auth_config: Typed auth config. Required unless using server_side_oauth_secret_id.
            server_side_oauth_secret_id: OAuth secret ID from get_consent_url redirect.
                When provided, auth_config is not required.
            name: Optional source name (defaults to connector name + workspace_name)
            replication_config: Typed replication settings.
                Required for connectors with x-airbyte-replication-config (REPLICATION mode sources).
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            A GmailConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await GmailConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=GmailAuthConfig(access_token="...", refresh_token="...", client_id="...", client_secret="..."),
            )
        
            # With replication config (required for this connector):
            connector = await GmailConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=GmailAuthConfig(access_token="...", refresh_token="...", client_id="...", client_secret="..."),
                replication_config=GmailReplicationConfig(include_spam_and_trash="..."),
            )
        
            # With server-side OAuth:
            connector = await GmailConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
                replication_config=GmailReplicationConfig(include_spam_and_trash="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: "'GmailReplicationConfig' | None" = None, source_template_id: str | None = None)`
    :   Initiate server-side OAuth flow with auto-source creation.
        
        Returns a consent URL where the end user should be redirected to grant access.
        After completing consent, the source is automatically created and the user is
        redirected to your redirect_url with a `connector_id` query parameter.
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials and workspace_name.
                Optionally include organization_id for multi-org request routing.
            redirect_url: URL where users will be redirected after OAuth consent.
                After consent, user arrives at: redirect_url?connector_id=...
            name: Optional name for the source. Defaults to connector name + workspace_name.
            replication_config: Typed replication settings. Merged with OAuth credentials.
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            The OAuth consent URL
        
        Example:
            consent_url = await GmailConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Gmail Source",
                replication_config=GmailReplicationConfig(include_spam_and_trash="..."),
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @GmailConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @GmailConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await GmailConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.gmail.models.GmailCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            GmailCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['get', 'list', 'create', 'update', 'delete']", params: Mapping[str, Any] | None = None) ‑> Any`
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

<a id="LabelsQuery"></a>

`LabelsQuery(connector: GmailConnector)`
:   Query class for Labels entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, name: str, message_list_visibility: str | None = None, label_list_visibility: str | None = None, color: LabelsCreateParamsColor | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gmail.models.Label`
    :   Creates a new label in the user's mailbox
        
        Args:
            name: The display name of the label
            message_list_visibility: The visibility of messages with this label in the message list (show or hide)
            label_list_visibility: The visibility of the label in the label list
            color: The color to assign to the label
            **kwargs: Additional parameters
        
        Returns:
            Label

    `delete(self, label_id: str, **kwargs) ‑> dict[str, typing.Any]`
    :   Deletes the specified label and removes it from any messages and threads
        
        Args:
            label_id: The ID of the label to delete
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `get(self, label_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.gmail.models.Label`
    :   Gets a specific label by ID including message and thread counts
        
        Args:
            label_id: The ID of the label to retrieve
            **kwargs: Additional parameters
        
        Returns:
            Label

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.gmail.models.GmailExecuteResult[list[Label]]`
    :   Lists all labels in the user's mailbox including system and user-created labels
        
        Returns:
            LabelsListResult

    `update(self, label_id: str, id: str | None = None, name: str | None = None, message_list_visibility: str | None = None, label_list_visibility: str | None = None, color: LabelsUpdateParamsColor | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gmail.models.Label`
    :   Updates the specified label
        
        Args:
            id: The ID of the label (must match the path parameter)
            name: The new display name of the label
            message_list_visibility: The visibility of messages with this label in the message list
            label_list_visibility: The visibility of the label in the label list
            color: The color to assign to the label
            label_id: The ID of the label to update
            **kwargs: Additional parameters
        
        Returns:
            Label

<a id="MessagesQuery"></a>

`MessagesQuery(connector: GmailConnector)`
:   Query class for Messages entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, raw: str, thread_id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gmail.models.Message`
    :   Sends a new email message. The message should be provided as a base64url-encoded
        RFC 2822 formatted string in the 'raw' field.
        
        
                Args:
                    raw: The entire email message in RFC 2822 format, base64url encoded
                    thread_id: The thread ID to reply to (for threading replies in a conversation)
                    **kwargs: Additional parameters
        
                Returns:
                    Message

    `get(self, message_id: str, format: str | None = None, metadata_headers: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gmail.models.Message`
    :   Gets the full email message content including headers, body, and attachments metadata
        
        Args:
            message_id: The ID of the message to retrieve
            format: The format to return the message in (full, metadata, minimal, raw)
            metadata_headers: When format is METADATA, only include headers specified (comma-separated)
            **kwargs: Additional parameters
        
        Returns:
            Message

    `list(self, max_results: int | None = None, page_token: str | None = None, q: str | None = None, label_ids: str | None = None, include_spam_trash: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gmail.models.GmailExecuteResultWithMeta[list[MessageRef], MessagesListResultMeta]`
    :   Lists the messages in the user's mailbox. Returns message IDs and thread IDs.
        
        Args:
            max_results: Maximum number of messages to return (1-500)
            page_token: Page token to retrieve a specific page of results
            q: Gmail search query (same format as Gmail search box, e.g. "from:user@example.com", "is:unread", "subject:hello")
            label_ids: Only return messages with labels matching all of the specified label IDs (comma-separated)
            include_spam_trash: Include messages from SPAM and TRASH in the results
            **kwargs: Additional parameters
        
        Returns:
            MessagesListResult

    `update(self, message_id: str, add_label_ids: list[str] | None = None, remove_label_ids: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gmail.models.Message`
    :   Modifies the labels on a message. Use this to archive (remove INBOX label),
        mark as read (remove UNREAD label), mark as unread (add UNREAD label),
        star (add STARRED label), or apply custom labels.
        
        
                Args:
                    add_label_ids: A list of label IDs to add to the message (e.g. STARRED, UNREAD, or custom label IDs)
                    remove_label_ids: A list of label IDs to remove from the message (e.g. INBOX to archive, UNREAD to mark as read)
                    message_id: The ID of the message to modify
                    **kwargs: Additional parameters
        
                Returns:
                    Message

<a id="MessagesTrashQuery"></a>

`MessagesTrashQuery(connector: GmailConnector)`
:   Query class for MessagesTrash entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, message_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.gmail.models.Message`
    :   Moves the specified message to the trash
        
        Args:
            message_id: The ID of the message to trash
            **kwargs: Additional parameters
        
        Returns:
            Message

<a id="MessagesUntrashQuery"></a>

`MessagesUntrashQuery(connector: GmailConnector)`
:   Query class for MessagesUntrash entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, message_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.gmail.models.Message`
    :   Removes the specified message from the trash
        
        Args:
            message_id: The ID of the message to untrash
            **kwargs: Additional parameters
        
        Returns:
            Message

<a id="ProfileQuery"></a>

`ProfileQuery(connector: GmailConnector)`
:   Query class for Profile entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, **kwargs) ‑> airbyte_agent_sdk.connectors.gmail.models.Profile`
    :   Gets the current user's Gmail profile including email address and mailbox statistics
        
        Returns:
            Profile

<a id="ThreadsQuery"></a>

`ThreadsQuery(connector: GmailConnector)`
:   Query class for Threads entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, thread_id: str, format: str | None = None, metadata_headers: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gmail.models.Thread`
    :   Gets the specified thread including all messages in the conversation
        
        Args:
            thread_id: The ID of the thread to retrieve
            format: The format to return the messages in (full, metadata, minimal)
            metadata_headers: When format is METADATA, only include headers specified (comma-separated)
            **kwargs: Additional parameters
        
        Returns:
            Thread

    `list(self, max_results: int | None = None, page_token: str | None = None, q: str | None = None, label_ids: str | None = None, include_spam_trash: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gmail.models.GmailExecuteResultWithMeta[list[ThreadRef], ThreadsListResultMeta]`
    :   Lists the threads in the user's mailbox
        
        Args:
            max_results: Maximum number of threads to return (1-500)
            page_token: Page token to retrieve a specific page of results
            q: Gmail search query to filter threads
            label_ids: Only return threads with labels matching all of the specified label IDs (comma-separated)
            include_spam_trash: Include threads from SPAM and TRASH in the results
            **kwargs: Additional parameters
        
        Returns:
            ThreadsListResult