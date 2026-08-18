---
id: airbyte_agent_sdk-connectors-shopify-connector
title: airbyte_agent_sdk.connectors.shopify.connector
---

Module airbyte_agent_sdk.connectors.shopify.connector
=====================================================
Shopify connector.

Classes
-------

<a id="AbandonedCheckoutsQuery"></a>

`AbandonedCheckoutsQuery(connector: ShopifyConnector)`
:   Query class for AbandonedCheckouts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AbandonedCheckoutsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[AbandonedCheckoutsSearchData]`
    :   Search abandoned_checkouts records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AbandonedCheckoutsSearchFilter):
        - id: Unique identifier for the abandoned checkout
        - token: Unique token identifying the checkout
        - email: Email address provided for the checkout
        - phone: Phone number provided for the checkout
        - name: Shopify-assigned display name for the checkout (e.g. `#C12345`)
        - currency: ISO 4217 currency code for the checkout totals
        - total_price: Total price of the checkout in the shop's currency
        - created_at: ISO 8601 timestamp when the checkout was created
        - updated_at: ISO 8601 timestamp when the checkout was last updated
        - completed_at: ISO 8601 timestamp when the checkout was completed, if applicable
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AbandonedCheckoutsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, limit: int | None = None, since_id: int | None = None, created_at_min: str | None = None, created_at_max: str | None = None, updated_at_min: str | None = None, updated_at_max: str | None = None, status: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[AbandonedCheckout], AbandonedCheckoutsListResultMeta]`
    :   Returns a list of abandoned checkouts
        
        Args:
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            created_at_min: Show checkouts created after date (ISO 8601 format)
            created_at_max: Show checkouts created before date (ISO 8601 format)
            updated_at_min: Show checkouts last updated after date (ISO 8601 format)
            updated_at_max: Show checkouts last updated before date (ISO 8601 format)
            status: Filter checkouts by status
            **kwargs: Additional parameters
        
        Returns:
            AbandonedCheckoutsListResult

<a id="ArticlesQuery"></a>

`ArticlesQuery(connector: ShopifyConnector)`
:   Query class for Articles entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ArticlesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[ArticlesSearchData]`
    :   Search articles records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ArticlesSearchFilter):
        - id: Unique identifier for the article
        - title: Title of the article
        - handle: URL-friendly handle for the article
        - author: Name of the author of the article
        - blog_id: Identifier of the blog the article belongs to
        - body_html: HTML content of the article body
        - summary_html: Summary of the article in HTML
        - tags: Comma-separated list of tags for the article
        - published_at: ISO 8601 timestamp when the article was published
        - created_at: ISO 8601 timestamp when the article was created
        - updated_at: ISO 8601 timestamp when the article was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ArticlesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, article: ArticlesCreateParamsArticle, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ArticleCreatePayload`
    :   Creates a new blog article via GraphQL mutation.
        
        
        Args:
            article: Parameter article
            **kwargs: Additional parameters
        
        Returns:
            ArticleCreatePayload

    `delete(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ArticleDeletePayload`
    :   Deletes a blog article via GraphQL mutation.
        
        
        Args:
            id: The GraphQL GID of the article to delete
            **kwargs: Additional parameters
        
        Returns:
            ArticleDeletePayload

    `get(self, blog_id: str, article_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.Article`
    :   Retrieves a single article by ID from a blog
        
        Args:
            blog_id: The blog ID
            article_id: The article ID
            **kwargs: Additional parameters
        
        Returns:
            Article

    `list(self, blog_id: str, limit: int | None = None, since_id: int | None = None, created_at_min: str | None = None, created_at_max: str | None = None, updated_at_min: str | None = None, updated_at_max: str | None = None, published_status: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Article], ArticlesListResultMeta]`
    :   Returns a list of articles from a specific blog
        
        Args:
            blog_id: The blog ID
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            created_at_min: Show articles created after date (ISO 8601 format)
            created_at_max: Show articles created before date (ISO 8601 format)
            updated_at_min: Show articles last updated after date (ISO 8601 format)
            updated_at_max: Show articles last updated before date (ISO 8601 format)
            published_status: Filter by published status (published, unpublished, any)
            **kwargs: Additional parameters
        
        Returns:
            ArticlesListResult

    `update(self, article: ArticlesUpdateParamsArticle, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ArticleUpdatePayload`
    :   Updates an existing blog article via GraphQL mutation.
        
        
        Args:
            id: The GraphQL GID of the article to update
            article: Parameter article
            **kwargs: Additional parameters
        
        Returns:
            ArticleUpdatePayload

<a id="BalanceTransactionsQuery"></a>

`BalanceTransactionsQuery(connector: ShopifyConnector)`
:   Query class for BalanceTransactions entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: BalanceTransactionsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[BalanceTransactionsSearchData]`
    :   Search balance_transactions records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (BalanceTransactionsSearchFilter):
        - id: Unique identifier of the balance transaction
        - type_: Type of the transaction (charge, refund, dispute, reserve, adjustment, credit, debit, payout, etc.)
        - amount: Gross amount of the transaction
        - fee: Total fees deducted from the transaction
        - net: Net amount of the transaction
        - currency: ISO 4217 currency code of the transaction
        - payout_id: Identifier of the payout the transaction was paid out in
        - payout_status: Status of the associated payout
        - source_type: Type of the resource that led to this transaction
        - source_order_id: Identifier of the source order, if applicable
        - processed_at: ISO 8601 timestamp when the transaction was processed
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            BalanceTransactionsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, limit: int | None = None, since_id: int | None = None, payout_id: int | None = None, payout_status: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[BalanceTransaction], BalanceTransactionsListResultMeta]`
    :   Returns a list of Shopify Payments balance transactions
        
        Args:
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            payout_id: Filter to transactions in a specific payout
            payout_status: Filter by payout status
            **kwargs: Additional parameters
        
        Returns:
            BalanceTransactionsListResult

<a id="BlogsQuery"></a>

`BlogsQuery(connector: ShopifyConnector)`
:   Query class for Blogs entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: BlogsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[BlogsSearchData]`
    :   Search blogs records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (BlogsSearchFilter):
        - id: Unique identifier for the blog
        - title: Title of the blog
        - handle: URL-friendly handle for the blog
        - commentable: Whether readers can post comments (no, moderate, yes)
        - tags: Comma-separated tags from the blog's articles
        - created_at: ISO 8601 timestamp when the blog was created
        - updated_at: ISO 8601 timestamp when the blog was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            BlogsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, blog: BlogsCreateParamsBlog, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.BlogCreatePayload`
    :   Creates a new blog on the online store via GraphQL mutation.
        
        
        Args:
            blog: Parameter blog
            **kwargs: Additional parameters
        
        Returns:
            BlogCreatePayload

    `delete(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.BlogDeletePayload`
    :   Deletes a blog from the online store via GraphQL mutation.
        
        
        Args:
            id: The GraphQL GID of the blog to delete
            **kwargs: Additional parameters
        
        Returns:
            BlogDeletePayload

    `get(self, blog_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.Blog`
    :   Retrieves a single blog by ID
        
        Args:
            blog_id: The blog ID
            **kwargs: Additional parameters
        
        Returns:
            Blog

    `list(self, limit: int | None = None, since_id: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Blog], BlogsListResultMeta]`
    :   Returns a list of blogs for the store
        
        Args:
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            **kwargs: Additional parameters
        
        Returns:
            BlogsListResult

    `update(self, blog: BlogsUpdateParamsBlog, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.BlogUpdatePayload`
    :   Updates an existing blog via GraphQL mutation.
        
        
        Args:
            id: The GraphQL GID of the blog to update
            blog: Parameter blog
            **kwargs: Additional parameters
        
        Returns:
            BlogUpdatePayload

<a id="CollectsQuery"></a>

`CollectsQuery(connector: ShopifyConnector)`
:   Query class for Collects entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CollectsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[CollectsSearchData]`
    :   Search collects records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CollectsSearchFilter):
        - id: Unique identifier for the collect
        - collection_id: Identifier of the collection the product belongs to
        - product_id: Identifier of the product in the collection
        - position: Position of the product within the collection
        - created_at: ISO 8601 timestamp when the collect was created
        - updated_at: ISO 8601 timestamp when the collect was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CollectsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, collect_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.Collect`
    :   Retrieves a single collect by ID
        
        Args:
            collect_id: The collect ID
            **kwargs: Additional parameters
        
        Returns:
            Collect

    `list(self, limit: int | None = None, since_id: int | None = None, collection_id: int | None = None, product_id: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Collect], CollectsListResultMeta]`
    :   Returns a list of collects (links between products and collections)
        
        Args:
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            collection_id: Filter by collection ID
            product_id: Filter by product ID
            **kwargs: Additional parameters
        
        Returns:
            CollectsListResult

<a id="CountriesQuery"></a>

`CountriesQuery(connector: ShopifyConnector)`
:   Query class for Countries entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CountriesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[CountriesSearchData]`
    :   Search countries records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CountriesSearchFilter):
        - id: Unique identifier for the country tax row
        - name: Human-readable country name
        - code: ISO 3166-1 alpha-2 country code
        - tax_name: Localized name of the tax applied in this country
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CountriesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, country_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.Country`
    :   Retrieves a single country by ID
        
        Args:
            country_id: The country ID
            **kwargs: Additional parameters
        
        Returns:
            Country

    `list(self, since_id: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Country], CountriesListResultMeta]`
    :   Returns a list of countries
        
        Args:
            since_id: Restrict results to after the specified ID
            **kwargs: Additional parameters
        
        Returns:
            CountriesListResult

<a id="CustomCollectionsQuery"></a>

`CustomCollectionsQuery(connector: ShopifyConnector)`
:   Query class for CustomCollections entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CustomCollectionsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[CustomCollectionsSearchData]`
    :   Search custom_collections records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CustomCollectionsSearchFilter):
        - id: Unique identifier for the custom collection
        - handle: URL-friendly handle for the custom collection
        - title: Display title of the custom collection
        - sort_order: How products are sorted within the collection (e.g. `best-selling`)
        - published_scope: Publishing scope (`web` or `global`)
        - published_at: ISO 8601 timestamp when the collection was published
        - updated_at: ISO 8601 timestamp when the collection was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CustomCollectionsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, input: CustomCollectionsCreateParamsInput, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.CollectionCreatePayload`
    :   Creates a new collection (custom or smart) via GraphQL mutation.
        For smart collections, provide ruleSet with rules.
        
        
                Args:
                    input: Parameter input
                    **kwargs: Additional parameters
        
                Returns:
                    CollectionCreatePayload

    `delete(self, input: CustomCollectionsDeleteParamsInput, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.CollectionDeletePayload`
    :   Deletes a collection via GraphQL mutation.
        
        
        Args:
            input: Parameter input
            **kwargs: Additional parameters
        
        Returns:
            CollectionDeletePayload

    `get(self, collection_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.CustomCollection`
    :   Retrieves a single custom collection by ID
        
        Args:
            collection_id: The collection ID
            **kwargs: Additional parameters
        
        Returns:
            CustomCollection

    `list(self, limit: int | None = None, since_id: int | None = None, title: str | None = None, product_id: int | None = None, updated_at_min: str | None = None, updated_at_max: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[CustomCollection], CustomCollectionsListResultMeta]`
    :   Returns a list of custom collections
        
        Args:
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            title: Filter by collection title
            product_id: Filter by product ID
            updated_at_min: Show collections last updated after date (ISO 8601 format)
            updated_at_max: Show collections last updated before date (ISO 8601 format)
            **kwargs: Additional parameters
        
        Returns:
            CustomCollectionsListResult

    `update(self, input: CustomCollectionsUpdateParamsInput, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.CollectionUpdatePayload`
    :   Updates an existing collection via GraphQL mutation.
        Rule-based membership recompute is async for smart collections.
        
        
                Args:
                    input: Parameter input
                    **kwargs: Additional parameters
        
                Returns:
                    CollectionUpdatePayload

<a id="CustomerAddressQuery"></a>

`CustomerAddressQuery(connector: ShopifyConnector)`
:   Query class for CustomerAddress entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, customer_id: str, address_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.CustomerAddress`
    :   Retrieves a single customer address by ID
        
        Args:
            customer_id: The customer ID
            address_id: The address ID
            **kwargs: Additional parameters
        
        Returns:
            CustomerAddress

    `list(self, customer_id: str, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[CustomerAddress], CustomerAddressListResultMeta]`
    :   Returns a list of addresses for a customer
        
        Args:
            customer_id: The customer ID
            limit: Maximum number of results to return (max 250)
            **kwargs: Additional parameters
        
        Returns:
            CustomerAddressListResult

<a id="CustomersQuery"></a>

`CustomersQuery(connector: ShopifyConnector)`
:   Query class for Customers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CustomersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[CustomersSearchData]`
    :   Search customers records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CustomersSearchFilter):
        - id: Unique identifier for the customer
        - email: Primary email address of the customer
        - phone: Primary phone number of the customer
        - first_name: First name of the customer
        - last_name: Last name of the customer
        - state: Account state (`disabled`, `invited`, `enabled`, `declined`)
        - orders_count: Number of orders placed by the customer
        - total_spent: Total lifetime amount spent by the customer
        - currency: ISO 4217 currency code for the customer's total spend
        - created_at: ISO 8601 timestamp when the customer record was created
        - updated_at: ISO 8601 timestamp when the customer record was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CustomersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, input: CustomersCreateParamsInput, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.CustomerCreatePayload`
    :   Creates a new customer in the store via GraphQL mutation.
        Requires at least one of: email, phone, firstName, or lastName.
        
        
                Args:
                    input: CustomerInput object
                    **kwargs: Additional parameters
        
                Returns:
                    CustomerCreatePayload

    `delete(self, input: CustomersDeleteParamsInput, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.CustomerDeletePayload`
    :   Deletes a customer from the store via GraphQL mutation.
        Only succeeds if the customer has no orders. This action is irreversible.
        
        
                Args:
                    input: Parameter input
                    **kwargs: Additional parameters
        
                Returns:
                    CustomerDeletePayload

    `get(self, customer_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.Customer`
    :   Retrieves a single customer by ID
        
        Args:
            customer_id: The customer ID
            **kwargs: Additional parameters
        
        Returns:
            Customer

    `list(self, limit: int | None = None, since_id: int | None = None, created_at_min: str | None = None, created_at_max: str | None = None, updated_at_min: str | None = None, updated_at_max: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Customer], CustomersListResultMeta]`
    :   Returns a list of customers from the store
        
        Args:
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            created_at_min: Show customers created after date (ISO 8601 format)
            created_at_max: Show customers created before date (ISO 8601 format)
            updated_at_min: Show customers last updated after date (ISO 8601 format)
            updated_at_max: Show customers last updated before date (ISO 8601 format)
            **kwargs: Additional parameters
        
        Returns:
            CustomersListResult

    `update(self, input: CustomersUpdateParamsInput, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.CustomerUpdatePayload`
    :   Updates an existing customer via GraphQL mutation.
        All fields except id are optional for partial updates.
        
        
                Args:
                    input: CustomerInput object with id
                    **kwargs: Additional parameters
        
                Returns:
                    CustomerUpdatePayload

<a id="DiscountCodesQuery"></a>

`DiscountCodesQuery(connector: ShopifyConnector)`
:   Query class for DiscountCodes entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: DiscountCodesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[DiscountCodesSearchData]`
    :   Search discount_codes records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (DiscountCodesSearchFilter):
        - id: Unique identifier for the discount code
        - price_rule_id: Identifier of the parent price rule
        - code: Discount code string shoppers enter at checkout
        - usage_count: Number of times the code has been redeemed
        - created_at: ISO 8601 timestamp when the code was created
        - updated_at: ISO 8601 timestamp when the code was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            DiscountCodesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, basic_code_discount: DiscountCodesCreateParamsBasiccodediscount, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.DiscountCodeBasicCreatePayload`
    :   Creates a basic discount code via GraphQL mutation.
        Supports percentage, fixed amount, or free shipping discounts.
        
        
                Args:
                    basic_code_discount: Parameter basicCodeDiscount
                    **kwargs: Additional parameters
        
                Returns:
                    DiscountCodeBasicCreatePayload

    `delete(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.DiscountCodeDeletePayload`
    :   Deletes a discount code via GraphQL mutation.
        
        
        Args:
            id: The GraphQL GID of the discount code node to delete
            **kwargs: Additional parameters
        
        Returns:
            DiscountCodeDeletePayload

    `get(self, price_rule_id: str, discount_code_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.DiscountCode`
    :   Retrieves a single discount code by ID
        
        Args:
            price_rule_id: The price rule ID
            discount_code_id: The discount code ID
            **kwargs: Additional parameters
        
        Returns:
            DiscountCode

    `list(self, price_rule_id: str, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[DiscountCode], DiscountCodesListResultMeta]`
    :   Returns a list of discount codes for a price rule
        
        Args:
            price_rule_id: The price rule ID
            limit: Maximum number of results to return (max 250)
            **kwargs: Additional parameters
        
        Returns:
            DiscountCodesListResult

    `update(self, basic_code_discount: DiscountCodesUpdateParamsBasiccodediscount, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.DiscountCodeBasicUpdatePayload`
    :   Updates an existing basic discount code via GraphQL mutation.
        
        
        Args:
            id: The GraphQL GID of the discount code node to update
            basic_code_discount: Parameter basicCodeDiscount
            **kwargs: Additional parameters
        
        Returns:
            DiscountCodeBasicUpdatePayload

<a id="DisputesQuery"></a>

`DisputesQuery(connector: ShopifyConnector)`
:   Query class for Disputes entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: DisputesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[DisputesSearchData]`
    :   Search disputes records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (DisputesSearchFilter):
        - id: Unique identifier for the dispute
        - order_id: Identifier of the order the dispute belongs to
        - type_: Whether the dispute is an inquiry or chargeback
        - amount: Disputed amount
        - currency: ISO 4217 currency code of the dispute amount
        - reason: Reason for the dispute provided by the cardholder's bank
        - network_reason_code: Network reason code from the cardholder's bank
        - status: Current state of the dispute (needs_response, under_review, charge_refunded, accepted, won, lost)
        - evidence_due_by: ISO 8601 deadline for evidence submission
        - initiated_at: ISO 8601 timestamp when the dispute was initiated
        - finalized_on: ISO 8601 timestamp when the dispute was resolved
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            DisputesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, dispute_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.Dispute`
    :   Retrieves a single Shopify Payments dispute by ID
        
        Args:
            dispute_id: The dispute ID
            **kwargs: Additional parameters
        
        Returns:
            Dispute

    `list(self, limit: int | None = None, since_id: int | None = None, status: str | None = None, initiated_at: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Dispute], DisputesListResultMeta]`
    :   Returns a list of Shopify Payments disputes (chargebacks and inquiries)
        
        Args:
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            status: Filter by dispute status
            initiated_at: Filter by initiated date (ISO 8601 format)
            **kwargs: Additional parameters
        
        Returns:
            DisputesListResult

<a id="DraftOrderCompleteQuery"></a>

`DraftOrderCompleteQuery(connector: ShopifyConnector)`
:   Query class for DraftOrderComplete entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `update(self, id: str | None = None, payment_pending: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.DraftOrderCompletePayload`
    :   Completes a draft order, converting it to a regular order via GraphQL mutation.
        
        
        Args:
            id: The GraphQL GID of the draft order to complete
            payment_pending: Whether payment is pending (true) or mark as paid (false/omit)
            **kwargs: Additional parameters
        
        Returns:
            DraftOrderCompletePayload

<a id="DraftOrdersQuery"></a>

`DraftOrdersQuery(connector: ShopifyConnector)`
:   Query class for DraftOrders entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: DraftOrdersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[DraftOrdersSearchData]`
    :   Search draft_orders records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (DraftOrdersSearchFilter):
        - id: Unique identifier for the draft order
        - name: Shopify-assigned display name for the draft order (e.g. `#D12345`)
        - email: Email address associated with the draft order
        - status: Status of the draft order (`open`, `invoice_sent`, `completed`)
        - currency: ISO 4217 currency code for the draft order totals
        - total_price: Total price of the draft order
        - order_id: Identifier of the completed order, if the draft has been completed
        - created_at: ISO 8601 timestamp when the draft order was created
        - updated_at: ISO 8601 timestamp when the draft order was last updated
        - completed_at: ISO 8601 timestamp when the draft order was completed, if applicable
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            DraftOrdersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, input: DraftOrdersCreateParamsInput, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.DraftOrderCreatePayload`
    :   Creates a new draft order via GraphQL mutation.
        Draft orders can be completed to become regular orders.
        
        
                Args:
                    input: DraftOrderInput object
                    **kwargs: Additional parameters
        
                Returns:
                    DraftOrderCreatePayload

    `delete(self, input: DraftOrdersDeleteParamsInput, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.DraftOrderDeletePayload`
    :   Deletes a draft order via GraphQL mutation.
        Only open draft orders can be deleted.
        
        
                Args:
                    input: Parameter input
                    **kwargs: Additional parameters
        
                Returns:
                    DraftOrderDeletePayload

    `get(self, draft_order_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.DraftOrder`
    :   Retrieves a single draft order by ID
        
        Args:
            draft_order_id: The draft order ID
            **kwargs: Additional parameters
        
        Returns:
            DraftOrder

    `list(self, limit: int | None = None, since_id: int | None = None, status: str | None = None, updated_at_min: str | None = None, updated_at_max: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[DraftOrder], DraftOrdersListResultMeta]`
    :   Returns a list of draft orders
        
        Args:
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            status: Filter draft orders by status
            updated_at_min: Show draft orders last updated after date (ISO 8601 format)
            updated_at_max: Show draft orders last updated before date (ISO 8601 format)
            **kwargs: Additional parameters
        
        Returns:
            DraftOrdersListResult

    `update(self, input: DraftOrdersUpdateParamsInput, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.DraftOrderUpdatePayload`
    :   Updates an existing draft order via GraphQL mutation.
        Only open draft orders can be updated.
        
        
                Args:
                    id: The GraphQL GID of the draft order to update
                    input: DraftOrderInput object with updated fields
                    **kwargs: Additional parameters
        
                Returns:
                    DraftOrderUpdatePayload

<a id="FulfillmentOrdersQuery"></a>

`FulfillmentOrdersQuery(connector: ShopifyConnector)`
:   Query class for FulfillmentOrders entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: FulfillmentOrdersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[FulfillmentOrdersSearchData]`
    :   Search fulfillment_orders records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (FulfillmentOrdersSearchFilter):
        - id: Unique identifier for the fulfillment order
        - order_id: Identifier of the parent order
        - shop_id: Identifier of the shop that owns the fulfillment order
        - assigned_location_id: Identifier of the location assigned to fulfill the order
        - status: Fulfillment order status (e.g. `open`, `in_progress`, `closed`)
        - request_status: Status of the fulfillment request (e.g. `unsubmitted`, `submitted`)
        - created_at: ISO 8601 timestamp when the fulfillment order was created
        - updated_at: ISO 8601 timestamp when the fulfillment order was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            FulfillmentOrdersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, fulfillment_order_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.FulfillmentOrder`
    :   Retrieves a single fulfillment order by ID
        
        Args:
            fulfillment_order_id: The fulfillment order ID
            **kwargs: Additional parameters
        
        Returns:
            FulfillmentOrder

    `list(self, order_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[FulfillmentOrder], FulfillmentOrdersListResultMeta]`
    :   Returns a list of fulfillment orders for a specific order
        
        Args:
            order_id: The order ID
            **kwargs: Additional parameters
        
        Returns:
            FulfillmentOrdersListResult

<a id="FulfillmentsQuery"></a>

`FulfillmentsQuery(connector: ShopifyConnector)`
:   Query class for Fulfillments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: FulfillmentsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[FulfillmentsSearchData]`
    :   Search fulfillments records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (FulfillmentsSearchFilter):
        - id: Unique identifier for the fulfillment
        - order_id: Identifier of the parent order
        - status: Fulfillment status (e.g. `pending`, `open`, `success`, `cancelled`)
        - shipment_status: Carrier shipment status (e.g. `delivered`, `in_transit`)
        - tracking_company: Name of the shipping carrier
        - tracking_number: Primary tracking number for the shipment
        - location_id: Identifier of the fulfilling location
        - created_at: ISO 8601 timestamp when the fulfillment was created
        - updated_at: ISO 8601 timestamp when the fulfillment was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            FulfillmentsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, order_id: str, fulfillment_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.Fulfillment`
    :   Retrieves a single fulfillment by ID
        
        Args:
            order_id: The order ID
            fulfillment_id: The fulfillment ID
            **kwargs: Additional parameters
        
        Returns:
            Fulfillment

    `list(self, order_id: str, limit: int | None = None, since_id: int | None = None, created_at_min: str | None = None, created_at_max: str | None = None, updated_at_min: str | None = None, updated_at_max: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Fulfillment], FulfillmentsListResultMeta]`
    :   Returns a list of fulfillments for an order
        
        Args:
            order_id: The order ID
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            created_at_min: Show fulfillments created after date (ISO 8601 format)
            created_at_max: Show fulfillments created before date (ISO 8601 format)
            updated_at_min: Show fulfillments last updated after date (ISO 8601 format)
            updated_at_max: Show fulfillments last updated before date (ISO 8601 format)
            **kwargs: Additional parameters
        
        Returns:
            FulfillmentsListResult

<a id="InventoryAdjustQuery"></a>

`InventoryAdjustQuery(connector: ShopifyConnector)`
:   Query class for InventoryAdjust entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, input: InventoryAdjustCreateParamsInput, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.InventoryAdjustQuantitiesPayload`
    :   Adjusts inventory quantities relatively (add/subtract) for items at locations via GraphQL mutation.
        
        
        Args:
            input: Parameter input
            **kwargs: Additional parameters
        
        Returns:
            InventoryAdjustQuantitiesPayload

<a id="InventoryItemsQuery"></a>

`InventoryItemsQuery(connector: ShopifyConnector)`
:   Query class for InventoryItems entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: InventoryItemsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[InventoryItemsSearchData]`
    :   Search inventory_items records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (InventoryItemsSearchFilter):
        - id: Unique identifier for the inventory item
        - sku: Stock keeping unit associated with the inventory item
        - tracked: Whether Shopify is tracking inventory for this item
        - requires_shipping: Whether the item requires shipping
        - country_code_of_origin: ISO country code of the item's country of origin
        - created_at: ISO 8601 timestamp when the inventory item was created
        - updated_at: ISO 8601 timestamp when the inventory item was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            InventoryItemsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, inventory_item_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.InventoryItem`
    :   Retrieves a single inventory item by ID
        
        Args:
            inventory_item_id: The inventory item ID
            **kwargs: Additional parameters
        
        Returns:
            InventoryItem

    `list(self, ids: str, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[InventoryItem], InventoryItemsListResultMeta]`
    :   Returns a list of inventory items
        
        Args:
            ids: Comma-separated list of inventory item IDs
            limit: Maximum number of results to return (max 250)
            **kwargs: Additional parameters
        
        Returns:
            InventoryItemsListResult

<a id="InventoryLevelsQuery"></a>

`InventoryLevelsQuery(connector: ShopifyConnector)`
:   Query class for InventoryLevels entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: InventoryLevelsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[InventoryLevelsSearchData]`
    :   Search inventory_levels records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (InventoryLevelsSearchFilter):
        - inventory_item_id: Identifier of the inventory item
        - location_id: Identifier of the location holding the inventory
        - available: Number of units available at the location
        - updated_at: ISO 8601 timestamp when the inventory level was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            InventoryLevelsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, location_id: str, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[InventoryLevel], InventoryLevelsListResultMeta]`
    :   Returns a list of inventory levels for a specific location
        
        Args:
            location_id: The location ID
            limit: Maximum number of results to return (max 250)
            **kwargs: Additional parameters
        
        Returns:
            InventoryLevelsListResult

<a id="InventorySetQuery"></a>

`InventorySetQuery(connector: ShopifyConnector)`
:   Query class for InventorySet entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, input: InventorySetCreateParamsInput, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.InventorySetQuantitiesPayload`
    :   Sets absolute inventory quantities for items at locations via GraphQL mutation.
        Uses the inventorySetQuantities mutation with a required reason and reference document.
        
        
                Args:
                    input: Parameter input
                    **kwargs: Additional parameters
        
                Returns:
                    InventorySetQuantitiesPayload

<a id="LocationsQuery"></a>

`LocationsQuery(connector: ShopifyConnector)`
:   Query class for Locations entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: LocationsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[LocationsSearchData]`
    :   Search locations records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (LocationsSearchFilter):
        - id: Unique identifier for the location
        - name: Display name of the location
        - address1: Primary street address of the location
        - city: City of the location
        - province: Province, state, or region of the location
        - country: Country name of the location
        - country_code: ISO 3166-1 alpha-2 country code of the location
        - phone: Phone number for the location
        - active: Whether the location is currently active
        - created_at: ISO 8601 timestamp when the location was created
        - updated_at: ISO 8601 timestamp when the location was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            LocationsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, location_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.Location`
    :   Retrieves a single location by ID
        
        Args:
            location_id: The location ID
            **kwargs: Additional parameters
        
        Returns:
            Location

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Location], LocationsListResultMeta]`
    :   Returns a list of locations for the store
        
        Returns:
            LocationsListResult

<a id="MetafieldArticlesQuery"></a>

`MetafieldArticlesQuery(connector: ShopifyConnector)`
:   Query class for MetafieldArticles entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: MetafieldArticlesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldArticlesSearchData]`
    :   Search metafield_articles records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (MetafieldArticlesSearchFilter):
        - id: Unique identifier for the metafield
        - namespace: Container namespace for the metafield
        - key: Identifier key for the metafield
        - value: The metafield value
        - type_: The metafield's information type
        - description: Human-readable description of the metafield
        - owner_id: Identifier of the article that owns this metafield
        - owner_resource: Resource type that owns this metafield (e.g. `article`)
        - created_at: ISO 8601 timestamp when the metafield was created
        - updated_at: ISO 8601 timestamp when the metafield was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            MetafieldArticlesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, blog_id: str, article_id: str, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldArticlesListResultMeta]`
    :   Returns a list of metafields for a specific article
        
        Args:
            blog_id: The blog ID
            article_id: The article ID
            limit: Maximum number of results to return (max 250)
            **kwargs: Additional parameters
        
        Returns:
            MetafieldArticlesListResult

<a id="MetafieldBlogsQuery"></a>

`MetafieldBlogsQuery(connector: ShopifyConnector)`
:   Query class for MetafieldBlogs entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: MetafieldBlogsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldBlogsSearchData]`
    :   Search metafield_blogs records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (MetafieldBlogsSearchFilter):
        - id: Unique identifier for the metafield
        - namespace: Container namespace for the metafield
        - key: Identifier key for the metafield
        - value: The metafield value
        - type_: The metafield's information type
        - description: Human-readable description of the metafield
        - owner_id: Identifier of the blog that owns this metafield
        - owner_resource: Resource type that owns this metafield (e.g. `blog`)
        - created_at: ISO 8601 timestamp when the metafield was created
        - updated_at: ISO 8601 timestamp when the metafield was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            MetafieldBlogsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, blog_id: str, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldBlogsListResultMeta]`
    :   Returns a list of metafields for a specific blog
        
        Args:
            blog_id: The blog ID
            limit: Maximum number of results to return (max 250)
            **kwargs: Additional parameters
        
        Returns:
            MetafieldBlogsListResult

<a id="MetafieldCustomersQuery"></a>

`MetafieldCustomersQuery(connector: ShopifyConnector)`
:   Query class for MetafieldCustomers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: MetafieldCustomersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldCustomersSearchData]`
    :   Search metafield_customers records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (MetafieldCustomersSearchFilter):
        - id: Unique identifier for the metafield
        - namespace: Namespace group for the metafield
        - key: Key of the metafield within its namespace
        - value: Serialized value stored in the metafield
        - type_: Shopify metafield type (e.g. `single_line_text_field`, `json`)
        - description: Human-readable description of the metafield
        - owner_id: Identifier of the resource that owns this metafield
        - owner_resource: Resource type that owns this metafield (e.g. `product`, `customer`)
        - created_at: ISO 8601 timestamp when the metafield was created
        - updated_at: ISO 8601 timestamp when the metafield was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            MetafieldCustomersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, customer_id: str, limit: int | None = None, since_id: int | None = None, namespace: str | None = None, key: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldCustomersListResultMeta]`
    :   Returns a list of metafields for a customer
        
        Args:
            customer_id: The customer ID
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            namespace: Filter by namespace
            key: Filter by key
            **kwargs: Additional parameters
        
        Returns:
            MetafieldCustomersListResult

<a id="MetafieldDraftOrdersQuery"></a>

`MetafieldDraftOrdersQuery(connector: ShopifyConnector)`
:   Query class for MetafieldDraftOrders entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: MetafieldDraftOrdersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldDraftOrdersSearchData]`
    :   Search metafield_draft_orders records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (MetafieldDraftOrdersSearchFilter):
        - id: Unique identifier for the metafield
        - namespace: Namespace group for the metafield
        - key: Key of the metafield within its namespace
        - value: Serialized value stored in the metafield
        - type_: Shopify metafield type (e.g. `single_line_text_field`, `json`)
        - description: Human-readable description of the metafield
        - owner_id: Identifier of the resource that owns this metafield
        - owner_resource: Resource type that owns this metafield (e.g. `product`, `customer`)
        - created_at: ISO 8601 timestamp when the metafield was created
        - updated_at: ISO 8601 timestamp when the metafield was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            MetafieldDraftOrdersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, draft_order_id: str, limit: int | None = None, since_id: int | None = None, namespace: str | None = None, key: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldDraftOrdersListResultMeta]`
    :   Returns a list of metafields for a draft order
        
        Args:
            draft_order_id: The draft order ID
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            namespace: Filter by namespace
            key: Filter by key
            **kwargs: Additional parameters
        
        Returns:
            MetafieldDraftOrdersListResult

<a id="MetafieldLocationsQuery"></a>

`MetafieldLocationsQuery(connector: ShopifyConnector)`
:   Query class for MetafieldLocations entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: MetafieldLocationsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldLocationsSearchData]`
    :   Search metafield_locations records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (MetafieldLocationsSearchFilter):
        - id: Unique identifier for the metafield
        - namespace: Namespace group for the metafield
        - key: Key of the metafield within its namespace
        - value: Serialized value stored in the metafield
        - type_: Shopify metafield type (e.g. `single_line_text_field`, `json`)
        - description: Human-readable description of the metafield
        - owner_id: Identifier of the resource that owns this metafield
        - owner_resource: Resource type that owns this metafield (e.g. `product`, `customer`)
        - created_at: ISO 8601 timestamp when the metafield was created
        - updated_at: ISO 8601 timestamp when the metafield was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            MetafieldLocationsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, location_id: str, limit: int | None = None, since_id: int | None = None, namespace: str | None = None, key: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldLocationsListResultMeta]`
    :   Returns a list of metafields for a location
        
        Args:
            location_id: The location ID
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            namespace: Filter by namespace
            key: Filter by key
            **kwargs: Additional parameters
        
        Returns:
            MetafieldLocationsListResult

