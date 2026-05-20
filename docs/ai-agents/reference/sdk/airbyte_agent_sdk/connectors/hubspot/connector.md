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
        - properties_createdate: Date the company was created
        - properties_domain: Company domain name
        - properties_hs_lastmodifieddate: Last modified date of the company
        - properties_hs_object_id: HubSpot object ID
        - properties_hubspot_owner_id: ID of the HubSpot owner assigned to this company
        - properties_name: Company name
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
        - archived: Boolean flag indicating whether the contact has been archived or deleted
        - companies: Associated company records linked to this contact
        - created_at: Timestamp indicating when the contact was first created in the system
        - id: Unique identifier for the contact record
        - properties: Key-value object storing all contact properties and their values.
        - properties_associatedcompanyid: ID of the associated company
        - properties_createdate: Date the contact was created
        - properties_email: Contact email address
        - properties_firstname: Contact first name
        - properties_hs_object_id: HubSpot object ID
        - properties_hubspot_owner_id: ID of the HubSpot owner assigned to this contact
        - properties_lastmodifieddate: Last modified date of the contact
        - properties_lastname: Contact last name
        - updated_at: Timestamp indicating when the contact record was last modified
        
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
        - properties_amount: Deal amount
        - properties_closedate: Expected close date of the deal
        - properties_createdate: Date the deal was created
        - properties_dealname: Deal name
        - properties_dealstage: Current deal stage
        - properties_hs_lastmodifieddate: Last modified date of the deal
        - properties_hs_object_id: HubSpot object ID
        - properties_hubspot_owner_id: ID of the HubSpot owner assigned to this deal
        - properties_pipeline: Deal pipeline
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

    `context_store_search(self, query: TicketsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[TicketsSearchData]`
    :   Search tickets records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TicketsSearchFilter):
        - archived: Indicates whether the ticket has been deleted and moved to the recycling bin
        - companies: Collection of company records associated with the ticket
        - contacts: Collection of contact records associated with the ticket
        - created_at: Timestamp when the ticket record was originally created
        - id: Unique identifier for the ticket record
        - properties: Object containing all property values for the ticket
        - properties_content: Ticket content/description
        - properties_createdate: Date the ticket was created
        - properties_hs_lastmodifieddate: Last modified date of the ticket
        - properties_hs_object_id: HubSpot object ID
        - properties_hs_pipeline: Ticket pipeline
        - properties_hs_pipeline_stage: Current pipeline stage of the ticket
        - properties_hs_ticket_category: Ticket category
        - properties_hs_ticket_priority: Ticket priority level
        - properties_subject: Ticket subject line
        - updated_at: Timestamp when the ticket record was last modified
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TicketsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

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