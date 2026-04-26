---
id: airbyte_agent_sdk-connectors-amazon_ads-connector
title: airbyte_agent_sdk.connectors.amazon_ads.connector
---

Module airbyte_agent_sdk.connectors.amazon_ads.connector
========================================================
Amazon-Ads connector.

Classes
-------

<a id="AmazonAdsConnector"></a>

`AmazonAdsConnector(auth_config: AmazonAdsAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, region: str | None = None)`
:   Type-safe Amazon-Ads API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
            Initialize a new amazon-ads connector instance.
    
            Supports both local and hosted execution modes:
            - Local mode: Provide connector-specific auth config (e.g., AmazonAdsAuthConfig)
            - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
            Args:
                auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
                on_token_refresh: Optional callback for OAuth2 token refresh persistence.
                    Called with new_tokens dict when tokens are refreshed. Can be sync or async.
                    Example: lambda tokens: save_to_database(tokens)            region: The Amazon Ads API endpoint URL based on region:
    - NA (North America): https://advertising-api.amazon.com
    - EU (Europe): https://advertising-api-eu.amazon.com
    - FE (Far East): https://advertising-api-fe.amazon.com
    
            Examples:
                # Local mode (direct API calls)
                connector = AmazonAdsConnector(auth_config=AmazonAdsAuthConfig(client_id="...", client_secret="...", refresh_token="..."))
                # Hosted mode with explicit connector_id (no lookup needed)
                connector = AmazonAdsConnector(
                    auth_config=AirbyteAuthConfig(
                        airbyte_client_id="client_abc123",
                        airbyte_client_secret="secret_xyz789",
                        connector_id="existing-source-uuid"
                    )
                )
    
                # Hosted mode with lookup by workspace_name
                connector = AmazonAdsConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'AmazonAdsAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None)`
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
            A AmazonAdsConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await AmazonAdsConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=AmazonAdsAuthConfig(client_id="...", client_secret="...", refresh_token="..."),
            )
        
            # With server-side OAuth:
            connector = await AmazonAdsConnector.create(
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
            consent_url = await AmazonAdsConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Amazon-Ads Source",
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @AmazonAdsConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @AmazonAdsConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await AmazonAdsConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            AmazonAdsCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="PortfoliosQuery"></a>

`PortfoliosQuery(connector: AmazonAdsConnector)`
:   Query class for Portfolios entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, portfolio_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.Portfolio`
    :   Retrieves a single portfolio by its ID using the v2 API.
        
        
        Args:
            portfolio_id: The unique identifier of the portfolio
            **kwargs: Additional parameters
        
        Returns:
            Portfolio

    `list(self, include_extended_data_fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], PortfoliosListResultMeta]`
    :   Returns a list of portfolios for the specified profile. Portfolios are used to
        group campaigns together for organizational and budget management purposes.
        
        
                Args:
                    include_extended_data_fields: Whether to include extended data fields in the response
                    **kwargs: Additional parameters
        
                Returns:
                    PortfoliosListResult

<a id="ProfilesQuery"></a>

`ProfilesQuery(connector: AmazonAdsConnector)`
:   Query class for Profiles entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ProfilesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AirbyteSearchResult[ProfilesSearchData]`
    :   Search profiles records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ProfilesSearchFilter):
        - account_info: 
        - country_code: 
        - currency_code: 
        - daily_budget: 
        - profile_id: 
        - timezone: 
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ProfilesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, profile_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.Profile`
    :   Retrieves a single advertising profile by its ID. The profile contains
        information about the advertiser's account in a specific marketplace.
        
        
                Args:
                    profile_id: The unique identifier of the profile
                    **kwargs: Additional parameters
        
                Returns:
                    Profile

    `list(self, profile_type_filter: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult[list[Profile]]`
    :   Returns a list of advertising profiles associated with the authenticated user.
        Profiles represent an advertiser's account in a specific marketplace. Advertisers
        may have a single profile if they advertise in only one marketplace, or a separate
        profile for each marketplace if they advertise regionally or globally.
        
        
                Args:
                    profile_type_filter: Filter profiles by type. Comma-separated list of profile types.
        Valid values: seller, vendor, agency
        
                    **kwargs: Additional parameters
        
                Returns:
                    ProfilesListResult

<a id="SponsoredBrandsAdGroupsQuery"></a>

`SponsoredBrandsAdGroupsQuery(connector: AmazonAdsConnector)`
:   Query class for SponsoredBrandsAdGroups entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, state_filter: SponsoredBrandsAdGroupsListParamsStatefilter | None = None, max_results: int | None = None, next_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredBrandsAdGroupsListResultMeta]`
    :   Returns a list of sponsored brands ad groups for the specified profile.
        Ad groups organize ads and targeting within a Sponsored Brands campaign.
        
        
                Args:
                    state_filter: Parameter stateFilter
                    max_results: Maximum number of results to return
                    next_token: Token for pagination
                    **kwargs: Additional parameters
        
                Returns:
                    SponsoredBrandsAdGroupsListResult

<a id="SponsoredBrandsCampaignsQuery"></a>

`SponsoredBrandsCampaignsQuery(connector: AmazonAdsConnector)`
:   Query class for SponsoredBrandsCampaigns entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, state_filter: SponsoredBrandsCampaignsListParamsStatefilter | None = None, max_results: int | None = None, next_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredBrandsCampaignsListResultMeta]`
    :   Returns a list of sponsored brands campaigns for the specified profile.
        Sponsored Brands campaigns help drive discovery and sales with creative ad experiences.
        
        
                Args:
                    state_filter: Parameter stateFilter
                    max_results: Maximum number of results to return
                    next_token: Token for pagination
                    **kwargs: Additional parameters
        
                Returns:
                    SponsoredBrandsCampaignsListResult

<a id="SponsoredProductAdGroupsQuery"></a>

`SponsoredProductAdGroupsQuery(connector: AmazonAdsConnector)`
:   Query class for SponsoredProductAdGroups entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, state_filter: SponsoredProductAdGroupsListParamsStatefilter | None = None, max_results: int | None = None, next_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductAdGroupsListResultMeta]`
    :   Returns a list of sponsored product ad groups for the specified profile.
        Ad groups are used to organize ads and targeting within a campaign.
        
        
                Args:
                    state_filter: Parameter stateFilter
                    max_results: Maximum number of results to return
                    next_token: Token for pagination
                    **kwargs: Additional parameters
        
                Returns:
                    SponsoredProductAdGroupsListResult

