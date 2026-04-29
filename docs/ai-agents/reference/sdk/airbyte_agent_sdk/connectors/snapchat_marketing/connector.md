---
id: airbyte_agent_sdk-connectors-snapchat_marketing-connector
title: airbyte_agent_sdk.connectors.snapchat_marketing.connector
---

Module airbyte_agent_sdk.connectors.snapchat_marketing.connector
================================================================
Snapchat-Marketing connector.

Classes
-------

<a id="AdaccountsQuery"></a>

`AdaccountsQuery(connector: SnapchatMarketingConnector)`
:   Query class for Adaccounts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdaccountsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult[AdaccountsSearchData]`
    :   Search adaccounts records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdaccountsSearchFilter):
        - advertiser_organization_id: Advertiser organization ID
        - agency_representing_client: Whether the account is managed by an agency
        - billing_center_id: Billing center ID
        - billing_type: Billing type
        - client_paying_invoices: Whether the client pays invoices directly
        - created_at: Creation timestamp
        - currency: Account currency code
        - funding_source_ids: Associated funding source IDs
        - id: Unique ad account identifier
        - name: Ad account name
        - organization_id: Parent organization ID
        - regulations: Regulatory settings
        - status: Ad account status
        - timezone: Account timezone
        - type_: Ad account type
        - updated_at: Last update timestamp
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdaccountsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single ad account by ID
        
        Args:
            id: Ad Account ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, organization_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta[list[AdAccount], AdaccountsListResultMeta]`
    :   Returns ad accounts belonging to an organization
        
        Args:
            organization_id: Organization ID
            **kwargs: Additional parameters
        
        Returns:
            AdaccountsListResult

<a id="AdsQuery"></a>

`AdsQuery(connector: SnapchatMarketingConnector)`
:   Query class for Ads entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult[AdsSearchData]`
    :   Search ads records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdsSearchFilter):
        - ad_squad_id: Parent ad squad ID
        - created_at: Creation timestamp
        - creative_id: Associated creative ID
        - delivery_status: Delivery status messages
        - id: Unique ad identifier
        - name: Ad name
        - render_type: Render type
        - review_status: Review status
        - review_status_reasons: Reasons for review status
        - status: Ad status
        - type_: Ad type
        - updated_at: Last update timestamp
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single ad by ID
        
        Args:
            id: Ad ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, ad_account_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta[list[Ad], AdsListResultMeta]`
    :   Returns ads belonging to an ad account
        
        Args:
            ad_account_id: Ad Account ID
            **kwargs: Additional parameters
        
        Returns:
            AdsListResult

<a id="AdsquadsQuery"></a>

`AdsquadsQuery(connector: SnapchatMarketingConnector)`
:   Query class for Adsquads entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdsquadsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult[AdsquadsSearchData]`
    :   Search adsquads records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdsquadsSearchFilter):
        - auto_bid: Whether auto bidding is enabled
        - bid_strategy: Bid strategy
        - billing_event: Billing event type
        - campaign_id: Parent campaign ID
        - child_ad_type: Child ad type
        - created_at: Creation timestamp
        - creation_state: Creation state
        - daily_budget_micro: Daily budget in micro-currency
        - delivery_constraint: Delivery constraint
        - delivery_properties_version: Delivery properties version
        - delivery_status: Delivery status messages
        - end_time: Ad squad end time
        - event_sources: Event sources configuration
        - forced_view_setting: Forced view setting
        - id: Unique ad squad identifier
        - lifetime_budget_micro: Lifetime budget in micro-currency
        - name: Ad squad name
        - optimization_goal: Optimization goal
        - pacing_type: Pacing type
        - placement: Placement type
        - skadnetwork_properties: SKAdNetwork properties
        - start_time: Ad squad start time
        - status: Ad squad status
        - target_bid: Whether target bid is enabled
        - targeting: Targeting specification
        - targeting_reach_status: Targeting reach status
        - type_: Ad squad type
        - updated_at: Last update timestamp
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdsquadsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single ad squad by ID
        
        Args:
            id: Ad Squad ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, ad_account_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta[list[AdSquad], AdsquadsListResultMeta]`
    :   Returns ad squads belonging to an ad account
        
        Args:
            ad_account_id: Ad Account ID
            **kwargs: Additional parameters
        
        Returns:
            AdsquadsListResult

<a id="CampaignsQuery"></a>

`CampaignsQuery(connector: SnapchatMarketingConnector)`
:   Query class for Campaigns entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CampaignsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult[CampaignsSearchData]`
    :   Search campaigns records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CampaignsSearchFilter):
        - ad_account_id: Parent ad account ID
        - buy_model: Buy model type
        - created_at: Creation timestamp
        - creation_state: Creation state
        - delivery_status: Delivery status messages
        - id: Unique campaign identifier
        - name: Campaign name
        - objective: Campaign objective
        - start_time: Campaign start time
        - status: Campaign status
        - updated_at: Last update timestamp
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CampaignsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single campaign by ID
        
        Args:
            id: Campaign ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, ad_account_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]`
    :   Returns campaigns belonging to an ad account
        
        Args:
            ad_account_id: Ad Account ID
            **kwargs: Additional parameters
        
        Returns:
            CampaignsListResult

<a id="CreativesQuery"></a>

