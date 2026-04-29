---
id: airbyte_agent_sdk-connectors-pinterest-connector
title: airbyte_agent_sdk.connectors.pinterest.connector
---

Module airbyte_agent_sdk.connectors.pinterest.connector
=======================================================
Pinterest connector.

Classes
-------

<a id="AdAccountsQuery"></a>

`AdAccountsQuery(connector: PinterestConnector)`
:   Query class for AdAccounts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdAccountsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[AdAccountsSearchData]`
    :   Search ad_accounts records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdAccountsSearchFilter):
        - country: Country associated with the ad account
        - created_time: Timestamp when the ad account was created (Unix seconds)
        - currency: Currency used for billing
        - id: Unique identifier for the ad account
        - name: Name of the ad account
        - owner: Owner details of the ad account
        - permissions: Permissions assigned to the ad account
        - updated_time: Timestamp when the ad account was last updated (Unix seconds)
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdAccountsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, ad_account_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.pinterest.models.AdAccount`
    :   Get an ad account by ID.
        
        Args:
            ad_account_id: Unique identifier of the ad account.
            **kwargs: Additional parameters
        
        Returns:
            AdAccount

    `list(self, page_size: int | None = None, bookmark: str | None = None, include_shared_accounts: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[AdAccount], AdAccountsListResultMeta]`
    :   Get a list of the ad accounts that the authenticated user has access to.
        
        Args:
            page_size: Maximum number of items to include in a single page of the response.
            bookmark: Cursor value for paginating through results.
            include_shared_accounts: Include shared ad accounts.
            **kwargs: Additional parameters
        
        Returns:
            AdAccountsListResult

<a id="AdGroupsQuery"></a>

`AdGroupsQuery(connector: PinterestConnector)`
:   Query class for AdGroups entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdGroupsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[AdGroupsSearchData]`
    :   Search ad_groups records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdGroupsSearchFilter):
        - ad_account_id: Ad account ID
        - auto_targeting_enabled: Whether auto targeting is enabled
        - bid_in_micro_currency: Bid in microcurrency
        - bid_strategy_type: Bid strategy type
        - billable_event: Billable event type
        - budget_in_micro_currency: Budget in microcurrency
        - budget_type: Budget type
        - campaign_id: Parent campaign ID
        - conversion_learning_mode_type: oCPM learn mode type
        - created_time: Creation timestamp (Unix seconds)
        - end_time: End time (Unix seconds)
        - feed_profile_id: Feed profile ID
        - id: Ad group ID
        - lifetime_frequency_cap: Max impressions per user in 30 days
        - name: Ad group name
        - optimization_goal_metadata: Optimization goal metadata
        - pacing_delivery_type: Pacing delivery type
        - placement_group: Placement group
        - start_time: Start time (Unix seconds)
        - status: Entity status
        - summary_status: Summary status
        - targeting_spec: Targeting specifications
        - tracking_urls: Third-party tracking URLs
        - type_: Always 'adgroup'
        - updated_time: Last update timestamp (Unix seconds)
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdGroupsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, ad_account_id: str, page_size: int | None = None, bookmark: str | None = None, entity_statuses: list[str] | None = None, order: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[AdGroup], AdGroupsListResultMeta]`
    :   Get a list of ad groups in the specified ad account.
        
        Args:
            ad_account_id: Unique identifier of the ad account.
            page_size: Maximum number of items to include in a single page of the response.
            bookmark: Cursor value for paginating through results.
            entity_statuses: Filter by entity status.
            order: Sort order.
            **kwargs: Additional parameters
        
        Returns:
            AdGroupsListResult

<a id="AdsQuery"></a>

