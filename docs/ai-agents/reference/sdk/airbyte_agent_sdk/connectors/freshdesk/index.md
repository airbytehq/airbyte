---
id: airbyte_agent_sdk-connectors-freshdesk-index
title: airbyte_agent_sdk.connectors.freshdesk.index
---

Module airbyte_agent_sdk.connectors.freshdesk
=============================================
Freshdesk connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.freshdesk.connector
* airbyte_agent_sdk.connectors.freshdesk.connector_model
* airbyte_agent_sdk.connectors.freshdesk.models
* airbyte_agent_sdk.connectors.freshdesk.types

Classes
-------

<a id="AgentsSearchData"></a>

`AgentsSearchData(**data: Any)`
:   Search result data for agents entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `available: bool | None`
    :   Whether the agent is available

    `available_since: str | None`
    :   Timestamp since the agent has been available

    `contact: dict[str, typing.Any] | None`
    :   Contact details of the agent including name, email, phone, and job title

    `created_at: str | None`
    :   Agent creation timestamp

    `id: int | None`
    :   Unique agent ID

    `last_active_at: str | None`
    :   Timestamp of last agent activity

    `model_config`
    :   The type of the None singleton.

    `occasional: bool | None`
    :   Whether the agent is an occasional agent

    `signature: str | None`
    :   Signature of the agent (HTML)

    `ticket_scope: int | None`
    :   Ticket scope: 1=Global, 2=Group, 3=Restricted

    `type_: str | None`
    :   Agent type: support_agent, field_agent, collaborator

    `updated_at: str | None`
    :   Agent last update timestamp

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

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult[AgentsSearchData]
    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult[CompaniesSearchData]
    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult[ContactsSearchData]
    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult[GroupsSearchData]
    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult[RolesSearchData]
    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult[SatisfactionRatingsSearchData]
    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult[SurveysSearchData]
    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult[TicketFieldsSearchData]
    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult[TicketsSearchData]
    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult[TimeEntriesSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="AgentsSearchResult"></a>

`AgentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="GroupsSearchResult"></a>

`GroupsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="RolesSearchResult"></a>

`RolesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SatisfactionRatingsSearchResult"></a>

`SatisfactionRatingsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SurveysSearchResult"></a>

`SurveysSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TicketFieldsSearchResult"></a>

`TicketFieldsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TimeEntriesSearchResult"></a>

`TimeEntriesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

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

    `account_tier: str | None`
    :   Account tier of the company

    `created_at: str | None`
    :   Company creation timestamp

    `custom_fields: dict[str, typing.Any] | None`
    :   Custom fields associated with the company

    `description: str | None`
    :   Description of the company

    `domains: list[typing.Any] | None`
    :   Email domains associated with the company

    `health_score: str | None`
    :   Health score of the company

    `id: int | None`
    :   Unique company ID

    `industry: str | None`
    :   Industry of the company

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the company

    `note: str | None`
    :   Notes about the company

    `renewal_date: str | None`
    :   Renewal date

    `updated_at: str | None`
    :   Company last update timestamp

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

    `active: bool | None`
    :   Whether the contact has been verified

    `address: str | None`
    :   Address of the contact

    `company_id: int | None`
    :   ID of the primary company

    `created_at: str | None`
    :   Contact creation timestamp

    `csat_rating: int | None`
    :   CSAT rating of the contact

    `custom_fields: dict[str, typing.Any] | None`
    :   Custom fields associated with the contact

    `description: str | None`
    :   Description of the contact

    `email: str | None`
    :   Primary email address

    `facebook_id: str | None`
    :   Facebook ID of the contact

    `id: int | None`
    :   Unique contact ID

    `job_title: str | None`
    :   Job title of the contact

    `language: str | None`
    :   Language of the contact

    `mobile: str | None`
    :   Mobile number

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the contact

    `phone: str | None`
    :   Phone number

    `preferred_source: str | None`
    :   Preferred contact source

    `time_zone: str | None`
    :   Time zone of the contact

    `twitter_id: str | None`
    :   Twitter ID

    `unique_external_id: str | None`
    :   External ID of the contact

    `updated_at: str | None`
    :   Contact last update timestamp

<a id="FreshdeskAuthConfig"></a>

`FreshdeskAuthConfig(**data: Any)`
:   API Key Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_key: str`
    :   Your Freshdesk API key (found in Profile Settings)

    `model_config`
    :   The type of the None singleton.

<a id="FreshdeskConnector"></a>

`FreshdeskConnector(auth_config: FreshdeskAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, subdomain: str | None = None)`
:   Type-safe Freshdesk API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new freshdesk connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., FreshdeskAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)            subdomain: Your Freshdesk subdomain (e.g., "acme" for acme.freshdesk.com)
    Examples:
        # Local mode (direct API calls)
        connector = FreshdeskConnector(auth_config=FreshdeskAuthConfig(api_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = FreshdeskConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = FreshdeskConnector(
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
            @FreshdeskConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @FreshdeskConnector.tool_utils(update_docstring=False, max_output_chars=None)
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @FreshdeskConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
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

    `check(self) ‑> airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            FreshdeskCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="GroupsSearchData"></a>

`GroupsSearchData(**data: Any)`
:   Search result data for groups entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `auto_ticket_assign: int | None`
    :   Auto ticket assignment: 0=Disabled, 1=Round Robin, 2=Skill Based, 3=Load Based

    `business_hour_id: int | None`
    :   ID of the associated business hour

    `created_at: str | None`
    :   Group creation timestamp

    `description: str | None`
    :   Description of the group

    `escalate_to: int | None`
    :   User ID for escalation

    `group_type: str | None`
    :   Type of the group (e.g., support_agent_group)

    `id: int | None`
    :   Unique group ID

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the group

    `unassigned_for: str | None`
    :   Time after which escalation triggers

    `updated_at: str | None`
    :   Group last update timestamp

<a id="RolesSearchData"></a>

`RolesSearchData(**data: Any)`
:   Search result data for roles entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   Role creation timestamp

    `default: bool | None`
    :   Whether this is a default role

    `description: str | None`
    :   Description of the role

    `id: int | None`
    :   Unique role ID

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the role

    `updated_at: str | None`
    :   Role last update timestamp

<a id="SatisfactionRatingsSearchData"></a>

`SatisfactionRatingsSearchData(**data: Any)`
:   Search result data for satisfaction_ratings entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agent_id: int | None`
    :   ID of the agent

    `created_at: str | None`
    :   Rating creation timestamp

    `feedback: str | None`
    :   Feedback text

    `group_id: int | None`
    :   ID of the group

    `id: int | None`
    :   Unique satisfaction rating ID

    `model_config`
    :   The type of the None singleton.

    `ratings: dict[str, typing.Any] | None`
    :   Rating values (question_id to rating mapping)

    `survey_id: int | None`
    :   ID of the survey

    `ticket_id: int | None`
    :   ID of the ticket

    `updated_at: str | None`
    :   Rating last update timestamp

    `user_id: int | None`
    :   ID of the user (requester)

<a id="SurveysSearchData"></a>

`SurveysSearchData(**data: Any)`
:   Search result data for surveys entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | None`
    :   Whether the survey is active

    `created_at: str | None`
    :   Survey creation timestamp

    `id: int | None`
    :   Unique survey ID

    `model_config`
    :   The type of the None singleton.

    `questions: list[typing.Any] | None`
    :   Survey questions

    `title: str | None`
    :   Title of the survey

    `updated_at: str | None`
    :   Survey last update timestamp

<a id="TicketFieldsSearchData"></a>

`TicketFieldsSearchData(**data: Any)`
:   Search result data for ticket_fields entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `choices: dict[str, typing.Any] | None`
    :   Available choices for dropdown fields

    `created_at: str | None`
    :   Field creation timestamp

    `customers_can_edit: bool | None`
    :   Whether customers can edit this field

    `default: bool | None`
    :   Whether this is a default (non-custom) field

    `description: str | None`
    :   Description of the field

    `displayed_to_customers: bool | None`
    :   Whether the field is displayed to customers

    `id: int | None`
    :   Unique ticket field ID

    `label: str | None`
    :   Display label for agents

    `label_for_customers: str | None`
    :   Display label in the customer portal

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the field

    `portal_cc: bool | None`
    :   Whether CC is enabled in the portal

    `portal_cc_to: str | None`
    :   CC recipients scope (all or company)

    `position: int | None`
    :   Position of the field in the form

    `required_for_agents: bool | None`
    :   Whether the field is required for agents

    `required_for_closure: bool | None`
    :   Whether the field is required for ticket closure

    `required_for_customers: bool | None`
    :   Whether the field is required for customers

    `type_: str | None`
    :   Field type (e.g., custom_dropdown, custom_text)

    `updated_at: str | None`
    :   Field last update timestamp

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

    `associated_tickets_count: int | None`
    :   Number of associated tickets

    `association_type: int | None`
    :   Association type for parent/child tickets

    `cc_emails: list[typing.Any] | None`
    :   CC email addresses

    `company_id: int | None`
    :   Company ID of the requester

    `created_at: str | None`
    :   Ticket creation timestamp

    `custom_fields: dict[str, typing.Any] | None`
    :   Custom fields associated with the ticket

    `description: str | None`
    :   HTML content of the ticket

    `description_text: str | None`
    :   Plain text content of the ticket

    `due_by: str | None`
    :   Resolution due by timestamp

    `email_config_id: int | None`
    :   ID of the email config used for the ticket

    `fr_due_by: str | None`
    :   First response due by timestamp

    `fr_escalated: bool | None`
    :   Whether the first response time was breached

    `fwd_emails: list[typing.Any] | None`
    :   Forwarded email addresses

    `group_id: int | None`
    :   ID of the group to which the ticket is assigned

    `id: int | None`
    :   Unique ticket ID

    `is_escalated: bool | None`
    :   Whether the ticket is escalated

    `model_config`
    :   The type of the None singleton.

    `nr_due_by: str | None`
    :   Next response due by timestamp

    `nr_escalated: bool | None`
    :   Whether the next response time was breached

    `priority: int | None`
    :   Priority: 1=Low, 2=Medium, 3=High, 4=Urgent

    `product_id: int | None`
    :   ID of the product associated with the ticket

    `reply_cc_emails: list[typing.Any] | None`
    :   Reply CC email addresses

    `requester: dict[str, typing.Any] | None`
    :   Requester details including name, email, and contact info

    `requester_id: int | None`
    :   ID of the requester

    `responder_id: int | None`
    :   ID of the agent to whom the ticket is assigned

    `source: int | None`
    :   Source: 1=Email, 2=Portal, 3=Phone, 7=Chat, 9=Feedback Widget, 10=Outbound Email

    `spam: bool | None`
    :   Whether the ticket is marked as spam

    `stats: dict[str, typing.Any] | None`
    :   Ticket statistics including response and resolution times

    `status: int | None`
    :   Status: 2=Open, 3=Pending, 4=Resolved, 5=Closed

    `subject: str | None`
    :   Subject of the ticket

    `tags: list[typing.Any] | None`
    :   Tags associated with the ticket

    `ticket_cc_emails: list[typing.Any] | None`
    :   Ticket CC email addresses

    `to_emails: list[typing.Any] | None`
    :   To email addresses

    `type_: str | None`
    :   Ticket type

    `updated_at: str | None`
    :   Ticket last update timestamp

<a id="TimeEntriesSearchData"></a>

`TimeEntriesSearchData(**data: Any)`
:   Search result data for time_entries entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agent_id: int | None`
    :   ID of the agent

    `billable: bool | None`
    :   Whether the time entry is billable

    `company_id: int | None`
    :   ID of the associated company

    `created_at: str | None`
    :   Time entry creation timestamp

    `executed_at: str | None`
    :   Execution timestamp

    `id: int | None`
    :   Unique time entry ID

    `model_config`
    :   The type of the None singleton.

    `note: str | None`
    :   Description of the time entry

    `start_time: str | None`
    :   Start time of the timer

    `ticket_id: int | None`
    :   ID of the associated ticket

    `time_spent: str | None`
    :   Time spent in hh:mm format

    `timer_running: bool | None`
    :   Whether the timer is running

    `updated_at: str | None`
    :   Time entry last update timestamp