`CreativesQuery(connector: SnapchatMarketingConnector)`
:   Query class for Creatives entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CreativesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult[CreativesSearchData]`
    :   Search creatives records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CreativesSearchFilter):
        - ad_account_id: Parent ad account ID
        - ad_product: Ad product type
        - ad_to_place_properties: Ad-to-place properties
        - brand_name: Brand name displayed in the creative
        - call_to_action: Call to action text
        - created_at: Creation timestamp
        - forced_view_eligibility: Forced view eligibility status
        - headline: Creative headline
        - id: Unique creative identifier
        - name: Creative name
        - packaging_status: Packaging status
        - render_type: Render type
        - review_status: Review status
        - review_status_details: Details about the review status
        - shareable: Whether the creative is shareable
        - top_snap_crop_position: Top snap crop position
        - top_snap_media_id: Top snap media ID
        - type_: Creative type
        - updated_at: Last update timestamp
        - web_view_properties: Web view properties
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CreativesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single creative by ID
        
        Args:
            id: Creative ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, ad_account_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta[list[Creative], CreativesListResultMeta]`
    :   Returns creatives belonging to an ad account
        
        Args:
            ad_account_id: Ad Account ID
            **kwargs: Additional parameters
        
        Returns:
            CreativesListResult

<a id="MediaQuery"></a>

`MediaQuery(connector: SnapchatMarketingConnector)`
:   Query class for Media entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: MediaSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult[MediaSearchData]`
    :   Search media records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (MediaSearchFilter):
        - ad_account_id: Parent ad account ID
        - created_at: Creation timestamp
        - download_link: Download URL for the media
        - duration_in_seconds: Duration in seconds for video media
        - file_name: Original file name
        - file_size_in_bytes: File size in bytes
        - hash: Media file hash
        - id: Unique media identifier
        - image_metadata: Image-specific metadata
        - is_demo_media: Whether this is demo media
        - media_status: Media processing status
        - media_usages: Where the media is used
        - name: Media name
        - type_: Media type
        - updated_at: Last update timestamp
        - video_metadata: Video-specific metadata
        - visibility: Media visibility setting
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            MediaSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single media item by ID
        
        Args:
            id: Media ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, ad_account_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta[list[Media], MediaListResultMeta]`
    :   Returns media belonging to an ad account
        
        Args:
            ad_account_id: Ad Account ID
            **kwargs: Additional parameters
        
        Returns:
            MediaListResult

<a id="OrganizationsQuery"></a>

`OrganizationsQuery(connector: SnapchatMarketingConnector)`
:   Query class for Organizations entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: OrganizationsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult[OrganizationsSearchData]`
    :   Search organizations records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (OrganizationsSearchFilter):
        - accepted_term_version: Version of accepted terms
        - address_line_1: Street address
        - administrative_district_level_1: State or province
        - configuration_settings: Organization configuration settings
        - contact_email: Contact email address
        - contact_name: Contact person name
        - contact_phone: Contact phone number
        - contact_phone_optin: Whether the contact opted in for phone communications
        - country: Country code
        - created_by_caller: Whether the organization was created by the caller
        - created_at: Creation timestamp
        - id: Unique organization identifier
        - locality: City or locality
        - my_display_name: Display name of the authenticated user in the organization
        - my_invited_email: Email used to invite the authenticated user
        - my_member_id: Member ID of the authenticated user
        - name: Organization name
        - postal_code: Postal code
        - roles: Roles of the authenticated user in this organization
        - state: Organization state
        - type_: Organization type
        - updated_at: Last update timestamp
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            OrganizationsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single organization by ID
        
        Args:
            id: Organization ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta[list[Organization], OrganizationsListResultMeta]`
    :   Returns the organizations the authenticated user belongs to
        
        Returns:
            OrganizationsListResult

<a id="SegmentsQuery"></a>

`SegmentsQuery(connector: SnapchatMarketingConnector)`
:   Query class for Segments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SegmentsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult[SegmentsSearchData]`
    :   Search segments records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SegmentsSearchFilter):
        - ad_account_id: Parent ad account ID
        - approximate_number_users: Approximate number of users in the segment
        - created_at: Creation timestamp
        - description: Segment description
        - id: Unique segment identifier
        - name: Segment name
        - organization_id: Parent organization ID
        - retention_in_days: Data retention period in days
        - source_type: Segment source type
        - status: Segment status
        - targetable_status: Whether the segment is targetable
        - updated_at: Last update timestamp
        - upload_status: Upload processing status
        - visible_to: Visibility settings
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SegmentsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single audience segment by ID
        
        Args:
            id: Segment ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, ad_account_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta[list[Segment], SegmentsListResultMeta]`
    :   Returns audience segments belonging to an ad account
        
        Args:
            ad_account_id: Ad Account ID
            **kwargs: Additional parameters
        
        Returns:
            SegmentsListResult

<a id="SnapchatMarketingConnector"></a>

`SnapchatMarketingConnector(auth_config: SnapchatMarketingAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Snapchat-Marketing API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new snapchat-marketing connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., SnapchatMarketingAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = SnapchatMarketingConnector(auth_config=SnapchatMarketingAuthConfig(client_id="...", client_secret="...", refresh_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = SnapchatMarketingConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = SnapchatMarketingConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'SnapchatMarketingAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: "'SnapchatMarketingReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A SnapchatMarketingConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await SnapchatMarketingConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=SnapchatMarketingAuthConfig(client_id="...", client_secret="...", refresh_token="..."),
            )
        
            # With replication config (required for this connector):
            connector = await SnapchatMarketingConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=SnapchatMarketingAuthConfig(client_id="...", client_secret="...", refresh_token="..."),
                replication_config=SnapchatMarketingReplicationConfig(start_date="..."),
            )
        
            # With server-side OAuth:
            connector = await SnapchatMarketingConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
                replication_config=SnapchatMarketingReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: "'SnapchatMarketingReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            consent_url = await SnapchatMarketingConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Snapchat-Marketing Source",
                replication_config=SnapchatMarketingReplicationConfig(start_date="..."),
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @SnapchatMarketingConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @SnapchatMarketingConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await SnapchatMarketingConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            SnapchatMarketingCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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