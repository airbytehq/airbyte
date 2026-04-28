---
id: airbyte_agent_sdk-connectors-incident_io-index
title: airbyte_agent_sdk.connectors.incident_io.index
---

Module airbyte_agent_sdk.connectors.incident_io
===============================================
Incident-Io connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.incident_io.connector
* airbyte_agent_sdk.connectors.incident_io.connector_model
* airbyte_agent_sdk.connectors.incident_io.models
* airbyte_agent_sdk.connectors.incident_io.types

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

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[AlertsSearchData]
    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[CatalogTypesSearchData]
    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[CustomFieldsSearchData]
    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[EscalationsSearchData]
    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[IncidentRolesSearchData]
    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[IncidentStatusesSearchData]
    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[IncidentTimestampsSearchData]
    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[IncidentUpdatesSearchData]
    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[IncidentsSearchData]
    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[SchedulesSearchData]
    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[SeveritiesSearchData]
    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[UsersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="AlertsSearchResult"></a>

`AlertsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CatalogTypesSearchResult"></a>

`CatalogTypesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CustomFieldsSearchResult"></a>

`CustomFieldsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="EscalationsSearchResult"></a>

`EscalationsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="IncidentRolesSearchResult"></a>

`IncidentRolesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="IncidentStatusesSearchResult"></a>

`IncidentStatusesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="IncidentTimestampsSearchResult"></a>

`IncidentTimestampsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="IncidentUpdatesSearchResult"></a>

`IncidentUpdatesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="IncidentsSearchResult"></a>

`IncidentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SchedulesSearchResult"></a>

`SchedulesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SeveritiesSearchResult"></a>

`SeveritiesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AlertsSearchData"></a>

`AlertsSearchData(**data: Any)`
:   Search result data for alerts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `alert_source_id: str | None`
    :   ID of the alert source that generated this alert

    `attributes: list[typing.Any] | None`
    :   Structured alert attributes

    `created_at: str | None`
    :   When the alert was created

    `deduplication_key: str | None`
    :   Deduplication key uniquely referencing this alert

    `description: str | None`
    :   Description of the alert

    `id: str | None`
    :   Unique identifier for the alert

    `model_config`
    :   The type of the None singleton.

    `resolved_at: str | None`
    :   When the alert was resolved

    `source_url: str | None`
    :   Link to the alert in the upstream system

    `status: str | None`
    :   Status of the alert: firing or resolved

    `title: str | None`
    :   Title of the alert

    `updated_at: str | None`
    :   When the alert was last updated

<a id="CatalogTypesSearchData"></a>

`CatalogTypesSearchData(**data: Any)`
:   Search result data for catalog_types entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: dict[str, typing.Any] | None`
    :   Annotations metadata

    `categories: list[typing.Any] | None`
    :   Categories this type belongs to

    `color: str | None`
    :   Display color

    `created_at: str | None`
    :   When the catalog type was created

    `description: str | None`
    :   Description of the catalog type

    `icon: str | None`
    :   Display icon

    `id: str | None`
    :   Unique identifier for the catalog type

    `is_editable: bool | None`
    :   Whether entries can be edited

    `last_synced_at: str | None`
    :   When the catalog type was last synced

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the catalog type

    `ranked: bool | None`
    :   Whether entries are ranked

    `registry_type: str | None`
    :   Registry type if synced from an integration

    `required_integrations: list[typing.Any] | None`
    :   Integrations required for this type

    `schema_: dict[str, typing.Any] | None`
    :   Schema definition for the catalog type

    `semantic_type: str | None`
    :   Semantic type for special behavior

    `type_name: str | None`
    :   Programmatic type name

    `updated_at: str | None`
    :   When the catalog type was last updated

<a id="CustomFieldsSearchData"></a>

`CustomFieldsSearchData(**data: Any)`
:   Search result data for custom_fields entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   When the custom field was created

    `description: str | None`
    :   Description of the custom field

    `field_type: str | None`
    :   Type of field

    `id: str | None`
    :   Unique identifier for the custom field

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the custom field

    `updated_at: str | None`
    :   When the custom field was last updated

<a id="EscalationsSearchData"></a>

`EscalationsSearchData(**data: Any)`
:   Search result data for escalations entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   When the escalation was created

    `creator: dict[str, typing.Any] | None`
    :   The creator of this escalation

    `escalation_path_id: str | None`
    :   ID of the escalation path used

    `events: list[typing.Any] | None`
    :   History of escalation events

    `id: str | None`
    :   Unique identifier for the escalation

    `model_config`
    :   The type of the None singleton.

    `priority: dict[str, typing.Any] | None`
    :   Priority of the escalation

    `related_alerts: list[typing.Any] | None`
    :   Alerts related to this escalation

    `related_incidents: list[typing.Any] | None`
    :   Incidents related to this escalation

    `status: str | None`
    :   Status: pending, triggered, acked, resolved, expired, cancelled

    `title: str | None`
    :   Title of the escalation

    `updated_at: str | None`
    :   When the escalation was last updated

<a id="IncidentIoAuthConfig"></a>

`IncidentIoAuthConfig(**data: Any)`
:   API Key Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_key: str`
    :   Your incident.io API key. Create one at https://app.incident.io/settings/api-keys

    `model_config`
    :   The type of the None singleton.

<a id="IncidentIoConnector"></a>

`IncidentIoConnector(auth_config: IncidentIoAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Incident-Io API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new incident-io connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., IncidentIoAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = IncidentIoConnector(auth_config=IncidentIoAuthConfig(api_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = IncidentIoConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = IncidentIoConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'IncidentIoAuthConfig'", name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None) ‑> airbyte_agent_sdk.connectors.incident_io.connector.IncidentIoConnector`
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
            A IncidentIoConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await IncidentIoConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=IncidentIoAuthConfig(api_key="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @IncidentIoConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @IncidentIoConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await IncidentIoConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.incident_io.models.IncidentIoCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            IncidentIoCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="IncidentRolesSearchData"></a>

`IncidentRolesSearchData(**data: Any)`
:   Search result data for incident_roles entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   When the role was created

    `description: str | None`
    :   Description of the role

    `id: str | None`
    :   Unique identifier for the incident role

    `instructions: str | None`
    :   Instructions for the role holder

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the role

    `required: bool | None`
    :   Whether this role must be assigned

    `role_type: str | None`
    :   Type of role

    `shortform: str | None`
    :   Short form label for the role

    `updated_at: str | None`
    :   When the role was last updated

<a id="IncidentStatusesSearchData"></a>

`IncidentStatusesSearchData(**data: Any)`
:   Search result data for incident_statuses entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `category: str | None`
    :   Category: triage, active, post-incident, closed, etc.

    `created_at: str | None`
    :   When the status was created

    `description: str | None`
    :   Description of the status

    `id: str | None`
    :   Unique identifier for the status

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the status

    `rank: float | None`
    :   Rank for ordering

    `updated_at: str | None`
    :   When the status was last updated

<a id="IncidentTimestampsSearchData"></a>

`IncidentTimestampsSearchData(**data: Any)`
:   Search result data for incident_timestamps entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   Unique identifier for the timestamp

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the timestamp

    `rank: float | None`
    :   Rank for ordering

<a id="IncidentUpdatesSearchData"></a>

`IncidentUpdatesSearchData(**data: Any)`
:   Search result data for incident_updates entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   When the update was created

    `id: str | None`
    :   Unique identifier for the incident update

    `incident_id: str | None`
    :   ID of the incident this update belongs to

    `message: str | None`
    :   Update message content

    `model_config`
    :   The type of the None singleton.

    `new_incident_status: dict[str, typing.Any] | None`
    :   New incident status set by this update

    `new_severity: dict[str, typing.Any] | None`
    :   New severity set by this update

    `updater: dict[str, typing.Any] | None`
    :   Who made this update

<a id="IncidentsSearchData"></a>

`IncidentsSearchData(**data: Any)`
:   Search result data for incidents entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   When the incident was created

    `creator: dict[str, typing.Any] | None`
    :   The user who created the incident

    `custom_field_entries: list[typing.Any] | None`
    :   Custom field values for the incident

    `duration_metrics: list[typing.Any] | None`
    :   Duration metrics associated with the incident

    `has_debrief: bool | None`
    :   Whether the incident has had a debrief

    `id: str | None`
    :   Unique identifier for the incident

    `incident_role_assignments: list[typing.Any] | None`
    :   Role assignments for the incident

    `incident_status: dict[str, typing.Any] | None`
    :   Current status of the incident

    `incident_timestamp_values: list[typing.Any] | None`
    :   Timestamp values for the incident

    `incident_type: dict[str, typing.Any] | None`
    :   Type of the incident

    `mode: str | None`
    :   Mode of the incident: standard, retrospective, test, or tutorial

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name/title of the incident

    `permalink: str | None`
    :   Link to the incident in the dashboard

    `reference: str | None`
    :   Human-readable reference (e.g. INC-123)

    `severity: dict[str, typing.Any] | None`
    :   Severity of the incident

    `slack_channel_id: str | None`
    :   Slack channel ID for the incident

    `slack_channel_name: str | None`
    :   Slack channel name for the incident

    `slack_team_id: str | None`
    :   Slack team/workspace ID

    `summary: str | None`
    :   Detailed summary of the incident

    `updated_at: str | None`
    :   When the incident was last updated

    `visibility: str | None`
    :   Whether the incident is public or private

    `workload_minutes_late: float | None`
    :   Minutes of workload classified as late

    `workload_minutes_sleeping: float | None`
    :   Minutes of workload classified as sleeping

    `workload_minutes_total: float | None`
    :   Total workload minutes

    `workload_minutes_working: float | None`
    :   Minutes of workload classified as working

<a id="SchedulesSearchData"></a>

`SchedulesSearchData(**data: Any)`
:   Search result data for schedules entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: dict[str, typing.Any] | None`
    :   Annotations metadata

    `config: dict[str, typing.Any] | None`
    :   Schedule configuration with rotations

    `created_at: str | None`
    :   When the schedule was created

    `current_shifts: list[typing.Any] | None`
    :   Currently active shifts

    `id: str | None`
    :   Unique identifier for the schedule

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the schedule

    `timezone: str | None`
    :   Timezone for the schedule

    `updated_at: str | None`
    :   When the schedule was last updated

<a id="SeveritiesSearchData"></a>

`SeveritiesSearchData(**data: Any)`
:   Search result data for severities entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   When the severity was created

    `description: str | None`
    :   Description of the severity

    `id: str | None`
    :   Unique identifier for the severity

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the severity

    `rank: float | None`
    :   Rank for ordering

    `updated_at: str | None`
    :   When the severity was last updated

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

    `base_role: dict[str, typing.Any] | None`
    :   Base role assigned to the user

    `custom_roles: list[typing.Any] | None`
    :   Custom roles assigned to the user

    `email: str | None`
    :   Email address of the user

    `id: str | None`
    :   Unique identifier for the user

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Full name of the user

    `role: str | None`
    :   Deprecated role field

    `slack_user_id: str | None`
    :   Slack user ID