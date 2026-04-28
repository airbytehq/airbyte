---
id: airbyte_agent_sdk-connectors-slack-connector
title: airbyte_agent_sdk.connectors.slack.connector
---

Module airbyte_agent_sdk.connectors.slack.connector
===================================================
Slack connector.

Classes
-------

<a id="ChannelInvitesQuery"></a>

`ChannelInvitesQuery(connector: SlackConnector)`
:   Query class for ChannelInvites entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, channel: str, users: str, force: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.slack.models.Channel`
    :   Invites one or more users to a public or private channel
        
        Args:
            channel: The ID of the public or private channel to invite user(s) to
            users: A comma separated list of user IDs. Up to 1000 users may be listed.
            force: When set to true and multiple user IDs are provided, continue inviting the valid ones while disregarding invalid IDs. Defaults to false.
            **kwargs: Additional parameters
        
        Returns:
            Channel

<a id="ChannelMessagesQuery"></a>

`ChannelMessagesQuery(connector: SlackConnector)`
:   Query class for ChannelMessages entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ChannelMessagesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.slack.models.AirbyteSearchResult[ChannelMessagesSearchData]`
    :   Search channel_messages records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ChannelMessagesSearchFilter):
        - type_: Message type.
        - subtype: Message subtype.
        - ts: Message timestamp (unique identifier).
        - user: User ID who sent the message.
        - text: Message text content.
        - thread_ts: Thread parent timestamp.
        - reply_count: Number of replies in thread.
        - reply_users_count: Number of unique users who replied.
        - latest_reply: Timestamp of latest reply.
        - reply_users: User IDs who replied to the thread.
        - is_locked: Whether the thread is locked.
        - subscribed: Whether the user is subscribed to the thread.
        - reactions: Reactions to the message.
        - attachments: Message attachments.
        - blocks: Block kit blocks.
        - bot_id: Bot ID if message was sent by a bot.
        - bot_profile: Bot profile information.
        - team: Team ID.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ChannelMessagesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, channel: str, cursor: str | None = None, limit: int | None = None, oldest: str | None = None, latest: str | None = None, inclusive: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.slack.models.SlackExecuteResultWithMeta[list[Message], ChannelMessagesListResultMeta]`
    :   Returns messages from a channel
        
        Args:
            channel: Channel ID to get messages from
            cursor: Pagination cursor for next page
            limit: Number of messages to return per page
            oldest: Start of time range (Unix timestamp)
            latest: End of time range (Unix timestamp)
            inclusive: Include messages with oldest or latest timestamps
            **kwargs: Additional parameters
        
        Returns:
            ChannelMessagesListResult

<a id="ChannelPurposesQuery"></a>

`ChannelPurposesQuery(connector: SlackConnector)`
:   Query class for ChannelPurposes entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, channel: str, purpose: str, **kwargs) ‑> airbyte_agent_sdk.connectors.slack.models.Channel`
    :   Sets the purpose for a channel
        
        Args:
            channel: Channel ID to set purpose for
            purpose: New purpose text (max 250 characters)
            **kwargs: Additional parameters
        
        Returns:
            Channel

<a id="ChannelTopicsQuery"></a>