<a id="SponsoredProductCampaignsQuery"></a>

`SponsoredProductCampaignsQuery(connector: AmazonAdsConnector)`
:   Query class for SponsoredProductCampaigns entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, campaign_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.SponsoredProductCampaign`
    :   Retrieves a single sponsored product campaign by its ID using the v2 API.
        
        
        Args:
            campaign_id: The unique identifier of the campaign
            **kwargs: Additional parameters
        
        Returns:
            SponsoredProductCampaign

    `list(self, state_filter: SponsoredProductCampaignsListParamsStatefilter | None = None, max_results: int | None = None, next_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductCampaignsListResultMeta]`
    :   Returns a list of sponsored product campaigns for the specified profile.
        Sponsored Products campaigns promote individual product listings on Amazon.
        
        
                Args:
                    state_filter: Parameter stateFilter
                    max_results: Maximum number of results to return
                    next_token: Token for pagination
                    **kwargs: Additional parameters
        
                Returns:
                    SponsoredProductCampaignsListResult

<a id="SponsoredProductKeywordsQuery"></a>

`SponsoredProductKeywordsQuery(connector: AmazonAdsConnector)`
:   Query class for SponsoredProductKeywords entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, state_filter: SponsoredProductKeywordsListParamsStatefilter | None = None, max_results: int | None = None, next_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductKeywordsListResultMeta]`
    :   Returns a list of sponsored product keywords for the specified profile.
        Keywords are used in manual targeting campaigns to match shopper search queries.
        
        
                Args:
                    state_filter: Parameter stateFilter
                    max_results: Maximum number of results to return
                    next_token: Token for pagination
                    **kwargs: Additional parameters
        
                Returns:
                    SponsoredProductKeywordsListResult

<a id="SponsoredProductNegativeKeywordsQuery"></a>

`SponsoredProductNegativeKeywordsQuery(connector: AmazonAdsConnector)`
:   Query class for SponsoredProductNegativeKeywords entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, state_filter: SponsoredProductNegativeKeywordsListParamsStatefilter | None = None, max_results: int | None = None, next_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductNegativeKeywordsListResultMeta]`
    :   Returns a list of sponsored product negative keywords for the specified profile.
        Negative keywords prevent ads from showing for specific search terms.
        
        
                Args:
                    state_filter: Parameter stateFilter
                    max_results: Maximum number of results to return
                    next_token: Token for pagination
                    **kwargs: Additional parameters
        
                Returns:
                    SponsoredProductNegativeKeywordsListResult

<a id="SponsoredProductNegativeTargetsQuery"></a>

`SponsoredProductNegativeTargetsQuery(connector: AmazonAdsConnector)`
:   Query class for SponsoredProductNegativeTargets entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, state_filter: SponsoredProductNegativeTargetsListParamsStatefilter | None = None, max_results: int | None = None, next_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductNegativeTargetsListResultMeta]`
    :   Returns a list of sponsored product negative targeting clauses for the specified profile.
        Negative targeting clauses exclude specific products or categories from targeting.
        
        
                Args:
                    state_filter: Parameter stateFilter
                    max_results: Maximum number of results to return
                    next_token: Token for pagination
                    **kwargs: Additional parameters
        
                Returns:
                    SponsoredProductNegativeTargetsListResult

<a id="SponsoredProductProductAdsQuery"></a>

`SponsoredProductProductAdsQuery(connector: AmazonAdsConnector)`
:   Query class for SponsoredProductProductAds entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, state_filter: SponsoredProductProductAdsListParamsStatefilter | None = None, max_results: int | None = None, next_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductProductAdsListResultMeta]`
    :   Returns a list of sponsored product ads for the specified profile.
        Product ads associate an advertised product with an ad group.
        
        
                Args:
                    state_filter: Parameter stateFilter
                    max_results: Maximum number of results to return
                    next_token: Token for pagination
                    **kwargs: Additional parameters
        
                Returns:
                    SponsoredProductProductAdsListResult

<a id="SponsoredProductTargetsQuery"></a>

`SponsoredProductTargetsQuery(connector: AmazonAdsConnector)`
:   Query class for SponsoredProductTargets entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, state_filter: SponsoredProductTargetsListParamsStatefilter | None = None, max_results: int | None = None, next_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductTargetsListResultMeta]`
    :   Returns a list of sponsored product targeting clauses for the specified profile.
        Targeting clauses define product or category targeting for ad groups.
        
        
                Args:
                    state_filter: Parameter stateFilter
                    max_results: Maximum number of results to return
                    next_token: Token for pagination
                    **kwargs: Additional parameters
        
                Returns:
                    SponsoredProductTargetsListResult