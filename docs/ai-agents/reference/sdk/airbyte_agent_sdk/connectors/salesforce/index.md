---
id: airbyte_agent_sdk-connectors-salesforce-index
title: airbyte_agent_sdk.connectors.salesforce.index
---

Module airbyte_agent_sdk.connectors.salesforce
==============================================
Salesforce connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.salesforce.connector
* airbyte_agent_sdk.connectors.salesforce.connector_model
* airbyte_agent_sdk.connectors.salesforce.models
* airbyte_agent_sdk.connectors.salesforce.types

Classes
-------

<a id="AccountsSearchData"></a>

`AccountsSearchData(**data: Any)`
:   Search result data for accounts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_source: str | None`
    :   Source of the account record (e.g., Web, Referral)

    `billing_address: dict[str, typing.Any] | None`
    :   Complete billing address as a compound field

    `billing_city: str | None`
    :   City portion of the billing address

    `billing_country: str | None`
    :   Country portion of the billing address

    `billing_postal_code: str | None`
    :   Postal code portion of the billing address

    `billing_state: str | None`
    :   State or province portion of the billing address

    `billing_street: str | None`
    :   Street address portion of the billing address

    `created_by_id: str | None`
    :   ID of the user who created this account

    `created_date: str | None`
    :   Date and time when the account was created

    `description: str | None`
    :   Text description of the account

    `id: str`
    :   Unique identifier for the account record

    `industry: str | None`
    :   Primary business industry of the account

    `is_deleted: bool | None`
    :   Whether the account has been moved to the Recycle Bin

    `last_activity_date: str | None`
    :   Date of the last activity associated with this account

    `last_modified_by_id: str | None`
    :   ID of the user who last modified this account

    `last_modified_date: str | None`
    :   Date and time when the account was last modified

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the account or company

    `number_of_employees: int | None`
    :   Number of employees at the account

    `owner_id: str | None`
    :   ID of the user who owns this account

    `parent_id: str | None`
    :   ID of the parent account, if this is a subsidiary

    `phone: str | None`
    :   Primary phone number for the account

    `shipping_address: dict[str, typing.Any] | None`
    :   Complete shipping address as a compound field

    `shipping_city: str | None`
    :   City portion of the shipping address

    `shipping_country: str | None`
    :   Country portion of the shipping address

    `shipping_postal_code: str | None`
    :   Postal code portion of the shipping address

    `shipping_state: str | None`
    :   State or province portion of the shipping address

    `shipping_street: str | None`
    :   Street address portion of the shipping address

    `system_modstamp: str | None`
    :   System timestamp when the record was last modified

    `type_: str | None`
    :   Type of account (e.g., Customer, Partner, Competitor)

    `website: str | None`
    :   Website URL for the account

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

    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult[AccountsSearchData]
    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult[ContactsSearchData]
    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult[LeadsSearchData]
    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult[OpportunitiesSearchData]
    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult[OpportunityStagesSearchData]
    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult[TasksSearchData]
    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult[UsersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="AccountsSearchResult"></a>

`AccountsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="LeadsSearchResult"></a>

`LeadsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="OpportunitiesSearchResult"></a>

`OpportunitiesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="OpportunityStagesSearchResult"></a>

`OpportunityStagesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

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

    `account_id: str | None`
    :   ID of the account this contact is associated with

    `created_by_id: str | None`
    :   ID of the user who created this contact

    `created_date: str | None`
    :   Date and time when the contact was created

    `department: str | None`
    :   Department within the account where the contact works

    `email: str | None`
    :   Email address of the contact

    `first_name: str | None`
    :   First name of the contact

    `id: str`
    :   Unique identifier for the contact record

    `is_deleted: bool | None`
    :   Whether the contact has been moved to the Recycle Bin

    `last_activity_date: str | None`
    :   Date of the last activity associated with this contact

    `last_modified_by_id: str | None`
    :   ID of the user who last modified this contact

    `last_modified_date: str | None`
    :   Date and time when the contact was last modified

    `last_name: str | None`
    :   Last name of the contact

    `lead_source: str | None`
    :   Source from which this contact originated

    `mailing_address: dict[str, typing.Any] | None`
    :   Complete mailing address as a compound field

    `mailing_city: str | None`
    :   City portion of the mailing address

    `mailing_country: str | None`
    :   Country portion of the mailing address

    `mailing_postal_code: str | None`
    :   Postal code portion of the mailing address

    `mailing_state: str | None`
    :   State or province portion of the mailing address

    `mailing_street: str | None`
    :   Street address portion of the mailing address

    `mobile_phone: str | None`
    :   Mobile phone number of the contact

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Full name of the contact (read-only, concatenation of first and last name)

    `owner_id: str | None`
    :   ID of the user who owns this contact

    `phone: str | None`
    :   Business phone number of the contact

    `reports_to_id: str | None`
    :   ID of the contact this contact reports to

    `system_modstamp: str | None`
    :   System timestamp when the record was last modified

    `title: str | None`
    :   Job title of the contact

<a id="LeadsSearchData"></a>

`LeadsSearchData(**data: Any)`
:   Search result data for leads entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address: dict[str, typing.Any] | None`
    :   Complete address as a compound field

    `city: str | None`
    :   City portion of the address

    `company: str | None`
    :   Company or organization the lead works for

    `converted_account_id: str | None`
    :   ID of the account created when lead was converted

    `converted_contact_id: str | None`
    :   ID of the contact created when lead was converted

    `converted_date: str | None`
    :   Date when the lead was converted

    `converted_opportunity_id: str | None`
    :   ID of the opportunity created when lead was converted

    `country: str | None`
    :   Country portion of the address

    `created_by_id: str | None`
    :   ID of the user who created this lead

    `created_date: str | None`
    :   Date and time when the lead was created

    `email: str | None`
    :   Email address of the lead

    `first_name: str | None`
    :   First name of the lead

    `id: str`
    :   Unique identifier for the lead record

    `industry: str | None`
    :   Industry the lead's company operates in

    `is_converted: bool | None`
    :   Whether the lead has been converted to an account, contact, and opportunity

    `is_deleted: bool | None`
    :   Whether the lead has been moved to the Recycle Bin

    `last_activity_date: str | None`
    :   Date of the last activity associated with this lead

    `last_modified_by_id: str | None`
    :   ID of the user who last modified this lead

    `last_modified_date: str | None`
    :   Date and time when the lead was last modified

    `last_name: str | None`
    :   Last name of the lead

    `lead_source: str | None`
    :   Source from which this lead originated

    `mobile_phone: str | None`
    :   Mobile phone number of the lead

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Full name of the lead (read-only, concatenation of first and last name)

    `number_of_employees: int | None`
    :   Number of employees at the lead's company

    `owner_id: str | None`
    :   ID of the user who owns this lead

    `phone: str | None`
    :   Phone number of the lead

    `postal_code: str | None`
    :   Postal code portion of the address

    `rating: str | None`
    :   Rating of the lead (e.g., Hot, Warm, Cold)

    `state: str | None`
    :   State or province portion of the address

    `status: str | None`
    :   Current status of the lead in the sales process

    `street: str | None`
    :   Street address portion of the address

    `system_modstamp: str | None`
    :   System timestamp when the record was last modified

    `title: str | None`
    :   Job title of the lead

    `website: str | None`
    :   Website URL for the lead's company

<a id="OpportunitiesSearchData"></a>

