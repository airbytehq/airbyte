---
id: airbyte_agent_sdk-connectors-gong-index
title: airbyte_agent_sdk.connectors.gong.index
---

Module airbyte_agent_sdk.connectors.gong
========================================
Gong connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.gong.connector
* airbyte_agent_sdk.connectors.gong.connector_model
* airbyte_agent_sdk.connectors.gong.models
* airbyte_agent_sdk.connectors.gong.types

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

    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult[CallsExtensiveSearchData]
    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult[CallsSearchData]
    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult[SettingsScorecardsSearchData]
    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult[StatsActivityScorecardsSearchData]
    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult[UsersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.gong.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="CallsExtensiveSearchResult"></a>

`CallsExtensiveSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CallsSearchResult"></a>

`CallsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SettingsScorecardsSearchResult"></a>

`SettingsScorecardsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="StatsActivityScorecardsSearchResult"></a>

`StatsActivityScorecardsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CallsExtensiveSearchData"></a>

`CallsExtensiveSearchData(**data: Any)`
:   Search result data for calls_extensive entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `collaboration: dict[str, typing.Any] | None`
    :   Collaboration information added to the call

    `content: dict[str, typing.Any] | None`
    :   Analysis of the interaction content.

    `context: dict[str, typing.Any] | None`
    :   A list of the agenda of each part of the call.

    `id: int | None`
    :   Unique identifier for the call (from metaData.id).

    `interaction: dict[str, typing.Any] | None`
    :   Metrics collected around the interaction during the call.

    `media: dict[str, typing.Any] | None`
    :   The media urls of the call.

    `meta_data: dict[str, typing.Any] | None`
    :   call's metadata.

    `model_config`
    :   The type of the None singleton.

    `parties: list[typing.Any] | None`
    :   A list of the call's participants

    `startdatetime: str | None`
    :   Datetime for extensive calls.

<a id="CallsSearchData"></a>

`CallsSearchData(**data: Any)`
:   Search result data for calls entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `calendar_event_id: str | None`
    :   Unique identifier for the calendar event associated with the call.

    `client_unique_id: str | None`
    :   Unique identifier for the client related to the call.

    `custom_data: str | None`
    :   Custom data associated with the call.

    `direction: str | None`
    :   Direction of the call (inbound/outbound).

    `duration: int | None`
    :   Duration of the call in seconds.

    `id: str | None`
    :   Unique identifier for the call.

    `is_private: bool | None`
    :   Indicates if the call is private or not.

    `language: str | None`
    :   Language used in the call.

    `media: str | None`
    :   Media type used for communication (voice, video, etc.).

    `meeting_url: str | None`
    :   URL for accessing the meeting associated with the call.

    `model_config`
    :   The type of the None singleton.

    `primary_user_id: str | None`
    :   Unique identifier for the primary user involved in the call.

    `purpose: str | None`
    :   Purpose or topic of the call.

    `scheduled: str | None`
    :   Scheduled date and time of the call.

    `scope: str | None`
    :   Scope or extent of the call.

    `sdr_disposition: str | None`
    :   Disposition set by the sales development representative.

    `started: str | None`
    :   Start date and time of the call.

    `system: str | None`
    :   System information related to the call.

    `title: str | None`
    :   Title or headline of the call.

    `url: str | None`
    :   URL associated with the call.

    `workspace_id: str | None`
    :   Identifier for the workspace to which the call belongs.

<a id="GongConnector"></a>

`GongConnector(auth_config: GongAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Gong API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new gong connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., GongAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = GongConnector(auth_config=GongAuthConfig(access_token="...", refresh_token="...", client_id="...", client_secret="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = GongConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = GongConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'GongAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None)`
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
            replication_config: Optional replication settings dict.
                Required for connectors with x-airbyte-replication-config (REPLICATION mode sources).
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            A GongConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await GongConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=GongAuthConfig(access_token="...", refresh_token="...", client_id="...", client_secret="..."),
            )
        
            # With server-side OAuth:
            connector = await GongConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None) ‑> str`
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
            replication_config: Optional replication settings dict. Merged with OAuth credentials.
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            The OAuth consent URL
        
        Example:
            consent_url = await GongConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Gong Source",
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @GongConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @GongConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await GongConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.gong.models.GongCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            GongCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'get', 'download', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
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

<a id="SettingsScorecardsSearchData"></a>

`SettingsScorecardsSearchData(**data: Any)`
:   Search result data for settings_scorecards entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: str | None`
    :   The timestamp when the scorecard was created

    `enabled: bool | None`
    :   Indicates if the scorecard is enabled or disabled

    `model_config`
    :   The type of the None singleton.

    `questions: list[typing.Any] | None`
    :   An array of questions related to the scorecard

    `scorecard_id: str | None`
    :   The unique identifier of the scorecard

    `scorecard_name: str | None`
    :   The name of the scorecard

    `updated: str | None`
    :   The timestamp when the scorecard was last updated

    `updater_user_id: str | None`
    :   The user ID of the person who last updated the scorecard

    `workspace_id: str | None`
    :   The unique identifier of the workspace associated with the scorecard

<a id="StatsActivityScorecardsSearchData"></a>

`StatsActivityScorecardsSearchData(**data: Any)`
:   Search result data for stats_activity_scorecards entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `answered_scorecard_id: str | None`
    :   Unique identifier for the answered scorecard instance.

    `answers: list[typing.Any] | None`
    :   Contains the answered questions in the scorecards

    `call_id: str | None`
    :   Unique identifier for the call associated with the answered scorecard.

    `call_start_time: str | None`
    :   Timestamp indicating the start time of the call.

    `model_config`
    :   The type of the None singleton.

    `review_time: str | None`
    :   Timestamp indicating when the review of the answered scorecard was completed.

    `reviewed_user_id: str | None`
    :   Unique identifier for the user whose performance was reviewed.

    `reviewer_user_id: str | None`
    :   Unique identifier for the user who performed the review.

    `scorecard_id: str | None`
    :   Unique identifier for the scorecard template used.

    `scorecard_name: str | None`
    :   Name or title of the scorecard template used.

    `visibility_type: str | None`
    :   Type indicating the visibility permissions for the answered scorecard.

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

    `active: bool | None`
    :   Indicates if the user is currently active or not

    `created: str | None`
    :   The timestamp denoting when the user account was created

    `email_address: str | None`
    :   The primary email address associated with the user

    `email_aliases: list[typing.Any] | None`
    :   Additional email addresses that can be used to reach the user

    `extension: str | None`
    :   The phone extension number for the user

    `first_name: str | None`
    :   The first name of the user

    `id: str | None`
    :   Unique identifier for the user

    `last_name: str | None`
    :   The last name of the user

    `manager_id: str | None`
    :   The ID of the user's manager

    `meeting_consent_page_url: str | None`
    :   URL for the consent page related to meetings

    `model_config`
    :   The type of the None singleton.

    `personal_meeting_urls: list[typing.Any] | None`
    :   URLs for personal meeting rooms assigned to the user

    `phone_number: str | None`
    :   The phone number associated with the user

    `settings: dict[str, typing.Any] | None`
    :   User-specific settings and configurations

    `spoken_languages: list[typing.Any] | None`
    :   Languages spoken by the user

    `title: str | None`
    :   The job title or position of the user

    `trusted_email_address: str | None`
    :   An email address that is considered trusted for the user