<a id="MetafieldOrdersQuery"></a>

`MetafieldOrdersQuery(connector: ShopifyConnector)`
:   Query class for MetafieldOrders entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: MetafieldOrdersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldOrdersSearchData]`
    :   Search metafield_orders records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (MetafieldOrdersSearchFilter):
        - id: Unique identifier for the metafield
        - namespace: Namespace group for the metafield
        - key: Key of the metafield within its namespace
        - value: Serialized value stored in the metafield
        - type_: Shopify metafield type (e.g. `single_line_text_field`, `json`)
        - description: Human-readable description of the metafield
        - owner_id: Identifier of the resource that owns this metafield
        - owner_resource: Resource type that owns this metafield (e.g. `product`, `customer`)
        - created_at: ISO 8601 timestamp when the metafield was created
        - updated_at: ISO 8601 timestamp when the metafield was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            MetafieldOrdersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, order_id: str, limit: int | None = None, since_id: int | None = None, namespace: str | None = None, key: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldOrdersListResultMeta]`
    :   Returns a list of metafields for an order
        
        Args:
            order_id: The order ID
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            namespace: Filter by namespace
            key: Filter by key
            **kwargs: Additional parameters
        
        Returns:
            MetafieldOrdersListResult

<a id="MetafieldPagesQuery"></a>

