---
id: airbyte_agent_sdk-connectors-paypal_transaction-index
title: airbyte_agent_sdk.connectors.paypal_transaction.index
---

Module airbyte_agent_sdk.connectors.paypal_transaction
======================================================
Paypal-Transaction connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.paypal_transaction.connector
* airbyte_agent_sdk.connectors.paypal_transaction.connector_model
* airbyte_agent_sdk.connectors.paypal_transaction.models
* airbyte_agent_sdk.connectors.paypal_transaction.types

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

    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult[BalancesSearchData]
    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult[ListDisputesSearchData]
    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult[ListPaymentsSearchData]
    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult[ListProductsSearchData]
    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult[SearchInvoicesSearchData]
    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult[ShowProductDetailsSearchData]
    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult[TransactionsSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="BalancesSearchResult"></a>

`BalancesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ListDisputesSearchResult"></a>

`ListDisputesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ListPaymentsSearchResult"></a>

`ListPaymentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ListProductsSearchResult"></a>

`ListProductsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SearchInvoicesSearchResult"></a>

`SearchInvoicesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ShowProductDetailsSearchResult"></a>

`ShowProductDetailsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TransactionsSearchResult"></a>

`TransactionsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="BalancesSearchData"></a>

`BalancesSearchData(**data: Any)`
:   Search result data for balances entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | None`
    :   The unique identifier of the account.

    `as_of_time: str | None`
    :   The timestamp when the balances data was reported.

    `balances: list[typing.Any] | None`
    :   Object containing information about the account balances.

    `last_refresh_time: str | None`
    :   The timestamp when the balances data was last refreshed.

    `model_config`
    :   The type of the None singleton.

<a id="ListDisputesSearchData"></a>

`ListDisputesSearchData(**data: Any)`
:   Search result data for list_disputes entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `create_time: str | None`
    :   The timestamp when the dispute was created.

    `dispute_amount: dict[str, typing.Any] | None`
    :   Details about the disputed amount.

    `dispute_channel: str | None`
    :   The channel through which the dispute was initiated.

    `dispute_id: str | None`
    :   The unique identifier for the dispute.

    `dispute_life_cycle_stage: str | None`
    :   The stage in the life cycle of the dispute.

    `dispute_state: str | None`
    :   The current state of the dispute.

    `disputed_transactions: list[typing.Any] | None`
    :   Details of transactions involved in the dispute.

    `links: list[typing.Any] | None`
    :   Links related to the dispute.

    `model_config`
    :   The type of the None singleton.

    `outcome: str | None`
    :   The outcome of the dispute resolution.

    `reason: str | None`
    :   The reason for the dispute.

    `status: str | None`
    :   The current status of the dispute.

    `update_time: str | None`
    :   The timestamp when the dispute was last updated.

    `updated_time_cut: str | None`
    :   The cut-off timestamp for the last update.

<a id="ListPaymentsSearchData"></a>

`ListPaymentsSearchData(**data: Any)`
:   Search result data for list_payments entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cart: str | None`
    :   Details of the cart associated with the payment.

    `create_time: str | None`
    :   The date and time when the payment was created.

    `id: str | None`
    :   Unique identifier for the payment.

    `intent: str | None`
    :   The intention or purpose behind the payment.

    `links: list[typing.Any] | None`
    :   Collection of links related to the payment

    `model_config`
    :   The type of the None singleton.

    `payer: dict[str, typing.Any] | None`
    :   Details of the payer who made the payment

    `state: str | None`
    :   The state of the payment.

    `transactions: list[typing.Any] | None`
    :   List of transactions associated with the payment

    `update_time: str | None`
    :   The date and time when the payment was last updated.

<a id="ListProductsSearchData"></a>

`ListProductsSearchData(**data: Any)`
:   Search result data for list_products entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `create_time: str | None`
    :   The time when the product was created

    `description: str | None`
    :   Detailed information or features of the product

    `id: str | None`
    :   Unique identifier for the product

    `links: list[typing.Any] | None`
    :   List of links related to the fetched products.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The name or title of the product

<a id="PaypalTransactionAuthConfig"></a>

`PaypalTransactionAuthConfig(**data: Any)`
:   PayPal OAuth2 Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str | None`
    :   OAuth2 access token obtained via client credentials grant. Use the PayPal token endpoint with your client_id and client_secret to obtain this.

    `client_id: str`
    :   The Client ID of your PayPal developer application.

    `client_secret: str`
    :   The Client Secret of your PayPal developer application.

    `model_config`
    :   The type of the None singleton.

<a id="PaypalTransactionConnector"></a>

`PaypalTransactionConnector(auth_config: PaypalTransactionAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Paypal-Transaction API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new paypal-transaction connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., PaypalTransactionAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = PaypalTransactionConnector(auth_config=PaypalTransactionAuthConfig(client_id="...", client_secret="...", access_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = PaypalTransactionConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = PaypalTransactionConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'PaypalTransactionAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: "'PaypalTransactionReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A PaypalTransactionConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await PaypalTransactionConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=PaypalTransactionAuthConfig(client_id="...", client_secret="...", access_token="..."),
            )
        
            # With replication config (required for this connector):
            connector = await PaypalTransactionConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=PaypalTransactionAuthConfig(client_id="...", client_secret="...", access_token="..."),
                replication_config=PaypalTransactionReplicationConfig(start_date="..."),
            )
        
            # With server-side OAuth:
            connector = await PaypalTransactionConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
                replication_config=PaypalTransactionReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: "'PaypalTransactionReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            consent_url = await PaypalTransactionConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Paypal-Transaction Source",
                replication_config=PaypalTransactionReplicationConfig(start_date="..."),
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @PaypalTransactionConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @PaypalTransactionConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await PaypalTransactionConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            PaypalTransactionCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="PaypalTransactionReplicationConfig"></a>

`PaypalTransactionReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from PayPal.
    
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
    :   Start date for data extraction in ISO 8601 format. Date must be in range from 3 years till 12 hours before present time.

<a id="SearchInvoicesSearchData"></a>

`SearchInvoicesSearchData(**data: Any)`
:   Search result data for search_invoices entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `additional_recipients: list[typing.Any] | None`
    :   List of additional recipients associated with the invoice

    `amount: dict[str, typing.Any] | None`
    :   Detailed breakdown of the invoice amount

    `configuration: dict[str, typing.Any] | None`
    :   Configuration settings related to the invoice

    `detail: dict[str, typing.Any] | None`
    :   Detailed information about the invoice

    `due_amount: dict[str, typing.Any] | None`
    :   Due amount remaining to be paid for the invoice

    `gratuity: dict[str, typing.Any] | None`
    :   Gratuity amount included in the invoice

    `id: str | None`
    :   Unique identifier of the invoice

    `invoicer: dict[str, typing.Any] | None`
    :   Information about the invoicer associated with the invoice

    `last_update_time: str | None`
    :   Date and time of the last update made to the invoice

    `links: list[typing.Any] | None`
    :   Links associated with the invoice

    `model_config`
    :   The type of the None singleton.

    `payments: dict[str, typing.Any] | None`
    :   Payment transactions associated with the invoice

    `primary_recipients: list[typing.Any] | None`
    :   Primary recipients associated with the invoice

    `refunds: dict[str, typing.Any] | None`
    :   Refund transactions associated with the invoice

    `status: str | None`
    :   Current status of the invoice

<a id="ShowProductDetailsSearchData"></a>

`ShowProductDetailsSearchData(**data: Any)`
:   Search result data for show_product_details entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `category: str | None`
    :   The category to which the product belongs

    `create_time: str | None`
    :   The date and time when the product was created

    `description: str | None`
    :   The detailed description of the product

    `home_url: str | None`
    :   The URL for the home page of the product

    `id: str | None`
    :   The unique identifier for the product

    `image_url: str | None`
    :   The URL to the image representing the product

    `links: list[typing.Any] | None`
    :   Contains links related to the product details.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The name of the product

    `type_: str | None`
    :   The type or category of the product

    `update_time: str | None`
    :   The date and time when the product was last updated

<a id="TransactionsSearchData"></a>

`TransactionsSearchData(**data: Any)`
:   Search result data for transactions entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `auction_info: dict[str, typing.Any] | None`
    :   Information related to an auction

    `cart_info: dict[str, typing.Any] | None`
    :   Details of items in the cart

    `incentive_info: dict[str, typing.Any] | None`
    :   Details of any incentives applied

    `model_config`
    :   The type of the None singleton.

    `payer_info: dict[str, typing.Any] | None`
    :   Information about the payer

    `shipping_info: dict[str, typing.Any] | None`
    :   Shipping information

    `store_info: dict[str, typing.Any] | None`
    :   Information about the store

    `transaction_id: str | None`
    :   Unique ID of the transaction

    `transaction_info: dict[str, typing.Any] | None`
    :   Detailed information about the transaction

    `transaction_initiation_date: str | None`
    :   Date and time when the transaction was initiated

    `transaction_updated_date: str | None`
    :   Date and time when the transaction was last updated