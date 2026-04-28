---
id: airbyte_agent_sdk-connectors-hubspot-connector
title: airbyte_agent_sdk.connectors.hubspot.connector
---

Module airbyte_agent_sdk.connectors.hubspot.connector
=====================================================
Hubspot connector.

Classes
-------

<a id="CompaniesQuery"></a>

`CompaniesQuery(connector: HubspotConnector)`
:   Query class for Companies entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, filter_groups: list[CompaniesApiSearchParamsFiltergroupsItem] | None = None, properties: list[str] | None = None, limit: int | None = None, after: str | None = None, sorts: list[CompaniesApiSearchParamsSortsItem] | None = None, query: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Company], CompaniesApiSearchResultMeta]`
    :   Search for companies by filtering on properties, searching through associations, and sorting results.
        
        Args:
            filter_groups: Up to 6 groups of filters defining additional query criteria.
            properties: A list of property names to include in the response.
            limit: Maximum number of results to return
            after: A paging cursor token for retrieving subsequent pages.
            sorts: Sort criteria
            query: The search query string, up to 3000 characters.
            **kwargs: Additional parameters
        
        Returns:
            CompaniesApiSearchResult

    `context_store_search(self, query: CompaniesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[CompaniesSearchData]`
    :   Search companies records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CompaniesSearchFilter):
        - archived: Indicates whether the company has been deleted and moved to the recycling bin
        - contacts: Associated contact records linked to this company
        - created_at: Timestamp when the company record was created
        - id: Unique identifier for the company record
        - properties: Object containing all property values for the company
        - updated_at: Timestamp when the company record was last modified
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CompaniesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, company_id: str, properties: str | None = None, properties_with_history: str | None = None, associations: str | None = None, id_property: str | None = None, archived: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.hubspot.models.Company`
    :   Get a single company by ID
        
        Args:
            company_id: Company ID
            properties: A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored.
            properties_with_history: A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored.
            associations: A comma separated list of object types to retrieve associated IDs for. If any of the specified associations do not exist, they will be ignored.
            id_property: The name of a property whose values are unique for this object.
            archived: Whether to return only results that have been archived.
            **kwargs: Additional parameters
        
        Returns:
            Company

    `list(self, limit: int | None = None, after: str | None = None, associations: str | None = None, properties: str | None = None, properties_with_history: str | None = None, archived: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Company], CompaniesListResultMeta]`
    :   Retrieve all companies, using query parameters to control the information that gets returned.
        
        Args:
            limit: The maximum number of results to display per page.
            after: The paging cursor token of the last successfully read resource will be returned as the paging.next.after JSON property of a paged response containing more results.
            associations: A comma separated list of associated object types to include in the response. Valid values are contacts, deals, tickets, and custom object type IDs or fully qualified names (e.g., "p12345_cars").
            properties: A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored.
            properties_with_history: A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored. Usage of this parameter will reduce the maximum number of companies that can be read by a single request.
            archived: Whether to return only results that have been archived.
            **kwargs: Additional parameters
        
        Returns:
            CompaniesListResult

<a id="ContactsQuery"></a>

`ContactsQuery(connector: HubspotConnector)`
:   Query class for Contacts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, filter_groups: list[ContactsApiSearchParamsFiltergroupsItem] | None = None, properties: list[str] | None = None, limit: int | None = None, after: str | None = None, sorts: list[ContactsApiSearchParamsSortsItem] | None = None, query: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Contact], ContactsApiSearchResultMeta]`
    :   Search for contacts by filtering on properties, searching through associations, and sorting results.
        
        Args:
            filter_groups: Up to 6 groups of filters defining additional query criteria.
            properties: A list of property names to include in the response.
            limit: Maximum number of results to return
            after: A paging cursor token for retrieving subsequent pages.
            sorts: Sort criteria
            query: The search query string, up to 3000 characters.
            **kwargs: Additional parameters
        
        Returns:
            ContactsApiSearchResult

    `context_store_search(self, query: ContactsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[ContactsSearchData]`
    :   Search contacts records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ContactsSearchFilter):
        - archived: Boolean flag indicating whether the contact has been archived or deleted.
        - companies: Associated company records linked to this contact.
        - created_at: Timestamp indicating when the contact was first created in the system.
        - id: Unique identifier for the contact record.
        - properties: Key-value object storing all contact properties and their values.
        - updated_at: Timestamp indicating when the contact record was last modified.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ContactsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, contact_id: str, properties: str | None = None, properties_with_history: str | None = None, associations: str | None = None, id_property: str | None = None, archived: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.hubspot.models.Contact`
    :   Get a single contact by ID
        
        Args:
            contact_id: Contact ID
            properties: A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored.
            properties_with_history: A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored.
            associations: A comma separated list of object types to retrieve associated IDs for. If any of the specified associations do not exist, they will be ignored.
            id_property: The name of a property whose values are unique for this object.
            archived: Whether to return only results that have been archived.
            **kwargs: Additional parameters
        
        Returns:
            Contact

    `list(self, limit: int | None = None, after: str | None = None, associations: str | None = None, properties: str | None = None, properties_with_history: str | None = None, archived: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Contact], ContactsListResultMeta]`
    :   Returns a paginated list of contacts
        
        Args:
            limit: The maximum number of results to display per page.
            after: The paging cursor token of the last successfully read resource will be returned as the paging.next.after JSON property of a paged response containing more results.
            associations: A comma separated list of associated object types to include in the response. Valid values are contacts, deals, tickets, and custom object type IDs or fully qualified names (e.g., "p12345_cars").
            properties: A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored.
            properties_with_history: A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored. Usage of this parameter will reduce the maximum number of companies that can be read by a single request.
            archived: Whether to return only results that have been archived.
            **kwargs: Additional parameters
        
        Returns:
            ContactsListResult

<a id="DealsQuery"></a>

`DealsQuery(connector: HubspotConnector)`
:   Query class for Deals entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, filter_groups: list[DealsApiSearchParamsFiltergroupsItem] | None = None, properties: list[str] | None = None, limit: int | None = None, after: str | None = None, sorts: list[DealsApiSearchParamsSortsItem] | None = None, query: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Deal], DealsApiSearchResultMeta]`
    :   Search deals with filters and sorting
        
        Args:
            filter_groups: Up to 6 groups of filters defining additional query criteria.
            properties: A list of property names to include in the response.
            limit: Maximum number of results to return
            after: A paging cursor token for retrieving subsequent pages.
            sorts: Sort criteria
            query: The search query string, up to 3000 characters.
            **kwargs: Additional parameters
        
        Returns:
            DealsApiSearchResult

    `context_store_search(self, query: DealsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[DealsSearchData]`
    :   Search deals records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (DealsSearchFilter):
        - archived: Indicates whether the deal has been deleted and moved to the recycling bin
        - companies: Collection of company records associated with the deal
        - contacts: Collection of contact records associated with the deal
        - created_at: Timestamp when the deal record was originally created
        - id: Unique identifier for the deal record
        - line_items: Collection of product line items associated with the deal
        - properties: Key-value object containing all deal properties and custom fields
        - updated_at: Timestamp when the deal record was last modified
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            DealsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, deal_id: str, properties: str | None = None, properties_with_history: str | None = None, associations: str | None = None, id_property: str | None = None, archived: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.hubspot.models.Deal`
    :   Get a single deal by ID
        
        Args:
            deal_id: Deal ID
            properties: A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored.
            properties_with_history: A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored.
            associations: A comma separated list of object types to retrieve associated IDs for. If any of the specified associations do not exist, they will be ignored.
            id_property: The name of a property whose values are unique for this object.
            archived: Whether to return only results that have been archived.
            **kwargs: Additional parameters
        
        Returns:
            Deal

    `list(self, limit: int | None = None, after: str | None = None, associations: str | None = None, properties: str | None = None, properties_with_history: str | None = None, archived: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Deal], DealsListResultMeta]`
    :   Returns a paginated list of deals
        
        Args:
            limit: The maximum number of results to display per page.
            after: The paging cursor token of the last successfully read resource will be returned as the paging.next.after JSON property of a paged response containing more results.
            associations: A comma separated list of associated object types to include in the response. Valid values are contacts, deals, tickets, and custom object type IDs or fully qualified names (e.g., "p12345_cars").
            properties: A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored.
            properties_with_history: A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored. Usage of this parameter will reduce the maximum number of companies that can be read by a single request.
            archived: Whether to return only results that have been archived.
            **kwargs: Additional parameters
        
        Returns:
            DealsListResult

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

    `configure_oauth_app_parameters(*, airbyte_config: AirbyteAuthConfig, credentials: HubspotOAuthCredentials | None) ‑> None`
    :   Configure or remove OAuth app credentials for your organization.
        
        When credentials are provided, replaces the default Airbyte-managed OAuth
        app credentials with your own. After calling this, all OAuth flows for
        this connector in your organization will use the provided credentials.
        
        When credentials are None, removes any existing override so the
        organization reverts to the default Airbyte-managed OAuth app.
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials.
            credentials: Your OAuth app credentials (HubspotOAuthCredentials), or None to remove the override.
        
        Example:
            await HubspotConnector.configure_oauth_app_parameters(
                airbyte_config=AirbyteAuthConfig(
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                credentials=HubspotOAuthCredentials(
                    client_id="...",
                    client_secret="...",
                ),
            )
        
            await HubspotConnector.configure_oauth_app_parameters(
                airbyte_config=AirbyteAuthConfig(
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                credentials=None,
            )

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'HubspotAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None)`
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
            A HubspotConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await HubspotConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=HubspotAuthConfig(client_id="...", client_secret="...", refresh_token="...", access_token="..."),
            )
        
            # With server-side OAuth:
            connector = await HubspotConnector.create(
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
            consent_url = await HubspotConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Hubspot Source",
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @HubspotConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @HubspotConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await HubspotConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

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

    `execute(self, entity: str, action: "Literal['list', 'get', 'api_search', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
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

<a id="ObjectsQuery"></a>

`ObjectsQuery(connector: HubspotConnector)`
:   Query class for Objects entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, object_type: str, object_id: str, properties: str | None = None, archived: bool | None = None, associations: str | None = None, id_property: str | None = None, properties_with_history: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.hubspot.models.CRMObject`
    :   Read an Object identified by \{objectId\}. \{objectId\} refers to the internal object ID by default, or optionally any unique property value as specified by the idProperty query param. Control what is returned via the properties query param.
        
        Args:
            object_type: Object type ID or fully qualified name
            object_id: Object record ID
            properties: A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored.
            archived: Whether to return only results that have been archived.
            associations: A comma separated list of object types to retrieve associated IDs for. If any of the specified associations do not exist, they will be ignored.
            id_property: The name of a property whose values are unique for this object.
            properties_with_history: A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored.
            **kwargs: Additional parameters
        
        Returns:
            CRMObject

    `list(self, object_type: str, limit: int | None = None, after: str | None = None, properties: str | None = None, archived: bool | None = None, associations: str | None = None, properties_with_history: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[CRMObject], ObjectsListResultMeta]`
    :   Read a page of objects. Control what is returned via the properties query param.
        
        Args:
            object_type: Object type ID or fully qualified name (e.g., "cars" or "p12345_cars")
            limit: The maximum number of results to display per page.
            after: The paging cursor token of the last successfully read resource will be returned as the `paging.next.after` JSON property of a paged response containing more results.
            properties: A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored.
            archived: Whether to return only results that have been archived.
            associations: A comma separated list of object types to retrieve associated IDs for. If any of the specified associations do not exist, they will be ignored.
            properties_with_history: A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored.
            **kwargs: Additional parameters
        
        Returns:
            ObjectsListResult

<a id="SchemasQuery"></a>

`SchemasQuery(connector: HubspotConnector)`
:   Query class for Schemas entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, object_type: str, **kwargs) ‑> airbyte_agent_sdk.connectors.hubspot.models.Schema`
    :   Get the schema for a specific custom object type
        
        Args:
            object_type: Fully qualified name or object type ID of your schema.
            **kwargs: Additional parameters
        
        Returns:
            Schema

    `list(self, archived: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResult[list[Schema]]`
    :   Returns all custom object schemas to discover available custom objects
        
        Args:
            archived: Whether to return only results that have been archived.
            **kwargs: Additional parameters
        
        Returns:
            SchemasListResult

<a id="TicketsQuery"></a>

`TicketsQuery(connector: HubspotConnector)`
:   Query class for Tickets entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, filter_groups: list[TicketsApiSearchParamsFiltergroupsItem] | None = None, properties: list[str] | None = None, limit: int | None = None, after: str | None = None, sorts: list[TicketsApiSearchParamsSortsItem] | None = None, query: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Ticket], TicketsApiSearchResultMeta]`
    :   Search for tickets by filtering on properties, searching through associations, and sorting results.
        
        Args:
            filter_groups: Up to 6 groups of filters defining additional query criteria.
            properties: A list of property names to include in the response.
            limit: Maximum number of results to return
            after: A paging cursor token for retrieving subsequent pages.
            sorts: Sort criteria
            query: The search query string, up to 3000 characters.
            **kwargs: Additional parameters
        
        Returns:
            TicketsApiSearchResult

    `get(self, ticket_id: str, properties: str | None = None, properties_with_history: str | None = None, associations: str | None = None, id_property: str | None = None, archived: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.hubspot.models.Ticket`
    :   Get a single ticket by ID
        
        Args:
            ticket_id: Ticket ID
            properties: A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored.
            properties_with_history: A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored.
            associations: A comma separated list of object types to retrieve associated IDs for. If any of the specified associations do not exist, they will be ignored.
            id_property: The name of a property whose values are unique for this object.
            archived: Whether to return only results that have been archived.
            **kwargs: Additional parameters
        
        Returns:
            Ticket

    `list(self, limit: int | None = None, after: str | None = None, associations: str | None = None, properties: str | None = None, properties_with_history: str | None = None, archived: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Ticket], TicketsListResultMeta]`
    :   Returns a paginated list of tickets
        
        Args:
            limit: The maximum number of results to display per page.
            after: The paging cursor token of the last successfully read resource will be returned as the paging.next.after JSON property of a paged response containing more results.
            associations: A comma separated list of associated object types to include in the response. Valid values are contacts, deals, tickets, and custom object type IDs or fully qualified names (e.g., "p12345_cars").
            properties: A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored.
            properties_with_history: A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored. Usage of this parameter will reduce the maximum number of companies that can be read by a single request.
            archived: Whether to return only results that have been archived.
            **kwargs: Additional parameters
        
        Returns:
            TicketsListResult