`MetafieldPagesQuery(connector: ShopifyConnector)`
:   Query class for MetafieldPages entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: MetafieldPagesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldPagesSearchData]`
    :   Search metafield_pages records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (MetafieldPagesSearchFilter):
        - id: Unique identifier for the metafield
        - namespace: Container namespace for the metafield
        - key: Identifier key for the metafield
        - value: The metafield value
        - type_: The metafield's information type
        - description: Human-readable description of the metafield
        - owner_id: Identifier of the page that owns this metafield
        - owner_resource: Resource type that owns this metafield (e.g. `page`)
        - created_at: ISO 8601 timestamp when the metafield was created
        - updated_at: ISO 8601 timestamp when the metafield was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            MetafieldPagesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, page_id: str, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldPagesListResultMeta]`
    :   Returns a list of metafields for a specific page
        
        Args:
            page_id: The page ID
            limit: Maximum number of results to return (max 250)
            **kwargs: Additional parameters
        
        Returns:
            MetafieldPagesListResult

<a id="MetafieldProductImagesQuery"></a>

`MetafieldProductImagesQuery(connector: ShopifyConnector)`
:   Query class for MetafieldProductImages entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: MetafieldProductImagesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldProductImagesSearchData]`
    :   Search metafield_product_images records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (MetafieldProductImagesSearchFilter):
        - id: Unique identifier for the metafield
        - namespace: Namespace group for the metafield
        - key: Key of the metafield within its namespace
        - value: Serialized value stored in the metafield
        - type_: Shopify metafield type (e.g. `single_line_text_field`, `json`)
        - description: Human-readable description of the metafield
        - owner_id: Identifier of the resource that owns this metafield
        - owner_resource: Resource type that owns this metafield (e.g. `product`, `customer`)
        - created_at: ISO 8601 timestamp when the metafield was created
        - updated_at: ISO 8601 timestamp when the metafield was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            MetafieldProductImagesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, product_id: str, image_id: str, limit: int | None = None, since_id: int | None = None, namespace: str | None = None, key: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldProductImagesListResultMeta]`
    :   Returns a list of metafields for a product image
        
        Args:
            product_id: The product ID
            image_id: The image ID
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            namespace: Filter by namespace
            key: Filter by key
            **kwargs: Additional parameters
        
        Returns:
            MetafieldProductImagesListResult