`AdsQuery(connector: PinterestConnector)`
:   Query class for Ads entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[AdsSearchData]`
    :   Search ads records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdsSearchFilter):
        - ad_account_id: Ad account ID
        - ad_group_id: Ad group ID
        - android_deep_link: Android deep link
        - campaign_id: Campaign ID
        - carousel_android_deep_links: Carousel Android deep links
        - carousel_destination_urls: Carousel destination URLs
        - carousel_ios_deep_links: Carousel iOS deep links
        - click_tracking_url: Click tracking URL
        - collection_items_destination_url_template: Template URL for collection items
        - created_time: Creation timestamp (Unix seconds)
        - creative_type: Creative type
        - destination_url: Main destination URL
        - id: Unique ad ID
        - ios_deep_link: iOS deep link
        - is_pin_deleted: Whether the original pin is deleted
        - is_removable: Whether the ad is removable
        - lead_form_id: Lead form ID
        - name: Ad name
        - pin_id: Associated pin ID
        - rejected_reasons: Rejection reasons
        - rejection_labels: Rejection text labels
        - review_status: Review status
        - status: Entity status
        - summary_status: Summary status
        - tracking_urls: Third-party tracking URLs
        - type_: Always 'pinpromotion'
        - updated_time: Last update timestamp (Unix seconds)
        - view_tracking_url: View tracking URL
        
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

    `list(self, ad_account_id: str, page_size: int | None = None, bookmark: str | None = None, entity_statuses: list[str] | None = None, order: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[Ad], AdsListResultMeta]`
    :   Get a list of ads in the specified ad account.
        
        Args:
            ad_account_id: Unique identifier of the ad account.
            page_size: Maximum number of items to include in a single page of the response.
            bookmark: Cursor value for paginating through results.
            entity_statuses: Filter by entity status.
            order: Sort order.
            **kwargs: Additional parameters
        
        Returns:
            AdsListResult

<a id="AudiencesQuery"></a>

`AudiencesQuery(connector: PinterestConnector)`
:   Query class for Audiences entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AudiencesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[AudiencesSearchData]`
    :   Search audiences records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AudiencesSearchFilter):
        - ad_account_id: Ad account ID
        - audience_type: Audience type
        - created_timestamp: Creation time (Unix seconds)
        - description: Audience description
        - id: Unique audience identifier
        - name: Audience name
        - rule: Audience targeting rules
        - size: Estimated audience size
        - status: Audience status
        - type_: Always 'audience'
        - updated_timestamp: Last update time (Unix seconds)
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AudiencesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, ad_account_id: str, page_size: int | None = None, bookmark: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[Audience], AudiencesListResultMeta]`
    :   Get a list of audiences for the specified ad account.
        
        Args:
            ad_account_id: Unique identifier of the ad account.
            page_size: Maximum number of items to include in a single page of the response.
            bookmark: Cursor value for paginating through results.
            **kwargs: Additional parameters
        
        Returns:
            AudiencesListResult

<a id="BoardPinsQuery"></a>

`BoardPinsQuery(connector: PinterestConnector)`
:   Query class for BoardPins entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: BoardPinsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[BoardPinsSearchData]`
    :   Search board_pins records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (BoardPinsSearchFilter):
        - alt_text: Alternate text for accessibility
        - board_id: Board the pin belongs to
        - board_owner: Board owner info
        - board_section_id: Section within the board
        - created_at: Timestamp when the pin was created
        - creative_type: Creative type
        - description: Pin description
        - dominant_color: Dominant color from the pin image
        - has_been_promoted: Whether the pin has been promoted
        - id: Unique pin identifier
        - is_owner: Whether the current user is the owner
        - is_standard: Whether the pin is a standard pin
        - link: URL link associated with the pin
        - media: Media content
        - parent_pin_id: Parent pin ID if this is a repin
        - pin_metrics: Pin metrics data
        - title: Pin title
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            BoardPinsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, board_id: str, page_size: int | None = None, bookmark: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[BoardPin], BoardPinsListResultMeta]`
    :   Get a list of pins on a specific board.
        
        Args:
            board_id: Unique identifier of the board.
            page_size: Maximum number of items to include in a single page of the response.
            bookmark: Cursor value for paginating through results.
            **kwargs: Additional parameters
        
        Returns:
            BoardPinsListResult

<a id="BoardSectionsQuery"></a>

`BoardSectionsQuery(connector: PinterestConnector)`
:   Query class for BoardSections entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: BoardSectionsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[BoardSectionsSearchData]`
    :   Search board_sections records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (BoardSectionsSearchFilter):
        - id: Unique identifier for the board section
        - name: Name of the board section
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            BoardSectionsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, board_id: str, page_size: int | None = None, bookmark: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[BoardSection], BoardSectionsListResultMeta]`
    :   Get a list of sections for a specific board.
        
        Args:
            board_id: Unique identifier of the board.
            page_size: Maximum number of items to include in a single page of the response.
            bookmark: Cursor value for paginating through results.
            **kwargs: Additional parameters
        
        Returns:
            BoardSectionsListResult

<a id="BoardsQuery"></a>

`BoardsQuery(connector: PinterestConnector)`
:   Query class for Boards entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: BoardsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[BoardsSearchData]`
    :   Search boards records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (BoardsSearchFilter):
        - board_pins_modified_at: Timestamp when pins on the board were last modified
        - collaborator_count: Number of collaborators
        - created_at: Timestamp when the board was created
        - description: Board description
        - follower_count: Number of followers
        - id: Unique identifier for the board
        - media: Media content for the board
        - name: Board name
        - owner: Board owner details
        - pin_count: Number of pins on the board
        - privacy: Board privacy setting
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            BoardsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, board_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.pinterest.models.Board`
    :   Get a board by ID.
        
        Args:
            board_id: Unique identifier of the board.
            **kwargs: Additional parameters
        
        Returns:
            Board

    `list(self, page_size: int | None = None, bookmark: str | None = None, privacy: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[Board], BoardsListResultMeta]`
    :   Get a list of the boards owned by the authenticated user.
        
        Args:
            page_size: Maximum number of items to include in a single page of the response.
            bookmark: Cursor value for paginating through results.
            privacy: Filter by board privacy setting.
            **kwargs: Additional parameters
        
        Returns:
            BoardsListResult

<a id="CampaignsQuery"></a>

`CampaignsQuery(connector: PinterestConnector)`
:   Query class for Campaigns entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CampaignsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[CampaignsSearchData]`
    :   Search campaigns records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CampaignsSearchFilter):
        - ad_account_id: Ad account ID
        - created_time: Creation timestamp (Unix seconds)
        - daily_spend_cap: Maximum daily spend in microcurrency
        - end_time: End timestamp (Unix seconds)
        - id: Campaign ID
        - is_campaign_budget_optimization: Whether CBO is enabled
        - is_flexible_daily_budgets: Whether flexible daily budgets are enabled
        - lifetime_spend_cap: Maximum lifetime spend in microcurrency
        - name: Campaign name
        - objective_type: Campaign objective type
        - order_line_id: Order line ID on invoice
        - start_time: Start timestamp (Unix seconds)
        - status: Entity status
        - summary_status: Summary status
        - tracking_urls: Third-party tracking URLs
        - type_: Always 'campaign'
        - updated_time: Last update timestamp (Unix seconds)
        
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

    `list(self, ad_account_id: str, page_size: int | None = None, bookmark: str | None = None, entity_statuses: list[str] | None = None, order: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]`
    :   Get a list of campaigns in the specified ad account.
        
        Args:
            ad_account_id: Unique identifier of the ad account.
            page_size: Maximum number of items to include in a single page of the response.
            bookmark: Cursor value for paginating through results.
            entity_statuses: Filter by entity status.
            order: Sort order.
            **kwargs: Additional parameters
        
        Returns:
            CampaignsListResult

