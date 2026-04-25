---
id: airbyte_agent_sdk-connectors-amplitude-index
title: airbyte_agent_sdk.connectors.amplitude.index
---

Module airbyte_agent_sdk.connectors.amplitude
=============================================
Amplitude connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.amplitude.connector
* airbyte_agent_sdk.connectors.amplitude.connector_model
* airbyte_agent_sdk.connectors.amplitude.models
* airbyte_agent_sdk.connectors.amplitude.types

Classes
-------

<a id="ActiveUsersSearchData"></a>

`ActiveUsersSearchData(**data: Any)`
:   Search result data for active_users entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `date: str | None`
    :   The date for which the active user data is reported

    `model_config`
    :   The type of the None singleton.

    `statistics: dict[str, typing.Any] | None`
    :   The statistics related to the active users for the given date

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

    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult[ActiveUsersSearchData]
    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult[AnnotationsSearchData]
    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult[AverageSessionLengthSearchData]
    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult[CohortsSearchData]
    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult[EventsListSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="ActiveUsersSearchResult"></a>

`ActiveUsersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AnnotationsSearchResult"></a>

`AnnotationsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AverageSessionLengthSearchResult"></a>

`AverageSessionLengthSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CohortsSearchResult"></a>

`CohortsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="EventsListSearchResult"></a>

`EventsListSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AmplitudeAuthConfig"></a>

`AmplitudeAuthConfig(**data: Any)`
:   API Key Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_key: str`
    :   Your Amplitude project API key. Find it in Settings > Projects in your Amplitude account.

    `model_config`
    :   The type of the None singleton.

    `secret_key: str`
    :   Your Amplitude project secret key. Find it in Settings > Projects in your Amplitude account.

<a id="AmplitudeConnector"></a>

`AmplitudeConnector(auth_config: AmplitudeAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Amplitude API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new amplitude connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., AmplitudeAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = AmplitudeConnector(auth_config=AmplitudeAuthConfig(api_key="...", secret_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = AmplitudeConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = AmplitudeConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'AmplitudeAuthConfig'", name: str | None = None, replication_config: "'AmplitudeReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A AmplitudeConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await AmplitudeConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=AmplitudeAuthConfig(api_key="...", secret_key="..."),
            )
        
            # With replication config (required for this connector):
            connector = await AmplitudeConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=AmplitudeAuthConfig(api_key="...", secret_key="..."),
                replication_config=AmplitudeReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @AmplitudeConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @AmplitudeConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await AmplitudeConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.amplitude.models.AmplitudeCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            AmplitudeCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'get', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
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

<a id="AmplitudeReplicationConfig"></a>

`AmplitudeReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Amplitude.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `start_date: str`
    :   UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ. Any data before this date will not be replicated.

<a id="AnnotationsSearchData"></a>

`AnnotationsSearchData(**data: Any)`
:   Search result data for annotations entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `date: str | None`
    :   The date when the annotation was made

    `details: str | None`
    :   Additional details or information related to the annotation

    `id: int | None`
    :   The unique identifier for the annotation

    `label: str | None`
    :   The label assigned to the annotation

    `model_config`
    :   The type of the None singleton.

<a id="AverageSessionLengthSearchData"></a>

`AverageSessionLengthSearchData(**data: Any)`
:   Search result data for average_session_length entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `date: str | None`
    :   The date on which the session occurred

    `length: float | None`
    :   The duration of the session in seconds

    `model_config`
    :   The type of the None singleton.

<a id="CohortsSearchData"></a>

`CohortsSearchData(**data: Any)`
:   Search result data for cohorts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `app_id: int | None`
    :   The unique identifier of the application

    `archived: bool | None`
    :   Indicates if the cohort data is archived

    `chart_id: str | None`
    :   The identifier of the chart associated with the cohort

    `created_at: int | None`
    :   The timestamp when the cohort was created

    `definition: dict[str, typing.Any] | None`
    :   The specific definition or criteria for the cohort

    `description: str | None`
    :   A brief explanation or summary of the cohort

    `edit_id: str | None`
    :   The ID for editing purposes or version control

    `finished: bool | None`
    :   Indicates if the cohort data has been finalized

    `hidden: bool | None`
    :   Flag to determine if the cohort is hidden from view

    `id: str | None`
    :   The unique identifier for the cohort

    `is_official_content: bool | None`
    :   Indicates if the cohort data is official content

    `is_predictive: bool | None`
    :   Flag to indicate if the cohort is predictive

    `last_computed: int | None`
    :   Timestamp of the last computation of cohort data

    `last_mod: int | None`
    :   Timestamp of the last modification made to the cohort

    `last_viewed: int | None`
    :   Timestamp when the cohort was last viewed

    `location_id: str | None`
    :   Identifier of the location associated with the cohort

    `metadata: list[typing.Any] | None`
    :   Additional information or data related to the cohort

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The name or title of the cohort

    `owners: list[typing.Any] | None`
    :   The owners or administrators of the cohort

    `popularity: int | None`
    :   Popularity rank or score of the cohort

    `published: bool | None`
    :   Status indicating if the cohort data is published

    `shortcut_ids: list[typing.Any] | None`
    :   Identifiers of any shortcuts associated with the cohort

    `size: int | None`
    :   Size or scale of the cohort data

    `type_: str | None`
    :   The type or category of the cohort

    `view_count: int | None`
    :   The total count of views on the cohort data

    `viewers: list[typing.Any] | None`
    :   Users or viewers who have access to the cohort data

<a id="EventsListSearchData"></a>

`EventsListSearchData(**data: Any)`
:   Search result data for events_list entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `autohidden: bool | None`
    :   Whether the event is auto-hidden

    `clusters_hidden: bool | None`
    :   Whether the event is hidden from clusters

    `deleted: bool | None`
    :   Whether the event is deleted

    `display: str | None`
    :   Display name of the event

    `flow_hidden: bool | None`
    :   Whether the event is hidden from Pathfinder

    `hidden: bool | None`
    :   Whether the event is hidden

    `id: float | None`
    :   Unique identifier for the event type

    `in_waitroom: bool | None`
    :   Whether the event is in the waitroom

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the event type

    `non_active: bool | None`
    :   Whether the event is marked as inactive

    `timeline_hidden: Any`
    :   Whether the event is hidden from the timeline

    `totals: float | None`
    :   Total number of times the event occurred this week

    `totals_delta: float | None`
    :   Change in totals from the previous period

    `value: str | None`
    :   Raw event name in the data