<a id="MetafieldProductVariantsQuery"></a>

`MetafieldProductVariantsQuery(connector: ShopifyConnector)`
:   Query class for MetafieldProductVariants entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: MetafieldProductVariantsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldProductVariantsSearchData]`
    :   Search metafield_product_variants records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (MetafieldProductVariantsSearchFilter):
        - id: Unique identifier for the metafield
        - namespace: Namespace group for the metafield
        - key: Key of the metafield within its namespace
        - value: Serialized value stored in the metafield
        - type_: Shopify metafield type (e.g. `single_line_text_field`, `json`)
        - description: Human-readable description of the metafield
        - owner_id: Identifier of the resource that owns this metafield
        - owner_resource: Resource type that owns this metafield (e.g. `product`, `customer`)
        - created_at: ISO 8601 timestamp when the metafield was created
        - updated_at: ISO 8601 timestamp when the metafield was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            MetafieldProductVariantsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, variant_id: str, limit: int | None = None, since_id: int | None = None, namespace: str | None = None, key: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldProductVariantsListResultMeta]`
    :   Returns a list of metafields for a product variant
        
        Args:
            variant_id: The variant ID
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            namespace: Filter by namespace
            key: Filter by key
            **kwargs: Additional parameters
        
        Returns:
            MetafieldProductVariantsListResult

