---
id: airbyte_agent_sdk-connectors-slack-index
title: airbyte_agent_sdk.connectors.slack.index
---

Module airbyte_agent_sdk.connectors.slack
=========================================
Slack connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.slack.connector
* airbyte_agent_sdk.connectors.slack.connector_model
* airbyte_agent_sdk.connectors.slack.models
* airbyte_agent_sdk.connectors.slack.types

Classes
-------

<a id="AirbyteAuthConfig"></a>

`AirbyteAuthConfig(**data: Any)`
:   Authentication configuration for Airbyte hosted mode execution.
    
    Pass this to the connector's `auth_config` parameter to use hosted mode,
    where API credentials are stored securely in Airbyte Cloud.
    
    For hosted mode execution, provide client credentials with either:
    - `connector_id`: Direct connector/source ID (skips lookup)
    - `workspace_name`: Workspace name for connector lookup
    
    Attributes:
        workspace_name: Workspace name for hosted mode connector lookup
        organization_id: Optional Airbyte organization ID for multi-org selection
        airbyte_client_id: Airbyte OAuth client ID (required for hosted mode)
        airbyte_client_secret: Airbyte OAuth client secret (required for hosted mode)
        connector_id: Specific connector/source ID (skips lookup if provided)
    
    Examples:
        # Hosted mode with connector_id (no lookup needed)
        connector = GongConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with workspace_name (lookup by workspace)
        connector = GongConnector(
            auth_config=AirbyteAuthConfig(
                workspace_name="user-123",
                organization_id="00000000-0000-0000-0000-000000000123",
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789"
            )
        )
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `airbyte_client_id: str | None`
    :   The type of the None singleton.

    `airbyte_client_secret: str | None`
    :   The type of the None singleton.

    `connector_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `organization_id: str | None`
    :   The type of the None singleton.

    `workspace_name: str | None`
    :   The type of the None singleton.

<a id="AirbyteSearchMeta"></a>

`AirbyteSearchMeta(**data: Any)`
:   Pagination metadata for search responses.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | None`
    :   Cursor for fetching the next page of results.

    `has_more: bool`
    :   Whether more results are available.

    `model_config`
    :   The type of the None singleton.

    `took_ms: int | None`
    :   Time taken to execute the search in milliseconds.

<a id="AirbyteSearchResult"></a>

`AirbyteSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.slack.models.AirbyteSearchResult[ChannelMessagesSearchData]
    * airbyte_agent_sdk.connectors.slack.models.AirbyteSearchResult[ChannelsSearchData]
    * airbyte_agent_sdk.connectors.slack.models.AirbyteSearchResult[ThreadsSearchData]
    * airbyte_agent_sdk.connectors.slack.models.AirbyteSearchResult[UsersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.slack.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="ChannelMessagesSearchResult"></a>

`ChannelMessagesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.slack.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ChannelsSearchResult"></a>

`ChannelsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.slack.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ThreadsSearchResult"></a>

`ThreadsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.slack.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="UsersSearchResult"></a>

`UsersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.slack.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ChannelMessagesSearchData"></a>

`ChannelMessagesSearchData(**data: Any)`
:   Search result data for channel_messages entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attachments: list[typing.Any] | None`
    :   Message attachments.

    `blocks: list[typing.Any] | None`
    :   Block kit blocks.

    `bot_id: str | None`
    :   Bot ID if message was sent by a bot.

    `bot_profile: dict[str, typing.Any] | None`
    :   Bot profile information.

    `is_locked: bool | None`
    :   Whether the thread is locked.

    `latest_reply: str | None`
    :   Timestamp of latest reply.

    `model_config`
    :   The type of the None singleton.

    `reactions: list[typing.Any] | None`
    :   Reactions to the message.

    `reply_count: int | None`
    :   Number of replies in thread.

    `reply_users: list[typing.Any] | None`
    :   User IDs who replied to the thread.

    `reply_users_count: int | None`
    :   Number of unique users who replied.

    `subscribed: bool | None`
    :   Whether the user is subscribed to the thread.

    `subtype: str | None`
    :   Message subtype.

    `team: str | None`
    :   Team ID.

    `text: str | None`
    :   Message text content.

    `thread_ts: str | None`
    :   Thread parent timestamp.

    `ts: str | None`
    :   Message timestamp (unique identifier).

    `type_: str | None`
    :   Message type.

    `user: str | None`
    :   User ID who sent the message.

<a id="ChannelsSearchData"></a>