`OpportunitiesSearchData(**data: Any)`
:   Search result data for opportunities entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | None`
    :   ID of the account associated with this opportunity

    `amount: float | None`
    :   Estimated total sale amount

    `campaign_id: str | None`
    :   ID of the campaign that generated this opportunity

    `close_date: str | None`
    :   Expected close date for the opportunity

    `contact_id: str | None`
    :   ID of the primary contact for this opportunity

    `created_by_id: str | None`
    :   ID of the user who created this opportunity

    `created_date: str | None`
    :   Date and time when the opportunity was created

    `description: str | None`
    :   Text description of the opportunity

    `expected_revenue: float | None`
    :   Expected revenue based on amount and probability

    `forecast_category: str | None`
    :   Forecast category for this opportunity

    `forecast_category_name: str | None`
    :   Name of the forecast category

    `id: str`
    :   Unique identifier for the opportunity record

    `is_closed: bool | None`
    :   Whether the opportunity is closed

    `is_deleted: bool | None`
    :   Whether the opportunity has been moved to the Recycle Bin

    `is_won: bool | None`
    :   Whether the opportunity was won

    `last_activity_date: str | None`
    :   Date of the last activity associated with this opportunity

    `last_modified_by_id: str | None`
    :   ID of the user who last modified this opportunity

    `last_modified_date: str | None`
    :   Date and time when the opportunity was last modified

    `lead_source: str | None`
    :   Source from which this opportunity originated

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the opportunity

    `next_step: str | None`
    :   Description of the next step in closing the opportunity

    `owner_id: str | None`
    :   ID of the user who owns this opportunity

    `probability: float | None`
    :   Likelihood of closing the opportunity (percentage)

    `stage_name: str | None`
    :   Current stage of the opportunity in the sales process

    `system_modstamp: str | None`
    :   System timestamp when the record was last modified

    `type_: str | None`
    :   Type of opportunity (e.g., New Business, Existing Business)

<a id="OpportunityStagesSearchData"></a>

`OpportunityStagesSearchData(**data: Any)`
:   Search result data for opportunity_stages entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_name: str | None`
    :   API name of the stage used in code and integrations

    `created_by_id: str | None`
    :   ID of the user who created this stage

    `created_date: str | None`
    :   Date and time when the stage was created

    `default_probability: float | None`
    :   Default probability percentage for opportunities at this stage

    `description: str | None`
    :   Description of the stage

    `forecast_category: str | None`
    :   Forecast category for opportunities at this stage

    `forecast_category_name: str | None`
    :   Display name of the forecast category

    `id: str`
    :   Unique identifier for the opportunity stage record

    `is_active: bool | None`
    :   Whether the stage is currently active and can be used

    `is_closed: bool | None`
    :   Whether opportunities at this stage are considered closed

    `is_won: bool | None`
    :   Whether opportunities at this stage are considered won

    `last_modified_by_id: str | None`
    :   ID of the user who last modified this stage

    `last_modified_date: str | None`
    :   Date and time when the stage was last modified

    `master_label: str | None`
    :   Display label for the stage

    `model_config`
    :   The type of the None singleton.

    `sort_order: int | None`
    :   Order in which the stage appears in the sales process

    `system_modstamp: str | None`
    :   System timestamp when the record was last modified

<a id="SalesforceAuthConfig"></a>