<a id="MetafieldProductsQuery"></a>

`MetafieldProductsQuery(connector: ShopifyConnector)`
:   Query class for MetafieldProducts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: MetafieldProductsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldProductsSearchData]`
    :   Search metafield_products records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (MetafieldProductsSearchFilter):
        - id: Unique identifier for the metafield
        - namespace: Namespace group for the metafield
        - key: Key of the metafield within its namespace
        - value: Serialized value stored in the metafield
        - type_: Shopify metafield type (e.g. `single_line_text_field`, `json`)
        - description: Human-readable description of the metafield
        - owner_id: Identifier of the resource that owns this metafield
        - owner_resource: Resource type that owns this metafield (e.g. `product`, `customer`)
        - created_at: ISO 8601 timestamp when the metafield was created
        - updated_at: ISO 8601 timestamp when the metafield was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            MetafieldProductsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, product_id: str, limit: int | None = None, since_id: int | None = None, namespace: str | None = None, key: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldProductsListResultMeta]`
    :   Returns a list of metafields for a product
        
        Args:
            product_id: The product ID
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            namespace: Filter by namespace
            key: Filter by key
            **kwargs: Additional parameters
        
        Returns:
            MetafieldProductsListResult

<a id="MetafieldShopsQuery"></a>

`MetafieldShopsQuery(connector: ShopifyConnector)`
:   Query class for MetafieldShops entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: MetafieldShopsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldShopsSearchData]`
    :   Search metafield_shops records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (MetafieldShopsSearchFilter):
        - id: Unique identifier for the metafield
        - namespace: Namespace group for the metafield
        - key: Key of the metafield within its namespace
        - value: Serialized value stored in the metafield
        - type_: Shopify metafield type (e.g. `single_line_text_field`, `json`)
        - description: Human-readable description of the metafield
        - owner_id: Identifier of the resource that owns this metafield
        - owner_resource: Resource type that owns this metafield (e.g. `product`, `customer`)
        - created_at: ISO 8601 timestamp when the metafield was created
        - updated_at: ISO 8601 timestamp when the metafield was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            MetafieldShopsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, metafield_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.Metafield`
    :   Retrieves a single metafield by ID
        
        Args:
            metafield_id: The metafield ID
            **kwargs: Additional parameters
        
        Returns:
            Metafield

    `list(self, limit: int | None = None, since_id: int | None = None, namespace: str | None = None, key: str | None = None, type: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldShopsListResultMeta]`
    :   Returns a list of metafields for the shop
        
        Args:
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            namespace: Filter by namespace
            key: Filter by key
            type: Filter by type
            **kwargs: Additional parameters
        
        Returns:
            MetafieldShopsListResult

<a id="MetafieldSmartCollectionsQuery"></a>

`MetafieldSmartCollectionsQuery(connector: ShopifyConnector)`
:   Query class for MetafieldSmartCollections entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: MetafieldSmartCollectionsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[MetafieldSmartCollectionsSearchData]`
    :   Search metafield_smart_collections records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (MetafieldSmartCollectionsSearchFilter):
        - id: Unique identifier for the metafield
        - namespace: Namespace group for the metafield
        - key: Key of the metafield within its namespace
        - value: Serialized value stored in the metafield
        - type_: Shopify metafield type (e.g. `single_line_text_field`, `json`)
        - description: Human-readable description of the metafield
        - owner_id: Identifier of the resource that owns this metafield
        - owner_resource: Resource type that owns this metafield (e.g. `product`, `customer`)
        - created_at: ISO 8601 timestamp when the metafield was created
        - updated_at: ISO 8601 timestamp when the metafield was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            MetafieldSmartCollectionsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, collection_id: str, limit: int | None = None, since_id: int | None = None, namespace: str | None = None, key: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Metafield], MetafieldSmartCollectionsListResultMeta]`
    :   Returns a list of metafields for a smart collection
        
        Args:
            collection_id: The collection ID
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            namespace: Filter by namespace
            key: Filter by key
            **kwargs: Additional parameters
        
        Returns:
            MetafieldSmartCollectionsListResult

<a id="MetafieldsQuery"></a>

