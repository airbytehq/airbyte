---
id: airbyte_agent_sdk-connectors-sendgrid-index
title: airbyte_agent_sdk.connectors.sendgrid.index
---

Module airbyte_agent_sdk.connectors.sendgrid
============================================
Sendgrid connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.sendgrid.connector
* airbyte_agent_sdk.connectors.sendgrid.connector_model
* airbyte_agent_sdk.connectors.sendgrid.models
* airbyte_agent_sdk.connectors.sendgrid.types

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

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[BlocksSearchData]
    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[BouncesSearchData]
    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[CampaignsSearchData]
    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[ContactsSearchData]
    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[GlobalSuppressionsSearchData]
    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[InvalidEmailsSearchData]
    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[ListsSearchData]
    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[SegmentsSearchData]
    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[SinglesendStatsSearchData]
    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[SinglesendsSearchData]
    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[SuppressionGroupMembersSearchData]
    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[SuppressionGroupsSearchData]
    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[TemplatesSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="BlocksSearchResult"></a>

`BlocksSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="BouncesSearchResult"></a>

`BouncesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CampaignsSearchResult"></a>

`CampaignsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="GlobalSuppressionsSearchResult"></a>

`GlobalSuppressionsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="InvalidEmailsSearchResult"></a>

`InvalidEmailsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ListsSearchResult"></a>

`ListsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SegmentsSearchResult"></a>

`SegmentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SinglesendStatsSearchResult"></a>

`SinglesendStatsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SinglesendsSearchResult"></a>

`SinglesendsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SuppressionGroupMembersSearchResult"></a>

`SuppressionGroupMembersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SuppressionGroupsSearchResult"></a>

`SuppressionGroupsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TemplatesSearchResult"></a>

`TemplatesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="BlocksSearchData"></a>

`BlocksSearchData(**data: Any)`
:   Search result data for blocks entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: int | None`
    :   Unix timestamp when the block occurred

    `email: str | None`
    :   The blocked email address

    `model_config`
    :   The type of the None singleton.

    `reason: str | None`
    :   The reason for the block

    `status: str | None`
    :   The status code for the block

<a id="BouncesSearchData"></a>

`BouncesSearchData(**data: Any)`
:   Search result data for bounces entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: int | None`
    :   Unix timestamp when the bounce occurred

    `email: str | None`
    :   The email address that bounced

    `model_config`
    :   The type of the None singleton.

    `reason: str | None`
    :   The reason for the bounce

    `status: str | None`
    :   The enhanced status code for the bounce

<a id="CampaignsSearchData"></a>

`CampaignsSearchData(**data: Any)`
:   Search result data for campaigns entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `channels: list[typing.Any] | None`
    :   Channels for this campaign

    `created_at: str | None`
    :   When the campaign was created

    `id: str | None`
    :   Unique campaign identifier

    `is_abtest: bool | None`
    :   Whether this campaign is an A/B test

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Campaign name

    `status: str | None`
    :   Campaign status

    `updated_at: str | None`
    :   When the campaign was last updated

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

    `address_line_1: str | None`
    :   Address line 1

    `address_line_2: str | None`
    :   Address line 2

    `alternate_emails: list[typing.Any] | None`
    :   Alternate email addresses

    `city: str | None`
    :   City

    `contact_id: str | None`
    :   Unique contact identifier used by Airbyte

    `country: str | None`
    :   Country

    `created_at: str | None`
    :   When the contact was created

    `custom_fields: dict[str, typing.Any] | None`
    :   Custom field values

    `email: str | None`
    :   Contact email address

    `facebook: str | None`
    :   Facebook ID

    `first_name: str | None`
    :   Contact first name

    `last_name: str | None`
    :   Contact last name

    `line: str | None`
    :   LINE ID

    `list_ids: list[typing.Any] | None`
    :   IDs of lists the contact belongs to

    `model_config`
    :   The type of the None singleton.

    `phone_number: str | None`
    :   Phone number

    `postal_code: str | None`
    :   Postal code

    `state_province_region: str | None`
    :   State, province, or region

    `unique_name: str | None`
    :   Unique name for the contact

    `updated_at: str | None`
    :   When the contact was last updated

    `whatsapp: str | None`
    :   WhatsApp number

<a id="GlobalSuppressionsSearchData"></a>

`GlobalSuppressionsSearchData(**data: Any)`
:   Search result data for global_suppressions entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: int | None`
    :   Unix timestamp when the global suppression was created

    `email: str | None`
    :   The globally suppressed email address

    `model_config`
    :   The type of the None singleton.

<a id="InvalidEmailsSearchData"></a>

`InvalidEmailsSearchData(**data: Any)`
:   Search result data for invalid_emails entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: int | None`
    :   Unix timestamp when the invalid email was recorded

    `email: str | None`
    :   The invalid email address

    `model_config`
    :   The type of the None singleton.

    `reason: str | None`
    :   The reason the email is invalid

<a id="ListsSearchData"></a>

`ListsSearchData(**data: Any)`
:   Search result data for lists entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `contact_count: int | None`
    :   Number of contacts in the list

    `id: str | None`
    :   Unique list identifier

    `metadata: dict[str, typing.Any] | None`
    :   Metadata about the list resource

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the list

<a id="SegmentsSearchData"></a>

`SegmentsSearchData(**data: Any)`
:   Search result data for segments entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `contacts_count: int | None`
    :   Number of contacts in the segment

    `created_at: str | None`
    :   When the segment was created

    `id: str | None`
    :   Unique segment identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Segment name

    `next_sample_update: str | None`
    :   When the next sample update will occur

    `parent_list_ids: list[typing.Any] | None`
    :   IDs of parent lists

    `query_version: str | None`
    :   Query version used

    `sample_updated_at: str | None`
    :   When the sample was last updated

    `status: dict[str, typing.Any] | None`
    :   Segment status details

    `updated_at: str | None`
    :   When the segment was last updated

<a id="SendgridAuthConfig"></a>

`SendgridAuthConfig(**data: Any)`
:   API Key Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_key: str`
    :   Your SendGrid API key (generated at https://app.sendgrid.com/settings/api_keys)

    `model_config`
    :   The type of the None singleton.

<a id="SendgridConnector"></a>

`SendgridConnector(auth_config: SendgridAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Sendgrid API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new sendgrid connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., SendgridAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = SendgridConnector(auth_config=SendgridAuthConfig(api_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = SendgridConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = SendgridConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'SendgridAuthConfig'", name: str | None = None, replication_config: "'SendgridReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A SendgridConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await SendgridConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=SendgridAuthConfig(api_key="..."),
            )
        
            # With replication config (required for this connector):
            connector = await SendgridConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=SendgridAuthConfig(api_key="..."),
                replication_config=SendgridReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @SendgridConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @SendgridConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await SendgridConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            SendgridCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="SendgridReplicationConfig"></a>

`SendgridReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from SendGrid.
    
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
    :   UTC date and time in the format 2017-01-25T00:00:00Z. Any data before this date will not be replicated.

<a id="SinglesendStatsSearchData"></a>

`SinglesendStatsSearchData(**data: Any)`
:   Search result data for singlesend_stats entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ab_phase: str | None`
    :   The A/B test phase

    `ab_variation: str | None`
    :   The A/B test variation

    `aggregation: str | None`
    :   The aggregation type

    `id: str | None`
    :   The single send ID

    `model_config`
    :   The type of the None singleton.

    `stats: dict[str, typing.Any] | None`
    :   Email statistics for the single send

<a id="SinglesendsSearchData"></a>

`SinglesendsSearchData(**data: Any)`
:   Search result data for singlesends entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `categories: list[typing.Any] | None`
    :   Categories associated with this single send

    `created_at: str | None`
    :   When the single send was created

    `id: str | None`
    :   Unique single send identifier

    `is_abtest: bool | None`
    :   Whether this is an A/B test

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Single send name

    `send_at: str | None`
    :   Scheduled send time

    `status: str | None`
    :   Current status: draft, scheduled, or triggered

    `updated_at: str | None`
    :   When the single send was last updated

<a id="SuppressionGroupMembersSearchData"></a>

`SuppressionGroupMembersSearchData(**data: Any)`
:   Search result data for suppression_group_members entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: int | None`
    :   Unix timestamp when the suppression was created

    `email: str | None`
    :   The suppressed email address

    `group_id: int | None`
    :   ID of the suppression group

    `group_name: str | None`
    :   Name of the suppression group

    `model_config`
    :   The type of the None singleton.

<a id="SuppressionGroupsSearchData"></a>

`SuppressionGroupsSearchData(**data: Any)`
:   Search result data for suppression_groups entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description: str | None`
    :   Description of the suppression group

    `id: int | None`
    :   Unique suppression group identifier

    `is_default: bool | None`
    :   Whether this is the default suppression group

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Suppression group name

    `unsubscribes: int | None`
    :   Number of unsubscribes in this group

<a id="TemplatesSearchData"></a>

`TemplatesSearchData(**data: Any)`
:   Search result data for templates entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `generation: str | None`
    :   Template generation (legacy or dynamic)

    `id: str | None`
    :   Unique template identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Template name

    `updated_at: str | None`
    :   When the template was last updated

    `versions: list[typing.Any] | None`
    :   Template versions