`ChannelTopicsQuery(connector: SlackConnector)`
:   Query class for ChannelTopics entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, channel: str, topic: str, **kwargs) ‑> airbyte_agent_sdk.connectors.slack.models.Channel`
    :   Sets the topic for a channel
        
        Args:
            channel: Channel ID to set topic for
            topic: New topic text (max 250 characters)
            **kwargs: Additional parameters
        
        Returns:
            Channel

<a id="ChannelsQuery"></a>

`ChannelsQuery(connector: SlackConnector)`
:   Query class for Channels entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ChannelsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.slack.models.AirbyteSearchResult[ChannelsSearchData]`
    :   Search channels records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ChannelsSearchFilter):
        - context_team_id: The unique identifier of the team context in which the channel exists.
        - created: The timestamp when the channel was created.
        - creator: The ID of the user who created the channel.
        - id: The unique identifier of the channel.
        - is_archived: Indicates if the channel is archived.
        - is_channel: Indicates if the entity is a channel.
        - is_ext_shared: Indicates if the channel is externally shared.
        - is_general: Indicates if the channel is a general channel in the workspace.
        - is_group: Indicates if the channel is a group (private channel) rather than a regular channel.
        - is_im: Indicates if the entity is a direct message (IM) channel.
        - is_member: Indicates if the calling user is a member of the channel.
        - is_mpim: Indicates if the entity is a multiple person direct message (MPIM) channel.
        - is_org_shared: Indicates if the channel is organization-wide shared.
        - is_pending_ext_shared: Indicates if the channel is pending external shared.
        - is_private: Indicates if the channel is a private channel.
        - is_read_only: Indicates if the channel is read-only.
        - is_shared: Indicates if the channel is shared.
        - last_read: The timestamp of the user's last read message in the channel.
        - locale: The locale of the channel.
        - name: The name of the channel.
        - name_normalized: The normalized name of the channel.
        - num_members: The number of members in the channel.
        - parent_conversation: The parent conversation of the channel.
        - pending_connected_team_ids: The IDs of teams that are pending to be connected to the channel.
        - pending_shared: The list of pending shared items of the channel.
        - previous_names: The previous names of the channel.
        - purpose: The purpose of the channel.
        - shared_team_ids: The IDs of teams with which the channel is shared.
        - topic: The topic of the channel.
        - unlinked: Indicates if the channel is unlinked.
        - updated: The timestamp when the channel was last updated.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ChannelsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, name: str, is_private: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.slack.models.Channel`
    :   Creates a new public or private channel
        
        Args:
            name: Channel name (lowercase, no spaces, max 80 chars)
            is_private: Create a private channel instead of public
            **kwargs: Additional parameters
        
        Returns:
            Channel

    `get(self, channel: str, **kwargs) ‑> airbyte_agent_sdk.connectors.slack.models.Channel`
    :   Get information about a single channel by ID
        
        Args:
            channel: Channel ID
            **kwargs: Additional parameters
        
        Returns:
            Channel

    `list(self, cursor: str | None = None, limit: int | None = None, types: str | None = None, exclude_archived: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.slack.models.SlackExecuteResultWithMeta[list[Channel], ChannelsListResultMeta]`
    :   Returns a list of all channels in the Slack workspace
        
        Args:
            cursor: Pagination cursor for next page
            limit: Number of channels to return per page
            types: Mix and match channel types (public_channel, private_channel, mpim, im)
            exclude_archived: Exclude archived channels
            **kwargs: Additional parameters
        
        Returns:
            ChannelsListResult

    `update(self, channel: str, name: str, **kwargs) ‑> airbyte_agent_sdk.connectors.slack.models.Channel`
    :   Renames an existing channel
        
        Args:
            channel: Channel ID to rename
            name: New channel name (lowercase, no spaces, max 80 chars)
            **kwargs: Additional parameters
        
        Returns:
            Channel

<a id="MessagesQuery"></a>

`MessagesQuery(connector: SlackConnector)`
:   Query class for Messages entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, channel: str, text: str, thread_ts: str | None = None, reply_broadcast: bool | None = None, unfurl_links: bool | None = None, unfurl_media: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.slack.models.CreatedMessage`
    :   Posts a message to a public channel, private channel, or direct message conversation
        
        Args:
            channel: Channel ID, private group ID, or user ID to send message to
            text: Message text content (supports mrkdwn formatting)
            thread_ts: Thread timestamp to reply to (for threaded messages)
            reply_broadcast: Also post reply to channel when replying to a thread
            unfurl_links: Enable unfurling of primarily text-based content
            unfurl_media: Enable unfurling of media content
            **kwargs: Additional parameters
        
        Returns:
            CreatedMessage

    `update(self, channel: str, ts: str, text: str, **kwargs) ‑> airbyte_agent_sdk.connectors.slack.models.CreatedMessage`
    :   Updates an existing message in a channel
        
        Args:
            channel: Channel ID containing the message
            ts: Timestamp of the message to update
            text: New message text content
            **kwargs: Additional parameters
        
        Returns:
            CreatedMessage

<a id="ReactionsQuery"></a>

`ReactionsQuery(connector: SlackConnector)`
:   Query class for Reactions entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, channel: str, timestamp: str, name: str, **kwargs) ‑> airbyte_agent_sdk.connectors.slack.models.ReactionAddResponse`
    :   Adds a reaction (emoji) to a message
        
        Args:
            channel: Channel ID containing the message
            timestamp: Timestamp of the message to react to
            name: Reaction emoji name (without colons, e.g., "thumbsup")
            **kwargs: Additional parameters
        
        Returns:
            ReactionAddResponse

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

<a id="ThreadsQuery"></a>

`ThreadsQuery(connector: SlackConnector)`
:   Query class for Threads entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ThreadsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.slack.models.AirbyteSearchResult[ThreadsSearchData]`
    :   Search threads records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ThreadsSearchFilter):
        - type_: Message type.
        - subtype: Message subtype.
        - ts: Message timestamp (unique identifier).
        - user: User ID who sent the message.
        - text: Message text content.
        - thread_ts: Thread parent timestamp.
        - parent_user_id: User ID of the parent message author (present in thread replies).
        - reply_count: Number of replies in thread.
        - reply_users_count: Number of unique users who replied.
        - latest_reply: Timestamp of latest reply.
        - reply_users: User IDs who replied to the thread.
        - is_locked: Whether the thread is locked.
        - subscribed: Whether the user is subscribed to the thread.
        - blocks: Block kit blocks.
        - bot_id: Bot ID if message was sent by a bot.
        - team: Team ID.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ThreadsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, channel: str, ts: str | None = None, cursor: str | None = None, limit: int | None = None, oldest: str | None = None, latest: str | None = None, inclusive: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.slack.models.SlackExecuteResultWithMeta[list[Thread], ThreadsListResultMeta]`
    :   Returns messages in a thread (thread replies from conversations.replies endpoint)
        
        Args:
            channel: Channel ID containing the thread
            ts: Timestamp of the parent message (required for thread replies)
            cursor: Pagination cursor for next page
            limit: Number of replies to return per page
            oldest: Start of time range (Unix timestamp)
            latest: End of time range (Unix timestamp)
            inclusive: Include messages with oldest or latest timestamps
            **kwargs: Additional parameters
        
        Returns:
            ThreadsListResult

<a id="UsersQuery"></a>

`UsersQuery(connector: SlackConnector)`
:   Query class for Users entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: UsersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.slack.models.AirbyteSearchResult[UsersSearchData]`
    :   Search users records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (UsersSearchFilter):
        - color: The color assigned to the user for visual purposes.
        - deleted: Indicates if the user is deleted or not.
        - has_2fa: Flag indicating if the user has two-factor authentication enabled.
        - id: Unique identifier for the user.
        - is_admin: Flag specifying if the user is an admin or not.
        - is_app_user: Specifies if the user is an app user.
        - is_bot: Indicates if the user is a bot account.
        - is_email_confirmed: Flag indicating if the user's email is confirmed.
        - is_forgotten: Specifies if the user is marked as forgotten.
        - is_invited_user: Indicates if the user is invited or not.
        - is_owner: Flag indicating if the user is an owner.
        - is_primary_owner: Specifies if the user is the primary owner.
        - is_restricted: Flag specifying if the user is restricted.
        - is_ultra_restricted: Indicates if the user has ultra-restricted access.
        - name: The username of the user.
        - profile: User's profile information containing detailed details.
        - real_name: The real name of the user.
        - team_id: Unique identifier for the team the user belongs to.
        - tz: Timezone of the user.
        - tz_label: Label representing the timezone of the user.
        - tz_offset: Offset of the user's timezone.
        - updated: Timestamp of when the user's information was last updated.
        - who_can_share_contact_card: Specifies who can share the user's contact card.
        
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

    `get(self, user: str, **kwargs) ‑> airbyte_agent_sdk.connectors.slack.models.User`
    :   Get information about a single user by ID
        
        Args:
            user: User ID
            **kwargs: Additional parameters
        
        Returns:
            User

    `list(self, cursor: str | None = None, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.slack.models.SlackExecuteResultWithMeta[list[User], UsersListResultMeta]`
    :   Returns a list of all users in the Slack workspace
        
        Args:
            cursor: Pagination cursor for next page
            limit: Number of users to return per page
            **kwargs: Additional parameters
        
        Returns:
            UsersListResult