`MetafieldsQuery(connector: ShopifyConnector)`
:   Query class for Metafields entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, metafields: list[MetafieldsCreateParamsMetafieldsItem], **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.MetafieldsSetPayload`
    :   Sets (creates or updates) up to 25 metafields atomically via GraphQL mutation.
        Works across all resource types (products, customers, orders, etc.).
        
        
                Args:
                    metafields: List of metafields to set
                    **kwargs: Additional parameters
        
                Returns:
                    MetafieldsSetPayload

    `delete(self, metafields: list[MetafieldsDeleteParamsMetafieldsItem], **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.MetafieldDeletePayload`
    :   Deletes one or more metafields via GraphQL mutation.
        Identifies metafields by ownerId + namespace + key.
        
        
                Args:
                    metafields: List of metafield identifiers to delete
                    **kwargs: Additional parameters
        
                Returns:
                    MetafieldDeletePayload

<a id="OrderRefundsQuery"></a>

`OrderRefundsQuery(connector: ShopifyConnector)`
:   Query class for OrderRefunds entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: OrderRefundsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[OrderRefundsSearchData]`
    :   Search order_refunds records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (OrderRefundsSearchFilter):
        - id: Unique identifier for the refund
        - order_id: Identifier of the refunded order
        - user_id: Identifier of the staff user who processed the refund
        - note: Merchant-provided note explaining the refund
        - created_at: ISO 8601 timestamp when the refund was created
        - processed_at: ISO 8601 timestamp when the refund was processed
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            OrderRefundsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, order_id: str, refund_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.Refund`
    :   Retrieves a single refund by ID
        
        Args:
            order_id: The order ID
            refund_id: The refund ID
            **kwargs: Additional parameters
        
        Returns:
            Refund

    `list(self, order_id: str, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Refund], OrderRefundsListResultMeta]`
    :   Returns a list of refunds for an order
        
        Args:
            order_id: The order ID
            limit: Maximum number of results to return (max 250)
            **kwargs: Additional parameters
        
        Returns:
            OrderRefundsListResult

<a id="OrdersQuery"></a>

`OrdersQuery(connector: ShopifyConnector)`
:   Query class for Orders entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: OrdersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[OrdersSearchData]`
    :   Search orders records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (OrdersSearchFilter):
        - id: Unique identifier for the order
        - name: Shopify-assigned display name for the order (e.g. `#1001`)
        - email: Email address associated with the order
        - phone: Phone number associated with the order
        - order_number: Sequential order number displayed in the Shopify admin
        - financial_status: Payment status of the order (e.g. `paid`, `pending`, `refunded`, `partially_refunded`)
        - fulfillment_status: Fulfillment status of the order (e.g. `fulfilled`, `partial`, `null` for unfulfilled)
        - currency: ISO 4217 currency code for the order totals
        - total_price: Total price of the order including taxes and discounts
        - subtotal_price: Subtotal of the order before shipping and taxes
        - total_tax: Total tax amount applied to the order
        - total_discounts: Total discount amount applied to the order
        - total_weight: Total weight of all items in the order, in grams
        - cancel_reason: Reason the order was cancelled, if applicable
        - cancelled_at: ISO 8601 timestamp when the order was cancelled, if applicable
        - closed_at: ISO 8601 timestamp when the order was closed, if applicable
        - tags: Comma-separated tags attached to the order
        - note: Merchant-provided note on the order
        - processed_at: ISO 8601 timestamp when the order was processed
        - created_at: ISO 8601 timestamp when the order was created
        - updated_at: ISO 8601 timestamp when the order was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            OrdersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, order: OrdersCreateParamsOrder, options: OrdersCreateParamsOptions | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.OrderCreatePayload`
    :   Creates a new order via GraphQL mutation.
        Use line items with either variantId or customAttributes.
        
        
                Args:
                    order: OrderCreateOrderInput object
                    options: OrderCreateOptionsInput
                    **kwargs: Additional parameters
        
                Returns:
                    OrderCreatePayload

    `delete(self, order_id: str, reason: str, restock: bool, notify_customer: bool | None = None, refund: bool | None = None, staff_note: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.OrderCancelPayload`
    :   Cancels an open order via GraphQL mutation.
        This action is irreversible. Optional refund and restock parameters.
        
        
                Args:
                    order_id: The GraphQL GID of the order to cancel
                    reason: Reason for cancellation
                    notify_customer: Whether to notify the customer
                    refund: Whether to refund the order
                    restock: Whether to restock items
                    staff_note: Staff note for the cancellation
                    **kwargs: Additional parameters
        
                Returns:
                    OrderCancelPayload

    `get(self, order_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.Order`
    :   Retrieves a single order by ID
        
        Args:
            order_id: The order ID
            **kwargs: Additional parameters
        
        Returns:
            Order

    `list(self, limit: int | None = None, since_id: int | None = None, created_at_min: str | None = None, created_at_max: str | None = None, updated_at_min: str | None = None, updated_at_max: str | None = None, status: str | None = None, financial_status: str | None = None, fulfillment_status: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Order], OrdersListResultMeta]`
    :   Returns a list of orders from the store
        
        Args:
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            created_at_min: Show orders created after date (ISO 8601 format)
            created_at_max: Show orders created before date (ISO 8601 format)
            updated_at_min: Show orders last updated after date (ISO 8601 format)
            updated_at_max: Show orders last updated before date (ISO 8601 format)
            status: Filter orders by status
            financial_status: Filter orders by financial status
            fulfillment_status: Filter orders by fulfillment status
            **kwargs: Additional parameters
        
        Returns:
            OrdersListResult

    `update(self, input: OrdersUpdateParamsInput, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.OrderUpdatePayload`
    :   Updates simple fields on an existing order via GraphQL mutation.
        For line item changes, use orderEditBegin/orderEditCommit instead.
        
        
                Args:
                    input: Parameter input
                    **kwargs: Additional parameters
        
                Returns:
                    OrderUpdatePayload

<a id="PagesQuery"></a>

`PagesQuery(connector: ShopifyConnector)`
:   Query class for Pages entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: PagesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[PagesSearchData]`
    :   Search pages records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (PagesSearchFilter):
        - id: Unique identifier for the page
        - title: Title of the page
        - handle: URL-friendly handle for the page
        - author: Name of the page author
        - body_html: HTML content of the page
        - published_at: ISO 8601 timestamp when the page was published
        - created_at: ISO 8601 timestamp when the page was created
        - updated_at: ISO 8601 timestamp when the page was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            PagesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, page: PagesCreateParamsPage, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.PageCreatePayload`
    :   Creates a new page on the online store via GraphQL mutation.
        
        
        Args:
            page: Parameter page
            **kwargs: Additional parameters
        
        Returns:
            PageCreatePayload

    `delete(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.PageDeletePayload`
    :   Deletes a page from the online store via GraphQL mutation.
        
        
        Args:
            id: The GraphQL GID of the page to delete
            **kwargs: Additional parameters
        
        Returns:
            PageDeletePayload

    `get(self, page_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.Page`
    :   Retrieves a single page by ID
        
        Args:
            page_id: The page ID
            **kwargs: Additional parameters
        
        Returns:
            Page

    `list(self, limit: int | None = None, since_id: int | None = None, created_at_min: str | None = None, created_at_max: str | None = None, updated_at_min: str | None = None, updated_at_max: str | None = None, published_status: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Page], PagesListResultMeta]`
    :   Returns a list of static pages for the store
        
        Args:
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            created_at_min: Show pages created after date (ISO 8601 format)
            created_at_max: Show pages created before date (ISO 8601 format)
            updated_at_min: Show pages last updated after date (ISO 8601 format)
            updated_at_max: Show pages last updated before date (ISO 8601 format)
            published_status: Filter by published status (published, unpublished, any)
            **kwargs: Additional parameters
        
        Returns:
            PagesListResult

    `update(self, page: PagesUpdateParamsPage, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.PageUpdatePayload`
    :   Updates an existing page on the online store via GraphQL mutation.
        
        
        Args:
            id: The GraphQL GID of the page to update
            page: Parameter page
            **kwargs: Additional parameters
        
        Returns:
            PageUpdatePayload

<a id="PriceRulesQuery"></a>

`PriceRulesQuery(connector: ShopifyConnector)`
:   Query class for PriceRules entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: PriceRulesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[PriceRulesSearchData]`
    :   Search price_rules records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (PriceRulesSearchFilter):
        - id: Unique identifier for the price rule
        - title: Administrative title of the price rule
        - value_type: How the discount value is interpreted (`fixed_amount` or `percentage`)
        - value: Discount value applied by the rule
        - target_type: Type of target the rule applies to (`line_item` or `shipping_line`)
        - target_selection: Which target items the rule applies to (`all` or `entitled`)
        - allocation_method: How the discount is allocated (`each` or `across`)
        - starts_at: ISO 8601 timestamp when the rule starts being active
        - ends_at: ISO 8601 timestamp when the rule stops being active, if applicable
        - created_at: ISO 8601 timestamp when the rule was created
        - updated_at: ISO 8601 timestamp when the rule was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            PriceRulesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, price_rule_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.PriceRule`
    :   Retrieves a single price rule by ID
        
        Args:
            price_rule_id: The price rule ID
            **kwargs: Additional parameters
        
        Returns:
            PriceRule

    `list(self, limit: int | None = None, since_id: int | None = None, created_at_min: str | None = None, created_at_max: str | None = None, updated_at_min: str | None = None, updated_at_max: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[PriceRule], PriceRulesListResultMeta]`
    :   Returns a list of price rules
        
        Args:
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            created_at_min: Show price rules created after date (ISO 8601 format)
            created_at_max: Show price rules created before date (ISO 8601 format)
            updated_at_min: Show price rules last updated after date (ISO 8601 format)
            updated_at_max: Show price rules last updated before date (ISO 8601 format)
            **kwargs: Additional parameters
        
        Returns:
            PriceRulesListResult

<a id="ProductImagesQuery"></a>

`ProductImagesQuery(connector: ShopifyConnector)`
:   Query class for ProductImages entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ProductImagesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[ProductImagesSearchData]`
    :   Search product_images records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ProductImagesSearchFilter):
        - id: Unique identifier for the product image
        - product_id: Identifier of the product the image belongs to
        - position: Display position of the image within the product
        - alt: Alt text for the image
        - width: Image width in pixels
        - height: Image height in pixels
        - src: Public URL of the image
        - created_at: ISO 8601 timestamp when the image was created
        - updated_at: ISO 8601 timestamp when the image was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ProductImagesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, product_id: str, image_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ProductImage`
    :   Retrieves a single product image by ID
        
        Args:
            product_id: The product ID
            image_id: The image ID
            **kwargs: Additional parameters
        
        Returns:
            ProductImage

    `list(self, product_id: str, since_id: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[ProductImage], ProductImagesListResultMeta]`
    :   Returns a list of images for a product
        
        Args:
            product_id: The product ID
            since_id: Restrict results to after the specified ID
            **kwargs: Additional parameters
        
        Returns:
            ProductImagesListResult

<a id="ProductVariantsQuery"></a>

`ProductVariantsQuery(connector: ShopifyConnector)`
:   Query class for ProductVariants entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ProductVariantsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[ProductVariantsSearchData]`
    :   Search product_variants records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ProductVariantsSearchFilter):
        - id: Unique identifier for the product variant
        - product_id: Identifier of the parent product
        - title: Display title of the variant
        - sku: Stock keeping unit for the variant
        - price: Price of the variant in the shop's currency
        - compare_at_price: Original (compare-at) price of the variant, if set
        - position: Display position of the variant within the product
        - inventory_policy: Behaviour when out of stock (`deny` or `continue`)
        - created_at: ISO 8601 timestamp when the variant was created
        - updated_at: ISO 8601 timestamp when the variant was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ProductVariantsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, product_id: str, variants: list[ProductVariantsCreateParamsVariantsItem], **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ProductVariantsBulkCreatePayload`
    :   Creates one or more product variants via GraphQL mutation.
        Variants are created in bulk for a given product.
        
        
                Args:
                    product_id: The GraphQL GID of the product (e.g. gid://shopify/Product/123)
                    variants: List of variants to create
                    **kwargs: Additional parameters
        
                Returns:
                    ProductVariantsBulkCreatePayload

    `delete(self, product_id: str, variants_ids: list[str], **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ProductVariantsBulkDeletePayload`
    :   Deletes one or more product variants via GraphQL mutation.
        Cannot delete the last variant of a product.
        
        
                Args:
                    product_id: The GraphQL GID of the product
                    variants_ids: List of variant GIDs to delete
                    **kwargs: Additional parameters
        
                Returns:
                    ProductVariantsBulkDeletePayload

    `get(self, variant_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ProductVariant`
    :   Retrieves a single product variant by ID
        
        Args:
            variant_id: The variant ID
            **kwargs: Additional parameters
        
        Returns:
            ProductVariant

    `list(self, product_id: str, limit: int | None = None, since_id: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[ProductVariant], ProductVariantsListResultMeta]`
    :   Returns a list of variants for a product
        
        Args:
            product_id: The product ID
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            **kwargs: Additional parameters
        
        Returns:
            ProductVariantsListResult

    `update(self, product_id: str, variants: list[ProductVariantsUpdateParamsVariantsItem], **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ProductVariantsBulkUpdatePayload`
    :   Updates one or more product variants via GraphQL mutation.
        Variants are updated in bulk for a given product.
        
        
                Args:
                    product_id: The GraphQL GID of the product
                    variants: List of variants to update (each must include id)
                    **kwargs: Additional parameters
        
                Returns:
                    ProductVariantsBulkUpdatePayload

<a id="ProductsQuery"></a>

`ProductsQuery(connector: ShopifyConnector)`
:   Query class for Products entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ProductsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[ProductsSearchData]`
    :   Search products records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ProductsSearchFilter):
        - id: Unique identifier for the product
        - title: Product title
        - body_html: Product description in HTML
        - vendor: Product vendor or manufacturer
        - product_type: Product type used for categorization
        - handle: URL-friendly handle for the product
        - status: Product status (`active`, `archived`, or `draft`)
        - tags: Comma-separated tags attached to the product
        - published_scope: Publishing scope (`web` or `global`)
        - published_at: ISO 8601 timestamp when the product was published
        - created_at: ISO 8601 timestamp when the product was created
        - updated_at: ISO 8601 timestamp when the product was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ProductsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, product: ProductsCreateParamsProduct, media: list[ProductsCreateParamsMediaItem] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ProductCreatePayload`
    :   Creates a new product via GraphQL mutation.
        Creates the product with a default variant. Use productVariantsBulkCreate
        to add additional variants afterwards.
        
        
                Args:
                    product: ProductCreateInput object
                    media: Media to attach to the product
                    **kwargs: Additional parameters
        
                Returns:
                    ProductCreatePayload

    `delete(self, input: ProductsDeleteParamsInput, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ProductDeletePayload`
    :   Deletes a product from the store via GraphQL mutation.
        This action is irreversible.
        
        
                Args:
                    input: Parameter input
                    **kwargs: Additional parameters
        
                Returns:
                    ProductDeletePayload

    `get(self, product_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.Product`
    :   Retrieves a single product by ID
        
        Args:
            product_id: The product ID
            **kwargs: Additional parameters
        
        Returns:
            Product

    `list(self, limit: int | None = None, since_id: int | None = None, created_at_min: str | None = None, created_at_max: str | None = None, updated_at_min: str | None = None, updated_at_max: str | None = None, status: str | None = None, product_type: str | None = None, vendor: str | None = None, collection_id: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Product], ProductsListResultMeta]`
    :   Returns a list of products from the store
        
        Args:
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            created_at_min: Show products created after date (ISO 8601 format)
            created_at_max: Show products created before date (ISO 8601 format)
            updated_at_min: Show products last updated after date (ISO 8601 format)
            updated_at_max: Show products last updated before date (ISO 8601 format)
            status: Filter products by status
            product_type: Filter by product type
            vendor: Filter by vendor
            collection_id: Filter by collection ID
            **kwargs: Additional parameters
        
        Returns:
            ProductsListResult

    `update(self, product: ProductsUpdateParamsProduct, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ProductUpdatePayload`
    :   Updates an existing product via GraphQL mutation.
        All fields except id are optional for partial updates.
        
        
                Args:
                    product: ProductUpdateInput object
                    **kwargs: Additional parameters
        
                Returns:
                    ProductUpdatePayload

<a id="ShopQuery"></a>

`ShopQuery(connector: ShopifyConnector)`
:   Query class for Shop entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ShopSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[ShopSearchData]`
    :   Search shop records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ShopSearchFilter):
        - id: Unique identifier for the shop
        - name: Display name of the shop
        - email: Primary contact email for the shop
        - domain: Custom domain configured for the shop, if any
        - myshopify_domain: Canonical `*.myshopify.com` domain for the shop
        - country_code: ISO 3166-1 alpha-2 country code of the shop
        - currency: ISO 4217 currency code used by the shop
        - timezone: Timezone configured for the shop (e.g. `(GMT-05:00) Eastern Time`)
        - plan_name: Shopify plan identifier (e.g. `shopify_plus`, `basic`)
        - created_at: ISO 8601 timestamp when the shop was created
        - updated_at: ISO 8601 timestamp when the shop was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ShopSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.Shop`
    :   Retrieves the shop's configuration
        
        Returns:
            Shop

<a id="ShopifyConnector"></a>

`ShopifyConnector(auth_config: ShopifyAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, shop: str | None = None)`
:   Type-safe Shopify API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new shopify connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., ShopifyAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)            shop: Your Shopify store name (e.g., 'my-store' from my-store.myshopify.com)
    Examples:
        # Local mode (direct API calls)
        connector = ShopifyConnector(auth_config=ShopifyAuthConfig(api_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = ShopifyConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = ShopifyConnector(
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

    `agent_tool(role: AgentToolRole | None = None, *, inspect_tool: str | None = None, docs_tool: str | None = None, max_output_chars: int | None | Unset = UNSET, framework: FrameworkName = 'none', internal_retries: int = 0, should_internal_retry: Callable[[Exception, tuple[Any, ...], dict[str, Any]], bool] | None = None, exhausted_runtime_failure_message: Callable[[Exception, tuple[Any, ...], dict[str, Any]], str | None] | None = None) ‑> Callable[[~_F], ~_F]`
    :   Framework-agnostic decorator for user-written connector tool functions.
        
        The progressive-docs sibling of tool_utils: instead of baking the full
        entity/action reference into the docstring, it instructs the agent to
        call this connector's inspect and docs tools before executing. Tool
        failures raise :class:`airbyte_agent_sdk.AirbyteToolError` by default
        (``framework="none"``, no auto-detection) — pass ``framework=...`` to
        translate to a supported framework's signal instead.
        
        Decorate three functions per connector — execute, inspect and docs.
        The role is inferred from each function's signature (extra parameters
        are allowed); a signature matching more than one role, a generic
        ``(*args, **kwargs)`` wrapper, or a callable whose signature cannot
        be read must pass the role explicitly:
        
        - ``(entity, action, ...)`` -> ``"execute"``
        - ``(section, ...)``        -> ``"read_skill_docs"``
        - ``()``                    -> ``"inspect_connector"``
        
        Usage:
            connector = ShopifyConnector(...)
        
            @ShopifyConnector.agent_tool()
            async def execute(entity: str, action: str, params: dict | None = None):
                return await connector.execute(entity=entity, action=action, params=params or \{\})
        
            @ShopifyConnector.agent_tool()
            async def inspect_connector():
                return await connector.inspect_connector()
        
            @ShopifyConnector.agent_tool()
            async def read_skill_docs(section: str | None = None):
                return await connector.read_skill_docs(section)
        
        Args:
            role: ``"execute" | "inspect_connector" | "read_skill_docs"``.
                None (default) infers the role from the decorated function's
                signature; an explicit role validates the canonical
                parameters are present (functions accepting ``**kwargs``, or
                callables whose signature cannot be read, pass validation).
            inspect_tool: Exact registered name of the sibling inspect tool,
                woven into the execute docstring for tighter steering.
                Defaults to generic phrasing.
            docs_tool: Exact registered name of the sibling docs tool (see
                inspect_tool).
            max_output_chars: Max serialized output size before failing.
                Defaults per role: execute -> DEFAULT_MAX_OUTPUT_CHARS, docs
                tools -> None.
            framework: Translation target for tool failures. Defaults to
                ``"none"`` (raise AirbyteToolError); never auto-detects.
            internal_retries: How many transient runtime failures (429/5xx,
                network, timeout) to retry silently before surfacing.
                Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.
            should_internal_retry: Optional predicate ``(error, args, kwargs)
                -> bool`` further restricting which retryable errors are safe
                for this specific tool. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.
            exhausted_runtime_failure_message: Optional callback ``(error,
                args, kwargs) -> str | None`` invoked after internal retries
                are exhausted or skipped. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000, framework: FrameworkName | None = None, internal_retries: int = 0, should_internal_retry: Callable[[Exception, tuple[Any, ...], dict[str, Any]], bool] | None = None, exhausted_runtime_failure_message: Callable[[Exception, tuple[Any, ...], dict[str, Any]], str | None] | None = None) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Add connector-specific documentation and runtime safeguards to one tool.
        
        For new agents, prefer `build_connector_tools`. It returns progressive
        `inspect_connector`, `read_skill_docs`, and `execute` tools so the agent
        can load only the connector guidance it needs:
        
        ```python
        from airbyte_agent_sdk import build_connector_tools
        from pydantic_ai import Agent
        
        tools = build_connector_tools(connector, framework="pydantic_ai")
        agent = Agent("openai:gpt-4o", tools=tools.as_list())
        ```
        
        ### Legacy: one generated-description tool
        
        Existing integrations can keep using `tool_utils` for one broad
        `execute` tool with the connector's full generated catalog in its
        description:
        
        ```python
        from fastmcp import FastMCP
        
        connector = ShopifyConnector()
        mcp = FastMCP("Connector Agent")
        
        @mcp.tool()
        @ShopifyConnector.tool_utils
        async def execute(entity: str, action: str, params: dict):
            ...
        ```
        
        Configure documentation, output limits, framework translation, and
        retries when needed:
        
        ```python
        @mcp.tool()
        @ShopifyConnector.tool_utils(update_docstring=False, max_output_chars=None)
        async def execute(entity: str, action: str, params: dict):
            ...
        
        @mcp.tool()
        @ShopifyConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
        async def execute(entity: str, action: str, params: dict):
            ...
        ```
        
        This decorator composes `translate_exceptions` for runtime wrapping,
        output-size checks, framework signal translation, and optional internal
        retries, then adds connector-specific docstring augmentation.
        
        Args:
            update_docstring: When True, append connector capabilities to `__doc__`.
            max_output_chars: Max serialized output size before raising. Use `None` to disable.
            framework: One of `"pydantic_ai" | "langchain" | "openai_agents" | "mcp"`.
                Defaults to `None`, which auto-detects each framework's canonical
                import in order. Explicit always wins.
            internal_retries: How many transient runtime failures (429/5xx, network,
                timeout) to retry silently before surfacing. Default 0. Forwarded to
                `airbyte_agent_sdk.translation.translate_exceptions`.
            should_internal_retry: Optional predicate `(error, args, kwargs) -> bool`
                further restricting which retryable errors are safe for this specific
                tool. Forwarded to `airbyte_agent_sdk.translation.translate_exceptions`.
            exhausted_runtime_failure_message: Optional callback
                `(error, args, kwargs) -> str | None`. Invoked after internal retries
                are exhausted or were skipped because `should_internal_retry` returned
                `False`. Forwarded to `airbyte_agent_sdk.translation.translate_exceptions`.

    ### Instance variables

    `connector_id: str | None`
    :   Get the connector/source ID (only available in hosted mode).
        
        Returns:
            The connector ID if in hosted mode, None if in local mode.

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            ShopifyCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'get', 'create', 'update', 'delete', 'context_store_search']", params: Mapping[str, Any] | None = None, *, select_fields: list[str] | None = None, exclude_fields: list[str] | None = None, skip_truncation: bool = True) ‑> Any`
    :   Execute an entity operation with full type safety.
        
        This is the recommended interface for blessed connectors as it:
        - Uses the same signature as non-blessed connectors
        - Provides full IDE autocomplete for entity/action/params
        - Makes migration from generic to blessed connectors seamless
        
        Args:
            entity: Entity name (e.g., "customers")
            action: Operation action (e.g., "create", "get", "list")
            params: Operation parameters (typed based on entity+action)
            select_fields: Optional allowlist of dot-notation fields to include
            exclude_fields: Optional blocklist of dot-notation fields to remove
            skip_truncation: Disable long-text truncation for collection actions
        
        Returns:
            Typed response based on the operation
        
        Example:
            customer = await connector.execute(
                entity="customers",
                action="get",
                params=\{"id": "cus_123"\}
            )

    `inspect_connector(self) ‑> dict[str, typing.Any]`
    :   Inspect this connector's hosted metadata/readiness and resolve its docs skill id.
        
        Call this before read_skill_docs in the normal hosted flow. For
        local/offline connectors this returns a local-mode payload with a
        warning instead of a hosted inspection.
        
        Example:
            info = await connector.inspect_connector()
            print(info["docs_skill_id"])

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

    `read_skill_docs(self, section: str | None = None) ‑> str`
    :   Read this connector's usage docs, rendered to text.
        
        Omit section for the outline and general guidance; pass an exact
        section id from the outline for full details. For local/offline
        connectors the full generated docs are returned and section is
        ignored.
        
        Example:
            outline = await connector.read_skill_docs()
            details = await connector.read_skill_docs(section="entity:contacts")

<a id="SmartCollectionsQuery"></a>

`SmartCollectionsQuery(connector: ShopifyConnector)`
:   Query class for SmartCollections entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SmartCollectionsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[SmartCollectionsSearchData]`
    :   Search smart_collections records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SmartCollectionsSearchFilter):
        - id: Unique identifier for the smart collection
        - handle: URL-friendly handle for the smart collection
        - title: Display title of the smart collection
        - sort_order: How products are sorted within the collection
        - published_scope: Publishing scope (`web` or `global`)
        - published_at: ISO 8601 timestamp when the collection was published
        - updated_at: ISO 8601 timestamp when the collection was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SmartCollectionsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, collection_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.SmartCollection`
    :   Retrieves a single smart collection by ID
        
        Args:
            collection_id: The collection ID
            **kwargs: Additional parameters
        
        Returns:
            SmartCollection

    `list(self, limit: int | None = None, since_id: int | None = None, title: str | None = None, product_id: int | None = None, updated_at_min: str | None = None, updated_at_max: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[SmartCollection], SmartCollectionsListResultMeta]`
    :   Returns a list of smart collections
        
        Args:
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            title: Filter by collection title
            product_id: Filter by product ID
            updated_at_min: Show collections last updated after date (ISO 8601 format)
            updated_at_max: Show collections last updated before date (ISO 8601 format)
            **kwargs: Additional parameters
        
        Returns:
            SmartCollectionsListResult

<a id="TenderTransactionsQuery"></a>

`TenderTransactionsQuery(connector: ShopifyConnector)`
:   Query class for TenderTransactions entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TenderTransactionsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.shopify.models.AirbyteSearchResult[TenderTransactionsSearchData]`
    :   Search tender_transactions records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TenderTransactionsSearchFilter):
        - id: Unique identifier for the tender transaction
        - order_id: Identifier of the order the transaction belongs to
        - user_id: Identifier of the staff user who processed the transaction
        - amount: Amount of the transaction in the shop's currency
        - currency: ISO 4217 currency code for the transaction amount
        - payment_method: Payment method used (e.g. `credit_card`, `paypal`)
        - test: Whether the transaction was a test transaction
        - processed_at: ISO 8601 timestamp when the transaction was processed
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TenderTransactionsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, limit: int | None = None, since_id: int | None = None, processed_at_min: str | None = None, processed_at_max: str | None = None, order: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[TenderTransaction], TenderTransactionsListResultMeta]`
    :   Returns a list of tender transactions
        
        Args:
            limit: Maximum number of results to return (max 250)
            since_id: Restrict results to after the specified ID
            processed_at_min: Show tender transactions processed after date (ISO 8601 format)
            processed_at_max: Show tender transactions processed before date (ISO 8601 format)
            order: Order of results
            **kwargs: Additional parameters
        
        Returns:
            TenderTransactionsListResult

<a id="TransactionsQuery"></a>

`TransactionsQuery(connector: ShopifyConnector)`
:   Query class for Transactions entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, order_id: str, transaction_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.Transaction`
    :   Retrieves a single transaction by ID
        
        Args:
            order_id: The order ID
            transaction_id: The transaction ID
            **kwargs: Additional parameters
        
        Returns:
            Transaction

    `list(self, order_id: str, since_id: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.shopify.models.ShopifyExecuteResultWithMeta[list[Transaction], TransactionsListResultMeta]`
    :   Returns a list of transactions for an order
        
        Args:
            order_id: The order ID
            since_id: Restrict results to after the specified ID
            **kwargs: Additional parameters
        
        Returns:
            TransactionsListResult