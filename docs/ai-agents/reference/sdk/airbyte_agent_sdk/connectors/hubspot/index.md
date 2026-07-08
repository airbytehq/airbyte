---
id: airbyte_agent_sdk-connectors-hubspot-index
title: airbyte_agent_sdk.connectors.hubspot.index
---

Module airbyte_agent_sdk.connectors.hubspot
===========================================
Hubspot connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.hubspot.connector
* airbyte_agent_sdk.connectors.hubspot.connector_model
* airbyte_agent_sdk.connectors.hubspot.models
* airbyte_agent_sdk.connectors.hubspot.types

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

    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[CallsSearchData]
    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[CompaniesSearchData]
    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[ContactsSearchData]
    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[DealsSearchData]
    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[EmailsSearchData]
    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[MeetingsSearchData]
    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[NotesSearchData]
    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[TasksSearchData]
    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[TicketsSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="CallsSearchResult"></a>

`CallsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CompaniesSearchResult"></a>

`CompaniesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ContactsSearchResult"></a>

`ContactsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="DealsSearchResult"></a>

`DealsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="EmailsSearchResult"></a>

`EmailsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="MeetingsSearchResult"></a>

`MeetingsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="NotesSearchResult"></a>

`NotesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TasksSearchResult"></a>

`TasksSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TicketsSearchResult"></a>

`TicketsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

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

    `archived: bool | None`
    :   Indicates whether the call has been archived

    `created_at: str | None`
    :   Timestamp when the call was created

    `id: str | None`
    :   Unique identifier for the call record

    `model_config`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any]`
    :   Object containing all property values for the call

    `properties_hs_call_body: str | None`
    :   Description or notes about the call

    `properties_hs_call_direction: str | None`
    :   Direction of the call (INBOUND or OUTBOUND)

    `properties_hs_call_duration: str | None`
    :   Duration of the call in milliseconds

    `properties_hs_call_status: str | None`
    :   Status of the call (e.g., COMPLETED, BUSY, NO_ANSWER)

    `properties_hs_call_title: str | None`
    :   Title or subject of the call

    `properties_hs_createdate: str | None`
    :   Date the call was created

    `properties_hs_lastmodifieddate: str | None`
    :   Last modified date of the call

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hs_timestamp: str | None`
    :   Timestamp when the call activity occurred

    `properties_hubspot_owner_id: str | None`
    :   ID of the call owner

    `updated_at: str | None`
    :   Timestamp when the call record was last modified

<a id="CompaniesSearchData"></a>

`CompaniesSearchData(**data: Any)`
:   Search result data for companies entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Indicates whether the company has been deleted and moved to the recycling bin

    `contacts: list[typing.Any] | None`
    :   Associated contact records linked to this company

    `created_at: str | None`
    :   Timestamp when the company record was created

    `id: str | None`
    :   Unique identifier for the company record

    `model_config`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any]`
    :   Object containing all property values for the company

    `properties_createdate: str | None`
    :   Date the company was created

    `properties_domain: str | None`
    :   Company domain name

    `properties_hs_lastmodifieddate: str | None`
    :   Last modified date of the company

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hubspot_owner_id: str | None`
    :   ID of the HubSpot owner assigned to this company

    `properties_name: str | None`
    :   Company name

    `updated_at: str | None`
    :   Timestamp when the company record was last modified

<a id="ContactsSearchData"></a>

`ContactsSearchData(**data: Any)`
:   Search result data for contacts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Boolean flag indicating whether the contact has been archived or deleted

    `companies: list[typing.Any] | None`
    :   Associated company records linked to this contact

    `created_at: str | None`
    :   Timestamp indicating when the contact was first created in the system

    `id: str | None`
    :   Unique identifier for the contact record

    `model_config`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any]`
    :   Key-value object storing all contact properties and their values.

    `properties_associatedcompanyid: str | None`
    :   ID of the associated company

    `properties_createdate: str | None`
    :   Date the contact was created

    `properties_email: str | None`
    :   Contact email address

    `properties_firstname: str | None`
    :   Contact first name

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hubspot_owner_id: str | None`
    :   ID of the HubSpot owner assigned to this contact

    `properties_lastmodifieddate: str | None`
    :   Last modified date of the contact

    `properties_lastname: str | None`
    :   Contact last name

    `updated_at: str | None`
    :   Timestamp indicating when the contact record was last modified

<a id="DealsSearchData"></a>

`DealsSearchData(**data: Any)`
:   Search result data for deals entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Indicates whether the deal has been deleted and moved to the recycling bin

    `companies: list[typing.Any] | None`
    :   Collection of company records associated with the deal

    `contacts: list[typing.Any] | None`
    :   Collection of contact records associated with the deal

    `created_at: str | None`
    :   Timestamp when the deal record was originally created

    `id: str | None`
    :   Unique identifier for the deal record

    `line_items: list[typing.Any] | None`
    :   Collection of product line items associated with the deal

    `model_config`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any]`
    :   Key-value object containing all deal properties and custom fields

    `properties_amount: str | None`
    :   Deal amount

    `properties_closedate: str | None`
    :   Expected close date of the deal

    `properties_createdate: str | None`
    :   Date the deal was created

    `properties_dealname: str | None`
    :   Deal name

    `properties_dealstage: str | None`
    :   Current deal stage

    `properties_hs_lastmodifieddate: str | None`
    :   Last modified date of the deal

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hubspot_owner_id: str | None`
    :   ID of the HubSpot owner assigned to this deal

    `properties_pipeline: str | None`
    :   Deal pipeline

    `updated_at: str | None`
    :   Timestamp when the deal record was last modified

<a id="EmailsSearchData"></a>

`EmailsSearchData(**data: Any)`
:   Search result data for emails entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Indicates whether the email has been archived

    `created_at: str | None`
    :   Timestamp when the email was created

    `id: str | None`
    :   Unique identifier for the email record

    `model_config`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any]`
    :   Object containing all property values for the email

    `properties_hs_createdate: str | None`
    :   Date the email was created

    `properties_hs_email_direction: str | None`
    :   Direction of the email (EMAIL, INCOMING_EMAIL, FORWARDED_EMAIL)

    `properties_hs_email_status: str | None`
    :   Status of the email (BOUNCED, FAILED, SCHEDULED, SENDING, SENT, DRAFT)

    `properties_hs_email_subject: str | None`
    :   Subject line of the email

    `properties_hs_email_text: str | None`
    :   Plain text body of the email

    `properties_hs_lastmodifieddate: str | None`
    :   Last modified date of the email

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hs_timestamp: str | None`
    :   Timestamp when the email activity occurred

    `properties_hubspot_owner_id: str | None`
    :   ID of the email owner

    `updated_at: str | None`
    :   Timestamp when the email record was last modified

<a id="HubspotConnector"></a>

`HubspotConnector(auth_config: HubspotAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Hubspot API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new hubspot connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., HubspotAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = HubspotConnector(auth_config=HubspotAuthConfig(client_id="...", client_secret="...", refresh_token="...", access_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = HubspotConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = HubspotConnector(
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
            @HubspotConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @HubspotConnector.tool_utils(update_docstring=False, max_output_chars=None)
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @HubspotConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
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

    `check(self) ‑> airbyte_agent_sdk.connectors.hubspot.models.HubspotCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            HubspotCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'create', 'get', 'update', 'api_search', 'delete', 'context_store_search']", params: Mapping[str, Any] | None = None, *, select_fields: list[str] | None = None, exclude_fields: list[str] | None = None, skip_truncation: bool = True) ‑> Any`
    :   Execute an entity operation with full type safety.
        
        This is the recommended interface for blessed connectors as it:
        - Uses the same signature as non-blessed connectors
        - Provides full IDE autocomplete for entity/action/params
        - Makes migration from generic to blessed connectors seamless
        
        Args:
            entity: Entity name (e.g., "customers")
            action: Operation action (e.g., "create", "get", "list")
            params: Operation parameters (typed based on entity+action)
            select_fields: Optional allowlist of dot-notation fields to include
            exclude_fields: Optional blocklist of dot-notation fields to remove
            skip_truncation: Disable long-text truncation for collection actions
        
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

<a id="HubspotOAuthCredentials"></a>

`HubspotOAuthCredentials(**data: Any)`
:   HubSpot OAuth App Credentials - Provide your own HubSpot OAuth app credentials to override the default Airbyte-managed ones.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `client_id: str`
    :   Your HubSpot OAuth app's client ID

    `client_secret: str`
    :   Your HubSpot OAuth app's client secret

    `model_config`
    :   The type of the None singleton.

<a id="MeetingsSearchData"></a>

`MeetingsSearchData(**data: Any)`
:   Search result data for meetings entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Indicates whether the meeting has been archived

    `created_at: str | None`
    :   Timestamp when the meeting was created

    `id: str | None`
    :   Unique identifier for the meeting record

    `model_config`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any]`
    :   Object containing all property values for the meeting

    `properties_hs_createdate: str | None`
    :   Date the meeting was created

    `properties_hs_lastmodifieddate: str | None`
    :   Last modified date of the meeting

    `properties_hs_meeting_body: str | None`
    :   Description or notes about the meeting

    `properties_hs_meeting_end_time: str | None`
    :   End time of the meeting

    `properties_hs_meeting_location: str | None`
    :   Location of the meeting

    `properties_hs_meeting_outcome: str | None`
    :   Outcome of the meeting (e.g., SCHEDULED, COMPLETED, NO_SHOW, CANCELED)

    `properties_hs_meeting_start_time: str | None`
    :   Start time of the meeting

    `properties_hs_meeting_title: str | None`
    :   Title of the meeting

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hs_timestamp: str | None`
    :   Timestamp when the meeting activity occurred

    `properties_hubspot_owner_id: str | None`
    :   ID of the meeting owner

    `updated_at: str | None`
    :   Timestamp when the meeting record was last modified

<a id="NotesSearchData"></a>

`NotesSearchData(**data: Any)`
:   Search result data for notes entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Indicates whether the note has been archived

    `created_at: str | None`
    :   Timestamp when the note was created

    `id: str | None`
    :   Unique identifier for the note record

    `model_config`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any]`
    :   Object containing all property values for the note

    `properties_hs_createdate: str | None`
    :   Date the note was created

    `properties_hs_lastmodifieddate: str | None`
    :   Last modified date of the note

    `properties_hs_note_body: str | None`
    :   The body content of the note (supports HTML)

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hs_timestamp: str | None`
    :   Timestamp when the note activity occurred

    `properties_hubspot_owner_id: str | None`
    :   ID of the note owner

    `updated_at: str | None`
    :   Timestamp when the note record was last modified

<a id="TasksSearchData"></a>

`TasksSearchData(**data: Any)`
:   Search result data for tasks entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Indicates whether the task has been archived

    `created_at: str | None`
    :   Timestamp when the task was created

    `id: str | None`
    :   Unique identifier for the task record

    `model_config`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any]`
    :   Object containing all property values for the task

    `properties_hs_createdate: str | None`
    :   Date the task was created

    `properties_hs_lastmodifieddate: str | None`
    :   Last modified date of the task

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hs_task_body: str | None`
    :   Description or notes for the task

    `properties_hs_task_priority: str | None`
    :   Priority of the task (LOW, MEDIUM, HIGH)

    `properties_hs_task_status: str | None`
    :   Status of the task (NOT_STARTED, IN_PROGRESS, WAITING, COMPLETED, DEFERRED)

    `properties_hs_task_subject: str | None`
    :   Subject or title of the task

    `properties_hs_task_type: str | None`
    :   Type of the task (TODO, CALL, EMAIL)

    `properties_hs_timestamp: str | None`
    :   Due date / timestamp for the task

    `properties_hubspot_owner_id: str | None`
    :   ID of the task owner

    `updated_at: str | None`
    :   Timestamp when the task record was last modified

<a id="TicketsSearchData"></a>

`TicketsSearchData(**data: Any)`
:   Search result data for tickets entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Indicates whether the ticket has been deleted and moved to the recycling bin

    `companies: list[typing.Any] | None`
    :   Collection of company records associated with the ticket

    `contacts: list[typing.Any] | None`
    :   Collection of contact records associated with the ticket

    `created_at: str | None`
    :   Timestamp when the ticket record was originally created

    `id: str | None`
    :   Unique identifier for the ticket record

    `model_config`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any]`
    :   Object containing all property values for the ticket

    `properties_content: str | None`
    :   Ticket content/description

    `properties_createdate: str | None`
    :   Date the ticket was created

    `properties_hs_lastmodifieddate: str | None`
    :   Last modified date of the ticket

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hs_pipeline: str | None`
    :   Ticket pipeline

    `properties_hs_pipeline_stage: str | None`
    :   Current pipeline stage of the ticket

    `properties_hs_ticket_category: str | None`
    :   Ticket category

    `properties_hs_ticket_priority: str | None`
    :   Ticket priority level

    `properties_subject: str | None`
    :   Ticket subject line

    `updated_at: str | None`
    :   Timestamp when the ticket record was last modified