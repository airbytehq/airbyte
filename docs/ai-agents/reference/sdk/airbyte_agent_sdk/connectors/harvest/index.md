---
id: airbyte_agent_sdk-connectors-harvest-index
title: airbyte_agent_sdk.connectors.harvest.index
---

Module airbyte_agent_sdk.connectors.harvest
===========================================
Harvest connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.harvest.connector
* airbyte_agent_sdk.connectors.harvest.connector_model
* airbyte_agent_sdk.connectors.harvest.models
* airbyte_agent_sdk.connectors.harvest.types

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

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[ClientsSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[CompanySearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[ContactsSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[EstimateItemCategoriesSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[EstimatesSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[ExpenseCategoriesSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[ExpensesSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[InvoiceItemCategoriesSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[InvoicesSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[ProjectsSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[RolesSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[TaskAssignmentsSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[TasksSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[TimeEntriesSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[TimeProjectsSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[TimeTasksSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[UserAssignmentsSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[UsersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="ClientsSearchResult"></a>

`ClientsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CompanySearchResult"></a>

`CompanySearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="EstimateItemCategoriesSearchResult"></a>

`EstimateItemCategoriesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="EstimatesSearchResult"></a>

`EstimatesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ExpenseCategoriesSearchResult"></a>

`ExpenseCategoriesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ExpensesSearchResult"></a>

`ExpensesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="InvoiceItemCategoriesSearchResult"></a>

`InvoiceItemCategoriesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="InvoicesSearchResult"></a>

`InvoicesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ProjectsSearchResult"></a>

`ProjectsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TaskAssignmentsSearchResult"></a>

`TaskAssignmentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TimeProjectsSearchResult"></a>

`TimeProjectsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TimeTasksSearchResult"></a>

`TimeTasksSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="UserAssignmentsSearchResult"></a>

`UserAssignmentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ClientsSearchData"></a>

`ClientsSearchData(**data: Any)`
:   Search result data for clients entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address: str | None`
    :   The client's postal address

    `created_at: str | None`
    :   When the client record was created

    `currency: str | None`
    :   The currency used by the client

    `id: int | None`
    :   Unique identifier for the client

    `is_active: bool | None`
    :   Whether the client is active

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The client's name

    `updated_at: str | None`
    :   When the client record was last updated

<a id="CompanySearchData"></a>

`CompanySearchData(**data: Any)`
:   Search result data for company entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `base_uri: str | None`
    :   The base URI

    `currency: str | None`
    :   Currency used by the company

    `full_domain: str | None`
    :   The full domain name

    `is_active: bool | None`
    :   Whether the company is active

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The name of the company

    `plan_type: str | None`
    :   The plan type

    `weekly_capacity: int | None`
    :   Weekly capacity in seconds

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

    `client: dict[str, typing.Any] | None`
    :   Client associated with the contact

    `created_at: str | None`
    :   When created

    `email: str | None`
    :   Email address

    `first_name: str | None`
    :   First name

    `id: int | None`
    :   Unique identifier

    `last_name: str | None`
    :   Last name

    `model_config`
    :   The type of the None singleton.

    `title: str | None`
    :   Job title

    `updated_at: str | None`
    :   When last updated

<a id="EstimateItemCategoriesSearchData"></a>

`EstimateItemCategoriesSearchData(**data: Any)`
:   Search result data for estimate_item_categories entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   When created

    `id: int | None`
    :   Unique identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Category name

    `updated_at: str | None`
    :   When last updated

<a id="EstimatesSearchData"></a>

`EstimatesSearchData(**data: Any)`
:   Search result data for estimates entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: float | None`
    :   Total amount

    `client: dict[str, typing.Any] | None`
    :   Client details

    `created_at: str | None`
    :   When created

    `currency: str | None`
    :   Currency

    `id: int | None`
    :   Unique identifier

    `issue_date: str | None`
    :   Issue date

    `model_config`
    :   The type of the None singleton.

    `number: str | None`
    :   Estimate number

    `state: str | None`
    :   Current state

    `subject: str | None`
    :   Subject

    `updated_at: str | None`
    :   When last updated

<a id="ExpenseCategoriesSearchData"></a>

`ExpenseCategoriesSearchData(**data: Any)`
:   Search result data for expense_categories entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   When created

    `id: int | None`
    :   Unique identifier

    `is_active: bool | None`
    :   Whether active

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Category name

    `unit_name: str | None`
    :   Unit name

    `unit_price: float | None`
    :   Unit price

    `updated_at: str | None`
    :   When last updated

<a id="ExpensesSearchData"></a>

`ExpensesSearchData(**data: Any)`
:   Search result data for expenses entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `billable: bool | None`
    :   Whether billable

    `client: dict[str, typing.Any] | None`
    :   Associated client

    `created_at: str | None`
    :   When created

    `expense_category: dict[str, typing.Any] | None`
    :   Expense category

    `id: int | None`
    :   Unique identifier

    `is_billed: bool | None`
    :   Whether billed

    `model_config`
    :   The type of the None singleton.

    `notes: str | None`
    :   Notes

    `project: dict[str, typing.Any] | None`
    :   Associated project

    `spent_date: str | None`
    :   Date spent

    `total_cost: float | None`
    :   Total cost

    `updated_at: str | None`
    :   When last updated

    `user: dict[str, typing.Any] | None`
    :   Associated user

<a id="HarvestConnector"></a>

`HarvestConnector(auth_config: HarvestAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Harvest API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new harvest connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., HarvestAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = HarvestConnector(auth_config=HarvestAuthConfig(client_id="...", client_secret="...", refresh_token="...", account_id="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = HarvestConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = HarvestConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'HarvestAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: "'HarvestReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A HarvestConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await HarvestConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=HarvestAuthConfig(client_id="...", client_secret="...", refresh_token="...", account_id="..."),
            )
        
            # With replication config (required for this connector):
            connector = await HarvestConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=HarvestAuthConfig(client_id="...", client_secret="...", refresh_token="...", account_id="..."),
                replication_config=HarvestReplicationConfig(replication_start_date="..."),
            )
        
            # With server-side OAuth:
            connector = await HarvestConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
                replication_config=HarvestReplicationConfig(replication_start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: "'HarvestReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            consent_url = await HarvestConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Harvest Source",
                replication_config=HarvestReplicationConfig(replication_start_date="..."),
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @HarvestConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @HarvestConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await HarvestConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.harvest.models.HarvestCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            HarvestCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="HarvestReplicationConfig"></a>

`HarvestReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Harvest.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `replication_start_date: str`
    :   UTC date and time in YYYY-MM-DDTHH:mm:ssZ format from which to start replicating data. Data before this date will not be replicated.

<a id="InvoiceItemCategoriesSearchData"></a>

`InvoiceItemCategoriesSearchData(**data: Any)`
:   Search result data for invoice_item_categories entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   When created

    `id: int | None`
    :   Unique identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Category name

    `updated_at: str | None`
    :   When last updated

    `use_as_expense: bool | None`
    :   Whether used as expense type

    `use_as_service: bool | None`
    :   Whether used as service type

<a id="InvoicesSearchData"></a>

`InvoicesSearchData(**data: Any)`
:   Search result data for invoices entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: float | None`
    :   Total amount

    `client: dict[str, typing.Any] | None`
    :   Client details

    `created_at: str | None`
    :   When created

    `currency: str | None`
    :   Currency

    `due_amount: float | None`
    :   Amount due

    `due_date: str | None`
    :   Due date

    `id: int | None`
    :   Unique identifier

    `issue_date: str | None`
    :   Issue date

    `model_config`
    :   The type of the None singleton.

    `number: str | None`
    :   Invoice number

    `state: str | None`
    :   Current state

    `subject: str | None`
    :   Subject

    `updated_at: str | None`
    :   When last updated

<a id="ProjectsSearchData"></a>

`ProjectsSearchData(**data: Any)`
:   Search result data for projects entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `budget: float | None`
    :   Budget amount

    `client: dict[str, typing.Any] | None`
    :   Client details

    `code: str | None`
    :   Project code

    `created_at: str | None`
    :   When created

    `hourly_rate: float | None`
    :   Hourly rate

    `id: int | None`
    :   Unique identifier

    `is_active: bool | None`
    :   Whether active

    `is_billable: bool | None`
    :   Whether billable

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Project name

    `starts_on: str | None`
    :   Start date

    `updated_at: str | None`
    :   When last updated

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
    :   When created

    `id: int | None`
    :   Unique identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Role name

    `updated_at: str | None`
    :   When last updated

    `user_ids: list[typing.Any] | None`
    :   User IDs with this role

<a id="TaskAssignmentsSearchData"></a>

`TaskAssignmentsSearchData(**data: Any)`
:   Search result data for task_assignments entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `billable: bool | None`
    :   Whether billable

    `created_at: str | None`
    :   When created

    `hourly_rate: float | None`
    :   Hourly rate

    `id: int | None`
    :   Unique identifier

    `is_active: bool | None`
    :   Whether active

    `model_config`
    :   The type of the None singleton.

    `project: dict[str, typing.Any] | None`
    :   Associated project

    `task: dict[str, typing.Any] | None`
    :   Associated task

    `updated_at: str | None`
    :   When last updated

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

    `billable_by_default: bool | None`
    :   Whether billable by default

    `created_at: str | None`
    :   When created

    `default_hourly_rate: float | None`
    :   Default hourly rate

    `id: int | None`
    :   Unique identifier

    `is_active: bool | None`
    :   Whether active

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Task name

    `updated_at: str | None`
    :   When last updated

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

    `billable: bool | None`
    :   Whether billable

    `client: dict[str, typing.Any] | None`
    :   Associated client

    `created_at: str | None`
    :   When created

    `hours: float | None`
    :   Hours logged

    `id: int | None`
    :   Unique identifier

    `is_billed: bool | None`
    :   Whether billed

    `model_config`
    :   The type of the None singleton.

    `notes: str | None`
    :   Notes

    `project: dict[str, typing.Any] | None`
    :   Associated project

    `spent_date: str | None`
    :   Date time was spent

    `task: dict[str, typing.Any] | None`
    :   Associated task

    `updated_at: str | None`
    :   When last updated

    `user: dict[str, typing.Any] | None`
    :   Associated user

<a id="TimeProjectsSearchData"></a>

`TimeProjectsSearchData(**data: Any)`
:   Search result data for time_projects entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `billable_amount: float | None`
    :   Total billable amount

    `billable_hours: float | None`
    :   Number of billable hours

    `client_id: int | None`
    :   Client identifier

    `client_name: str | None`
    :   Client name

    `currency: str | None`
    :   Currency code

    `model_config`
    :   The type of the None singleton.

    `project_id: int | None`
    :   Project identifier

    `project_name: str | None`
    :   Project name

    `total_hours: float | None`
    :   Total hours spent

<a id="TimeTasksSearchData"></a>

`TimeTasksSearchData(**data: Any)`
:   Search result data for time_tasks entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `billable_amount: float | None`
    :   Total billable amount

    `billable_hours: float | None`
    :   Number of billable hours

    `currency: str | None`
    :   Currency code

    `model_config`
    :   The type of the None singleton.

    `task_id: int | None`
    :   Task identifier

    `task_name: str | None`
    :   Task name

    `total_hours: float | None`
    :   Total hours spent

<a id="UserAssignmentsSearchData"></a>

`UserAssignmentsSearchData(**data: Any)`
:   Search result data for user_assignments entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `budget: float | None`
    :   Budget

    `created_at: str | None`
    :   When created

    `hourly_rate: float | None`
    :   Hourly rate

    `id: int | None`
    :   Unique identifier

    `is_active: bool | None`
    :   Whether active

    `is_project_manager: bool | None`
    :   Whether project manager

    `model_config`
    :   The type of the None singleton.

    `project: dict[str, typing.Any] | None`
    :   Associated project

    `updated_at: str | None`
    :   When last updated

    `user: dict[str, typing.Any] | None`
    :   Associated user

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

    `avatar_url: str | None`
    :   Avatar URL

    `cost_rate: float | None`
    :   Cost rate

    `created_at: str | None`
    :   When created

    `default_hourly_rate: float | None`
    :   Default hourly rate

    `email: str | None`
    :   Email address

    `first_name: str | None`
    :   First name

    `id: int | None`
    :   Unique identifier

    `is_active: bool | None`
    :   Whether active

    `is_contractor: bool | None`
    :   Whether contractor

    `last_name: str | None`
    :   Last name

    `model_config`
    :   The type of the None singleton.

    `roles: list[typing.Any] | None`
    :   Assigned roles

    `telephone: str | None`
    :   Phone number

    `timezone: str | None`
    :   Timezone

    `updated_at: str | None`
    :   When last updated

    `weekly_capacity: int | None`
    :   Weekly capacity in seconds