<a id="CatalogsFeedsQuery"></a>

`CatalogsFeedsQuery(connector: PinterestConnector)`
:   Query class for CatalogsFeeds entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CatalogsFeedsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[CatalogsFeedsSearchData]`
    :   Search catalogs_feeds records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CatalogsFeedsSearchFilter):
        - catalog_type: Type of catalog
        - created_at: Timestamp when the feed was created
        - default_availability: Default availability status
        - default_country: Default country
        - default_currency: Default currency for pricing
        - default_locale: Default locale
        - format: Feed format
        - id: Unique feed identifier
        - location: URL where the feed is available
        - name: Feed name
        - preferred_processing_schedule: Preferred processing schedule
        - status: Feed status
        - updated_at: Timestamp when the feed was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CatalogsFeedsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, page_size: int | None = None, bookmark: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[CatalogsFeed], CatalogsFeedsListResultMeta]`
    :   Get a list of catalog feeds for the authenticated user.
        
        Args:
            page_size: Maximum number of items to include in a single page of the response.
            bookmark: Cursor value for paginating through results.
            **kwargs: Additional parameters
        
        Returns:
            CatalogsFeedsListResult

<a id="CatalogsProductGroupsQuery"></a>

`CatalogsProductGroupsQuery(connector: PinterestConnector)`
:   Query class for CatalogsProductGroups entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CatalogsProductGroupsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[CatalogsProductGroupsSearchData]`
    :   Search catalogs_product_groups records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CatalogsProductGroupsSearchFilter):
        - created_at: Creation timestamp (Unix seconds)
        - description: Product group description
        - feed_id: Associated feed ID
        - id: Unique product group identifier
        - is_featured: Whether the product group is featured
        - name: Product group name
        - status: Product group status
        - type_: Product group type
        - updated_at: Last update timestamp (Unix seconds)
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CatalogsProductGroupsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, page_size: int | None = None, bookmark: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[CatalogsProductGroup], CatalogsProductGroupsListResultMeta]`
    :   Get a list of catalog product groups for the authenticated user.
        
        Args:
            page_size: Maximum number of items to include in a single page of the response.
            bookmark: Cursor value for paginating through results.
            **kwargs: Additional parameters
        
        Returns:
            CatalogsProductGroupsListResult

<a id="CatalogsQuery"></a>

`CatalogsQuery(connector: PinterestConnector)`
:   Query class for Catalogs entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CatalogsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[CatalogsSearchData]`
    :   Search catalogs records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CatalogsSearchFilter):
        - catalog_type: Type of catalog
        - created_at: Timestamp when the catalog was created
        - id: Unique catalog identifier
        - name: Catalog name
        - updated_at: Timestamp when the catalog was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CatalogsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, page_size: int | None = None, bookmark: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[Catalog], CatalogsListResultMeta]`
    :   Get a list of catalogs for the authenticated user.
        
        Args:
            page_size: Maximum number of items to include in a single page of the response.
            bookmark: Cursor value for paginating through results.
            **kwargs: Additional parameters
        
        Returns:
            CatalogsListResult