`ChannelsSearchData(**data: Any)`
:   Search result data for channels entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `context_team_id: str | None`
    :   The unique identifier of the team context in which the channel exists.

    `created: int | None`
    :   The timestamp when the channel was created.

    `creator: str | None`
    :   The ID of the user who created the channel.

    `id: str | None`
    :   The unique identifier of the channel.

    `is_archived: bool | None`
    :   Indicates if the channel is archived.

    `is_channel: bool | None`
    :   Indicates if the entity is a channel.

    `is_ext_shared: bool | None`
    :   Indicates if the channel is externally shared.

    `is_general: bool | None`
    :   Indicates if the channel is a general channel in the workspace.

    `is_group: bool | None`
    :   Indicates if the channel is a group (private channel) rather than a regular channel.

    `is_im: bool | None`
    :   Indicates if the entity is a direct message (IM) channel.

    `is_member: bool | None`
    :   Indicates if the calling user is a member of the channel.

    `is_mpim: bool | None`
    :   Indicates if the entity is a multiple person direct message (MPIM) channel.

    `is_org_shared: bool | None`
    :   Indicates if the channel is organization-wide shared.

    `is_pending_ext_shared: bool | None`
    :   Indicates if the channel is pending external shared.

    `is_private: bool | None`
    :   Indicates if the channel is a private channel.

    `is_read_only: bool | None`
    :   Indicates if the channel is read-only.

    `is_shared: bool | None`
    :   Indicates if the channel is shared.

    `last_read: str | None`
    :   The timestamp of the user's last read message in the channel.

    `locale: str | None`
    :   The locale of the channel.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The name of the channel.

    `name_normalized: str | None`
    :   The normalized name of the channel.

    `num_members: int | None`
    :   The number of members in the channel.

    `parent_conversation: str | None`
    :   The parent conversation of the channel.

    `pending_connected_team_ids: list[typing.Any] | None`
    :   The IDs of teams that are pending to be connected to the channel.

    `pending_shared: list[typing.Any] | None`
    :   The list of pending shared items of the channel.

    `previous_names: list[typing.Any] | None`
    :   The previous names of the channel.

    `purpose: dict[str, typing.Any] | None`
    :   The purpose of the channel.

    `shared_team_ids: list[typing.Any] | None`
    :   The IDs of teams with which the channel is shared.

    `topic: dict[str, typing.Any] | None`
    :   The topic of the channel.

    `unlinked: int | None`
    :   Indicates if the channel is unlinked.

    `updated: int | None`
    :   The timestamp when the channel was last updated.

<a id="SlackConnector"></a>

`SlackConnector(auth_config: SlackAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Slack API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new slack connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., SlackAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = SlackConnector(auth_config=SlackAuthConfig(bot_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = SlackConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = SlackConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'SlackAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: "'SlackReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A SlackConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await SlackConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=SlackAuthConfig(bot_key="..."),
            )
        
            # With replication config (required for this connector):
            connector = await SlackConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=SlackAuthConfig(bot_key="..."),
                replication_config=SlackReplicationConfig(start_date="...", lookback_window="...", join_channels="..."),
            )
        
            # With server-side OAuth:
            connector = await SlackConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
                replication_config=SlackReplicationConfig(start_date="...", lookback_window="...", join_channels="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: "'SlackReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            consent_url = await SlackConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Slack Source",
                replication_config=SlackReplicationConfig(start_date="...", lookback_window="...", join_channels="..."),
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @SlackConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @SlackConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await SlackConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.slack.models.SlackCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            SlackCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="SlackReplicationConfig"></a>

`SlackReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Slack.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `join_channels: bool`
    :   Whether to automatically join public channels to sync messages.

    `lookback_window: int`
    :   Number of days to look back when syncing data (0-365).

    `model_config`
    :   The type of the None singleton.

    `start_date: str`
    :   UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ from which to start replicating data.

<a id="ThreadsSearchData"></a>

`ThreadsSearchData(**data: Any)`
:   Search result data for threads entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `blocks: list[typing.Any] | None`
    :   Block kit blocks.

    `bot_id: str | None`
    :   Bot ID if message was sent by a bot.

    `is_locked: bool | None`
    :   Whether the thread is locked.

    `latest_reply: str | None`
    :   Timestamp of latest reply.

    `model_config`
    :   The type of the None singleton.

    `parent_user_id: str | None`
    :   User ID of the parent message author (present in thread replies).

    `reply_count: int | None`
    :   Number of replies in thread.

    `reply_users: list[typing.Any] | None`
    :   User IDs who replied to the thread.

    `reply_users_count: int | None`
    :   Number of unique users who replied.

    `subscribed: bool | None`
    :   Whether the user is subscribed to the thread.

    `subtype: str | None`
    :   Message subtype.

    `team: str | None`
    :   Team ID.

    `text: str | None`
    :   Message text content.

    `thread_ts: str | None`
    :   Thread parent timestamp.

    `ts: str | None`
    :   Message timestamp (unique identifier).

    `type_: str | None`
    :   Message type.

    `user: str | None`
    :   User ID who sent the message.

<a id="UsersSearchData"></a>

`UsersSearchData(**data: Any)`
:   Search result data for users entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The color assigned to the user for visual purposes.

    `deleted: bool | None`
    :   Indicates if the user is deleted or not.

    `has_2fa: bool | None`
    :   Flag indicating if the user has two-factor authentication enabled.

    `id: str | None`
    :   Unique identifier for the user.

    `is_admin: bool | None`
    :   Flag specifying if the user is an admin or not.

    `is_app_user: bool | None`
    :   Specifies if the user is an app user.

    `is_bot: bool | None`
    :   Indicates if the user is a bot account.

    `is_email_confirmed: bool | None`
    :   Flag indicating if the user's email is confirmed.

    `is_forgotten: bool | None`
    :   Specifies if the user is marked as forgotten.

    `is_invited_user: bool | None`
    :   Indicates if the user is invited or not.

    `is_owner: bool | None`
    :   Flag indicating if the user is an owner.

    `is_primary_owner: bool | None`
    :   Specifies if the user is the primary owner.

    `is_restricted: bool | None`
    :   Flag specifying if the user is restricted.

    `is_ultra_restricted: bool | None`
    :   Indicates if the user has ultra-restricted access.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The username of the user.

    `profile: dict[str, typing.Any] | None`
    :   User's profile information containing detailed details.

    `real_name: str | None`
    :   The real name of the user.

    `team_id: str | None`
    :   Unique identifier for the team the user belongs to.

    `tz: str | None`
    :   Timezone of the user.

    `tz_label: str | None`
    :   Label representing the timezone of the user.

    `tz_offset: int | None`
    :   Offset of the user's timezone.

    `updated: int | None`
    :   Timestamp of when the user's information was last updated.

    `who_can_share_contact_card: str | None`
    :   Specifies who can share the user's contact card.