`SalesforceAuthConfig(**data: Any)`
:   Salesforce OAuth 2.0
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `client_id: str | None`
    :   Connected App Consumer Key

    `client_secret: str | None`
    :   Connected App Consumer Secret

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str`
    :   OAuth refresh token for automatic token renewal

<a id="SalesforceConnector"></a>

`SalesforceConnector(auth_config: SalesforceAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, instance_url: str | None = None)`
:   Type-safe Salesforce API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new salesforce connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., SalesforceAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)            instance_url: Your Salesforce instance URL (e.g., https://na1.salesforce.com)
    Examples:
        # Local mode (direct API calls)
        connector = SalesforceConnector(auth_config=SalesforceAuthConfig(refresh_token="...", client_id="...", client_secret="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = SalesforceConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = SalesforceConnector(
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
            @SalesforceConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @SalesforceConnector.tool_utils(update_docstring=False, max_output_chars=None)
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @SalesforceConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
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

    `check(self) ‑> airbyte_agent_sdk.connectors.salesforce.models.SalesforceCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            SalesforceCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'get', 'api_search', 'download', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
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

    `account_id: str | None`
    :   ID of the account associated with this task

    `activity_date: str | None`
    :   Due date for the task

    `call_disposition: str | None`
    :   Result of the call, if this task represents a call

    `call_duration_in_seconds: int | None`
    :   Duration of the call in seconds

    `call_type: str | None`
    :   Type of call (Inbound, Outbound, Internal)

    `completed_date_time: str | None`
    :   Date and time when the task was completed

    `created_by_id: str | None`
    :   ID of the user who created this task

    `created_date: str | None`
    :   Date and time when the task was created

    `description: str | None`
    :   Text description or notes about the task

    `id: str`
    :   Unique identifier for the task record

    `is_closed: bool | None`
    :   Whether the task has been completed

    `is_deleted: bool | None`
    :   Whether the task has been moved to the Recycle Bin

    `is_high_priority: bool | None`
    :   Whether the task is marked as high priority

    `last_modified_by_id: str | None`
    :   ID of the user who last modified this task

    `last_modified_date: str | None`
    :   Date and time when the task was last modified

    `model_config`
    :   The type of the None singleton.

    `owner_id: str | None`
    :   ID of the user who owns this task

    `priority: str | None`
    :   Priority level of the task (High, Normal, Low)

    `status: str | None`
    :   Current status of the task

    `subject: str | None`
    :   Subject or title of the task

    `system_modstamp: str | None`
    :   System timestamp when the record was last modified

    `task_subtype: str | None`
    :   Subtype of the task (e.g., Call, Email, Task)

    `type_: str | None`
    :   Type of task

    `what_id: str | None`
    :   ID of the related object (Account, Opportunity, etc.)

    `who_id: str | None`
    :   ID of the related person (Contact or Lead)

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

    `account_id: str | None`
    :   ID of the account associated with this user (for portal users)

    `alias: str | None`
    :   Short name used to identify the user in list views and reports

    `city: str | None`
    :   City portion of the user's address

    `company_name: str | None`
    :   Name of the user's company

    `contact_id: str | None`
    :   ID of the contact associated with this user (for portal users)

    `country: str | None`
    :   Country portion of the user's address

    `created_by_id: str | None`
    :   ID of the user who created this user record

    `created_date: str | None`
    :   Date and time when the user was created

    `department: str | None`
    :   Department within the organization

    `division: str | None`
    :   Division within the organization

    `email: str | None`
    :   Email address of the user

    `employee_number: str | None`
    :   Employee number or ID assigned by the organization

    `first_name: str | None`
    :   First name of the user

    `id: str`
    :   Unique identifier for the user record

    `is_active: bool | None`
    :   Whether the user is active and can log in

    `last_login_date: str | None`
    :   Date and time of the user's most recent login

    `last_modified_by_id: str | None`
    :   ID of the user who last modified this user record

    `last_modified_date: str | None`
    :   Date and time when the user was last modified

    `last_name: str | None`
    :   Last name of the user

    `manager_id: str | None`
    :   ID of the user's manager

    `mobile_phone: str | None`
    :   Mobile phone number of the user

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Full name of the user

    `phone: str | None`
    :   Business phone number of the user

    `postal_code: str | None`
    :   Postal code portion of the user's address

    `profile_id: str | None`
    :   ID of the user's profile

    `state: str | None`
    :   State or province portion of the user's address

    `street: str | None`
    :   Street address of the user

    `system_modstamp: str | None`
    :   System timestamp when the record was last modified

    `title: str | None`
    :   Job title of the user

    `user_role_id: str | None`
    :   ID of the user's role in the organization

    `user_type: str | None`
    :   Type of user license (e.g., Standard, PowerPartner)

    `username: str | None`
    :   Username for logging into Salesforce (unique across all orgs)