<a id="ConversionTagsQuery"></a>

`ConversionTagsQuery(connector: PinterestConnector)`
:   Query class for ConversionTags entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ConversionTagsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[ConversionTagsSearchData]`
    :   Search conversion_tags records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ConversionTagsSearchFilter):
        - ad_account_id: Ad account ID
        - code_snippet: JavaScript code snippet for tracking
        - configs: Tag configurations
        - enhanced_match_status: Enhanced match status
        - id: Unique conversion tag identifier
        - last_fired_time_ms: Timestamp of last event fired (milliseconds)
        - name: Conversion tag name
        - status: Status
        - version: Version number
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ConversionTagsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, ad_account_id: str, page_size: int | None = None, bookmark: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[ConversionTag], ConversionTagsListResultMeta]`
    :   Get a list of conversion tags for the specified ad account.
        
        Args:
            ad_account_id: Unique identifier of the ad account.
            page_size: Maximum number of items to include in a single page of the response.
            bookmark: Cursor value for paginating through results.
            **kwargs: Additional parameters
        
        Returns:
            ConversionTagsListResult

<a id="CustomerListsQuery"></a>

`CustomerListsQuery(connector: PinterestConnector)`
:   Query class for CustomerLists entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CustomerListsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[CustomerListsSearchData]`
    :   Search customer_lists records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CustomerListsSearchFilter):
        - ad_account_id: Associated ad account ID
        - created_time: Creation time (Unix seconds)
        - id: Unique customer list identifier
        - name: Customer list name
        - num_batches: Total number of list updates
        - num_removed_user_records: Count of removed user records
        - num_uploaded_user_records: Count of uploaded user records
        - status: Status
        - type_: Always 'customerlist'
        - updated_time: Last update time (Unix seconds)
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CustomerListsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, ad_account_id: str, page_size: int | None = None, bookmark: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[CustomerList], CustomerListsListResultMeta]`
    :   Get a list of customer lists for the specified ad account.
        
        Args:
            ad_account_id: Unique identifier of the ad account.
            page_size: Maximum number of items to include in a single page of the response.
            bookmark: Cursor value for paginating through results.
            **kwargs: Additional parameters
        
        Returns:
            CustomerListsListResult

<a id="KeywordsQuery"></a>

`KeywordsQuery(connector: PinterestConnector)`
:   Query class for Keywords entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: KeywordsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[KeywordsSearchData]`
    :   Search keywords records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (KeywordsSearchFilter):
        - archived: Whether the keyword is archived
        - bid: Bid value in microcurrency
        - id: Unique keyword identifier
        - match_type: Match type
        - parent_id: Parent entity ID
        - parent_type: Parent entity type
        - type_: Always 'keyword'
        - value: Keyword text value
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            KeywordsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, ad_account_id: str, ad_group_id: str, page_size: int | None = None, bookmark: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[Keyword], KeywordsListResultMeta]`
    :   Get a list of keywords for the specified ad account. Requires an ad_group_id filter.
        
        Args:
            ad_account_id: Unique identifier of the ad account.
            ad_group_id: Ad group ID to filter keywords by.
            page_size: Maximum number of items to include in a single page of the response.
            bookmark: Cursor value for paginating through results.
            **kwargs: Additional parameters
        
        Returns:
            KeywordsListResult

<a id="PinterestConnector"></a>

`PinterestConnector(auth_config: PinterestAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Pinterest API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new pinterest connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., PinterestAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = PinterestConnector(auth_config=PinterestAuthConfig(refresh_token="...", client_id="...", client_secret="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = PinterestConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = PinterestConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'PinterestAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: "'PinterestReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A PinterestConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await PinterestConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=PinterestAuthConfig(refresh_token="...", client_id="...", client_secret="..."),
            )
        
            # With replication config (required for this connector):
            connector = await PinterestConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=PinterestAuthConfig(refresh_token="...", client_id="...", client_secret="..."),
                replication_config=PinterestReplicationConfig(start_date="..."),
            )
        
            # With server-side OAuth:
            connector = await PinterestConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
                replication_config=PinterestReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: "'PinterestReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            consent_url = await PinterestConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Pinterest Source",
                replication_config=PinterestReplicationConfig(start_date="..."),
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @PinterestConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @PinterestConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await PinterestConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.pinterest.models.PinterestCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            PinterestCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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