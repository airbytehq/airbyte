---
id: airbyte_agent_sdk-connectors-woocommerce-connector
title: airbyte_agent_sdk.connectors.woocommerce.connector
---

Module airbyte_agent_sdk.connectors.woocommerce.connector
=========================================================
Woocommerce connector.

Classes
-------

<a id="CouponsQuery"></a>

`CouponsQuery(connector: WoocommerceConnector)`
:   Query class for Coupons entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CouponsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[CouponsSearchData]`
    :   Search coupons records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CouponsSearchFilter):
        - amount: The amount of discount
        - code: Coupon code
        - date_created: The date the coupon was created
        - date_created_gmt: The date the coupon was created, as GMT
        - date_expires: The date the coupon expires
        - date_expires_gmt: The date the coupon expires, as GMT
        - date_modified: The date the coupon was last modified
        - date_modified_gmt: The date the coupon was last modified, as GMT
        - description: Coupon description
        - discount_type: Determines the type of discount
        - email_restrictions: List of email addresses that can use this coupon
        - exclude_sale_items: If true, not applied to sale items
        - excluded_product_categories: Excluded category IDs
        - excluded_product_ids: Excluded product IDs
        - free_shipping: Enables free shipping
        - id: Unique identifier
        - individual_use: Can only be used individually
        - limit_usage_to_x_items: Max cart items coupon applies to
        - maximum_amount: Maximum order amount
        - meta_data: Meta data
        - minimum_amount: Minimum order amount
        - product_categories: Applicable category IDs
        - product_ids: Applicable product IDs
        - usage_count: Times used
        - usage_limit: Total usage limit
        - usage_limit_per_user: Per-customer usage limit
        - used_by: Users who have used the coupon
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CouponsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.Coupon`
    :   Retrieve a coupon
        
        Args:
            id: Unique identifier for the coupon
            **kwargs: Additional parameters
        
        Returns:
            Coupon

    `list(self, page: int | None = None, per_page: int | None = None, search: str | None = None, after: str | None = None, before: str | None = None, modified_after: str | None = None, modified_before: str | None = None, code: str | None = None, orderby: str | None = None, order: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[Coupon], CouponsListResultMeta]`
    :   List coupons
        
        Args:
            page: Current page of the collection
            per_page: Maximum number of items to return per page
            search: Limit results to those matching a string
            after: Limit response to resources published after a given ISO8601 date
            before: Limit response to resources published before a given ISO8601 date
            modified_after: Limit response to resources modified after a given ISO8601 date
            modified_before: Limit response to resources modified before a given ISO8601 date
            code: Limit result set to resources with a specific code
            orderby: Sort collection by attribute
            order: Order sort attribute ascending or descending
            **kwargs: Additional parameters
        
        Returns:
            CouponsListResult

<a id="CustomersQuery"></a>

`CustomersQuery(connector: WoocommerceConnector)`
:   Query class for Customers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CustomersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[CustomersSearchData]`
    :   Search customers records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CustomersSearchFilter):
        - avatar_url: Avatar URL
        - billing: List of billing address data
        - date_created: The date the customer was created, in the site's timezone
        - date_created_gmt: The date the customer was created, as GMT
        - date_modified: The date the customer was last modified, in the site's timezone
        - date_modified_gmt: The date the customer was last modified, as GMT
        - email: The email address for the customer
        - first_name: Customer first name
        - id: Unique identifier for the resource
        - is_paying_customer: Is the customer a paying customer
        - last_name: Customer last name
        - meta_data: Meta data
        - role: Customer role
        - shipping: List of shipping address data
        - username: Customer login name
        
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

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.Customer`
    :   Retrieve a customer
        
        Args:
            id: Unique identifier for the customer
            **kwargs: Additional parameters
        
        Returns:
            Customer

    `list(self, page: int | None = None, per_page: int | None = None, search: str | None = None, orderby: str | None = None, order: str | None = None, email: str | None = None, role: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[Customer], CustomersListResultMeta]`
    :   List customers
        
        Args:
            page: Current page of the collection
            per_page: Maximum number of items to return per page
            search: Limit results to those matching a string
            orderby: Sort collection by attribute
            order: Order sort attribute ascending or descending
            email: Limit result set to resources with a specific email
            role: Limit result set to resources with a specific role
            **kwargs: Additional parameters
        
        Returns:
            CustomersListResult

<a id="OrderNotesQuery"></a>

`OrderNotesQuery(connector: WoocommerceConnector)`
:   Query class for OrderNotes entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: OrderNotesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[OrderNotesSearchData]`
    :   Search order_notes records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (OrderNotesSearchFilter):
        - author: Order note author
        - date_created: The date the order note was created
        - date_created_gmt: The date the order note was created, as GMT
        - id: Unique identifier
        - note: Order note content
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            OrderNotesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, order_id: str, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.OrderNote`
    :   Retrieve an order note
        
        Args:
            order_id: Unique identifier for the order
            id: Unique identifier for the note
            **kwargs: Additional parameters
        
        Returns:
            OrderNote

    `list(self, order_id: str, type: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[OrderNote], OrderNotesListResultMeta]`
    :   List order notes
        
        Args:
            order_id: Unique identifier for the order
            type: Limit result set to a specific note type
            **kwargs: Additional parameters
        
        Returns:
            OrderNotesListResult

<a id="OrdersQuery"></a>

`OrdersQuery(connector: WoocommerceConnector)`
:   Query class for Orders entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: OrdersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[OrdersSearchData]`
    :   Search orders records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (OrdersSearchFilter):
        - billing: Billing address
        - cart_hash: MD5 hash of cart items to ensure orders are not modified
        - cart_tax: Sum of line item taxes only
        - coupon_lines: Coupons line data
        - created_via: Shows where the order was created
        - currency: Currency the order was created with, in ISO format
        - customer_id: User ID who owns the order (0 for guests)
        - customer_ip_address: Customer's IP address
        - customer_note: Note left by the customer during checkout
        - customer_user_agent: User agent of the customer
        - date_completed: The date the order was completed, in the site's timezone
        - date_completed_gmt: The date the order was completed, as GMT
        - date_created: The date the order was created, in the site's timezone
        - date_created_gmt: The date the order was created, as GMT
        - date_modified: The date the order was last modified, in the site's timezone
        - date_modified_gmt: The date the order was last modified, as GMT
        - date_paid: The date the order was paid, in the site's timezone
        - date_paid_gmt: The date the order was paid, as GMT
        - discount_tax: Total discount tax amount for the order
        - discount_total: Total discount amount for the order
        - fee_lines: Fee lines data
        - id: Unique identifier for the resource
        - line_items: Line items data
        - meta_data: Meta data
        - number: Order number
        - order_key: Order key
        - parent_id: Parent order ID
        - payment_method: Payment method ID
        - payment_method_title: Payment method title
        - prices_include_tax: True if the prices included tax during checkout
        - refunds: List of refunds
        - shipping: Shipping address
        - shipping_lines: Shipping lines data
        - shipping_tax: Total shipping tax amount for the order
        - shipping_total: Total shipping amount for the order
        - status: Order status
        - tax_lines: Tax lines data
        - total: Grand total
        - total_tax: Sum of all taxes
        - transaction_id: Unique transaction ID
        - version: Version of WooCommerce which last updated the order
        
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

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.Order`
    :   Retrieve an order
        
        Args:
            id: Unique identifier for the order
            **kwargs: Additional parameters
        
        Returns:
            Order

    `list(self, page: int | None = None, per_page: int | None = None, search: str | None = None, after: str | None = None, before: str | None = None, modified_after: str | None = None, modified_before: str | None = None, status: str | None = None, customer: int | None = None, product: int | None = None, orderby: str | None = None, order: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[Order], OrdersListResultMeta]`
    :   List orders
        
        Args:
            page: Current page of the collection
            per_page: Maximum number of items to return per page
            search: Limit results to those matching a string
            after: Limit response to resources published after a given ISO8601 date
            before: Limit response to resources published before a given ISO8601 date
            modified_after: Limit response to resources modified after a given ISO8601 date
            modified_before: Limit response to resources modified before a given ISO8601 date
            status: Limit result set to orders with a specific status
            customer: Limit result set to orders assigned to a specific customer ID
            product: Limit result set to orders that include a specific product ID
            orderby: Sort collection by attribute
            order: Order sort attribute ascending or descending
            **kwargs: Additional parameters
        
        Returns:
            OrdersListResult

<a id="PaymentGatewaysQuery"></a>

`PaymentGatewaysQuery(connector: WoocommerceConnector)`
:   Query class for PaymentGateways entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: PaymentGatewaysSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[PaymentGatewaysSearchData]`
    :   Search payment_gateways records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (PaymentGatewaysSearchFilter):
        - description: Payment gateway description on checkout
        - enabled: Payment gateway enabled status
        - id: Payment gateway ID
        - method_description: Payment gateway method description
        - method_supports: Supported features
        - method_title: Payment gateway method title
        - order: Payment gateway sort order
        - settings: Payment gateway settings
        - title: Payment gateway title on checkout
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            PaymentGatewaysSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.PaymentGateway`
    :   Retrieve a payment gateway
        
        Args:
            id: Unique identifier for the payment gateway
            **kwargs: Additional parameters
        
        Returns:
            PaymentGateway

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[PaymentGateway], PaymentGatewaysListResultMeta]`
    :   List payment gateways
        
        Returns:
            PaymentGatewaysListResult

<a id="ProductAttributesQuery"></a>

`ProductAttributesQuery(connector: WoocommerceConnector)`
:   Query class for ProductAttributes entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ProductAttributesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[ProductAttributesSearchData]`
    :   Search product_attributes records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ProductAttributesSearchFilter):
        - has_archives: Enable/Disable attribute archives
        - id: Unique identifier
        - name: Attribute name
        - order_by: Default sort order
        - slug: Alphanumeric identifier
        - type_: Type of attribute
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ProductAttributesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.ProductAttribute`
    :   Retrieve a product attribute
        
        Args:
            id: Unique identifier for the attribute
            **kwargs: Additional parameters
        
        Returns:
            ProductAttribute

    `list(self, page: int | None = None, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[ProductAttribute], ProductAttributesListResultMeta]`
    :   List product attributes
        
        Args:
            page: Current page of the collection
            per_page: Maximum number of items to return per page
            **kwargs: Additional parameters
        
        Returns:
            ProductAttributesListResult

<a id="ProductCategoriesQuery"></a>

`ProductCategoriesQuery(connector: WoocommerceConnector)`
:   Query class for ProductCategories entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ProductCategoriesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[ProductCategoriesSearchData]`
    :   Search product_categories records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ProductCategoriesSearchFilter):
        - count: Number of published products for the resource
        - description: HTML description of the resource
        - display: Category archive display type
        - id: Unique identifier for the resource
        - image: Image data
        - menu_order: Menu order
        - name: Category name
        - parent: The ID for the parent of the resource
        - slug: An alphanumeric identifier
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ProductCategoriesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.ProductCategory`
    :   Retrieve a product category
        
        Args:
            id: Unique identifier for the category
            **kwargs: Additional parameters
        
        Returns:
            ProductCategory

    `list(self, page: int | None = None, per_page: int | None = None, search: str | None = None, orderby: str | None = None, order: str | None = None, hide_empty: bool | None = None, parent: int | None = None, product: int | None = None, slug: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[ProductCategory], ProductCategoriesListResultMeta]`
    :   List product categories
        
        Args:
            page: Current page of the collection
            per_page: Maximum number of items to return per page
            search: Limit results to those matching a string
            orderby: Sort collection by attribute
            order: Order sort attribute ascending or descending
            hide_empty: Whether to hide categories not assigned to any products
            parent: Limit result set to categories assigned a specific parent
            product: Limit result set to categories assigned to a specific product
            slug: Limit result set to categories with a specific slug
            **kwargs: Additional parameters
        
        Returns:
            ProductCategoriesListResult

<a id="ProductReviewsQuery"></a>

`ProductReviewsQuery(connector: WoocommerceConnector)`
:   Query class for ProductReviews entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ProductReviewsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[ProductReviewsSearchData]`
    :   Search product_reviews records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ProductReviewsSearchFilter):
        - date_created: The date the review was created
        - date_created_gmt: The date the review was created, as GMT
        - id: Unique identifier
        - product_id: Product the review belongs to
        - rating: Review rating (0 to 5)
        - review: The content of the review
        - reviewer: Reviewer name
        - reviewer_email: Reviewer email
        - status: Status of the review
        - verified: Shows if the reviewer bought the product
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ProductReviewsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.ProductReview`
    :   Retrieve a product review
        
        Args:
            id: Unique identifier for the review
            **kwargs: Additional parameters
        
        Returns:
            ProductReview

    `list(self, page: int | None = None, per_page: int | None = None, search: str | None = None, after: str | None = None, before: str | None = None, product: list[int] | None = None, status: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[ProductReview], ProductReviewsListResultMeta]`
    :   List product reviews
        
        Args:
            page: Current page of the collection
            per_page: Maximum number of items to return per page
            search: Limit results to those matching a string
            after: Limit response to reviews published after a given ISO8601 date
            before: Limit response to reviews published before a given ISO8601 date
            product: Limit result set to reviews assigned to specific product IDs
            status: Limit result set to reviews assigned a specific status
            **kwargs: Additional parameters
        
        Returns:
            ProductReviewsListResult

<a id="ProductTagsQuery"></a>

`ProductTagsQuery(connector: WoocommerceConnector)`
:   Query class for ProductTags entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ProductTagsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[ProductTagsSearchData]`
    :   Search product_tags records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ProductTagsSearchFilter):
        - count: Number of published products
        - description: HTML description
        - id: Unique identifier
        - name: Tag name
        - slug: Alphanumeric identifier
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ProductTagsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.ProductTag`
    :   Retrieve a product tag
        
        Args:
            id: Unique identifier for the tag
            **kwargs: Additional parameters
        
        Returns:
            ProductTag

    `list(self, page: int | None = None, per_page: int | None = None, search: str | None = None, orderby: str | None = None, order: str | None = None, hide_empty: bool | None = None, product: int | None = None, slug: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[ProductTag], ProductTagsListResultMeta]`
    :   List product tags
        
        Args:
            page: Current page of the collection
            per_page: Maximum number of items to return per page
            search: Limit results to those matching a string
            orderby: Sort collection by attribute
            order: Order sort attribute ascending or descending
            hide_empty: Whether to hide tags not assigned to any products
            product: Limit result set to tags assigned to a specific product
            slug: Limit result set to tags with a specific slug
            **kwargs: Additional parameters
        
        Returns:
            ProductTagsListResult

<a id="ProductVariationsQuery"></a>

`ProductVariationsQuery(connector: WoocommerceConnector)`
:   Query class for ProductVariations entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ProductVariationsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[ProductVariationsSearchData]`
    :   Search product_variations records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ProductVariationsSearchFilter):
        - attributes: List of attributes
        - backordered: On backordered
        - backorders: Backorders allowed setting
        - backorders_allowed: Shows if backorders are allowed
        - date_created: The date the variation was created
        - date_created_gmt: The date the variation was created, as GMT
        - date_modified: The date the variation was last modified
        - date_modified_gmt: The date the variation was last modified, as GMT
        - date_on_sale_from: Start date of sale price
        - date_on_sale_from_gmt: Start date of sale price, as GMT
        - date_on_sale_to: End date of sale price
        - date_on_sale_to_gmt: End date of sale price, as GMT
        - description: Variation description
        - dimensions: Variation dimensions
        - download_expiry: Days until access expires
        - download_limit: Download limit
        - downloadable: If downloadable
        - downloads: Downloadable files
        - id: Unique identifier
        - image: Variation image data
        - manage_stock: Stock management at variation level
        - menu_order: Menu order
        - meta_data: Meta data
        - on_sale: Shows if on sale
        - permalink: Variation URL
        - price: Current variation price
        - purchasable: Can be bought
        - regular_price: Variation regular price
        - sale_price: Variation sale price
        - shipping_class: Shipping class slug
        - shipping_class_id: Shipping class ID
        - sku: Unique identifier (SKU)
        - status: Variation status
        - stock_quantity: Stock quantity
        - stock_status: Controls the stock status
        - tax_class: Tax class
        - tax_status: Tax status
        - virtual: If virtual
        - weight: Variation weight
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ProductVariationsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, product_id: str, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.ProductVariation`
    :   Retrieve a product variation
        
        Args:
            product_id: Unique identifier for the parent product
            id: Unique identifier for the variation
            **kwargs: Additional parameters
        
        Returns:
            ProductVariation

    `list(self, product_id: str, page: int | None = None, per_page: int | None = None, search: str | None = None, sku: str | None = None, status: str | None = None, stock_status: str | None = None, on_sale: bool | None = None, min_price: str | None = None, max_price: str | None = None, orderby: str | None = None, order: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[ProductVariation], ProductVariationsListResultMeta]`
    :   List product variations
        
        Args:
            product_id: Unique identifier for the parent product
            page: Current page of the collection
            per_page: Maximum number of items to return per page
            search: Limit results to those matching a string
            sku: Limit result set to variations with a specific SKU
            status: Limit result set to variations with a specific status
            stock_status: Limit result set to variations with specified stock status
            on_sale: Limit result set to variations on sale
            min_price: Limit result set to variations based on a minimum price
            max_price: Limit result set to variations based on a maximum price
            orderby: Sort collection by attribute
            order: Order sort attribute ascending or descending
            **kwargs: Additional parameters
        
        Returns:
            ProductVariationsListResult

<a id="ProductsQuery"></a>

`ProductsQuery(connector: WoocommerceConnector)`
:   Query class for Products entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ProductsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[ProductsSearchData]`
    :   Search products records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ProductsSearchFilter):
        - attributes: List of attributes
        - average_rating: Reviews average rating
        - backordered: Shows if the product is on backordered
        - backorders: If managing stock, this controls if backorders are allowed
        - backorders_allowed: Shows if backorders are allowed
        - button_text: Product external button text
        - catalog_visibility: Catalog visibility
        - categories: List of categories
        - cross_sell_ids: List of cross-sell products IDs
        - date_created: The date the product was created
        - date_created_gmt: The date the product was created, as GMT
        - date_modified: The date the product was last modified
        - date_modified_gmt: The date the product was last modified, as GMT
        - date_on_sale_from: Start date of sale price
        - date_on_sale_from_gmt: Start date of sale price, as GMT
        - date_on_sale_to: End date of sale price
        - date_on_sale_to_gmt: End date of sale price, as GMT
        - default_attributes: Defaults variation attributes
        - description: Product description
        - dimensions: Product dimensions
        - download_expiry: Number of days until access to downloadable files expires
        - download_limit: Number of times downloadable files can be downloaded
        - downloadable: If the product is downloadable
        - downloads: List of downloadable files
        - external_url: Product external URL
        - grouped_products: List of grouped products ID
        - id: Unique identifier for the resource
        - images: List of images
        - manage_stock: Stock management at product level
        - menu_order: Menu order
        - meta_data: Meta data
        - name: Product name
        - on_sale: Shows if the product is on sale
        - parent_id: Product parent ID
        - permalink: Product URL
        - price: Current product price
        - price_html: Price formatted in HTML
        - purchasable: Shows if the product can be bought
        - purchase_note: Note to send customer after purchase
        - rating_count: Amount of reviews
        - regular_price: Product regular price
        - related_ids: List of related products IDs
        - reviews_allowed: Allow reviews
        - sale_price: Product sale price
        - shipping_class: Shipping class slug
        - shipping_class_id: Shipping class ID
        - shipping_required: Shows if the product needs to be shipped
        - shipping_taxable: Shows if product shipping is taxable
        - short_description: Product short description
        - sku: Unique identifier (SKU)
        - slug: Product slug
        - sold_individually: Allow one item per order
        - status: Product status
        - stock_quantity: Stock quantity
        - stock_status: Controls the stock status
        - tags: List of tags
        - tax_class: Tax class
        - tax_status: Tax status
        - total_sales: Amount of sales
        - type_: Product type
        - upsell_ids: List of up-sell products IDs
        - variations: List of variations IDs
        - virtual: If the product is virtual
        - weight: Product weight
        
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

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.Product`
    :   Retrieve a product
        
        Args:
            id: Unique identifier for the product
            **kwargs: Additional parameters
        
        Returns:
            Product

    `list(self, page: int | None = None, per_page: int | None = None, search: str | None = None, after: str | None = None, before: str | None = None, modified_after: str | None = None, modified_before: str | None = None, status: str | None = None, type: str | None = None, sku: str | None = None, featured: bool | None = None, category: str | None = None, tag: str | None = None, on_sale: bool | None = None, min_price: str | None = None, max_price: str | None = None, stock_status: str | None = None, orderby: str | None = None, order: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[Product], ProductsListResultMeta]`
    :   List products
        
        Args:
            page: Current page of the collection
            per_page: Maximum number of items to return per page
            search: Limit results to those matching a string
            after: Limit response to resources published after a given ISO8601 date
            before: Limit response to resources published before a given ISO8601 date
            modified_after: Limit response to resources modified after a given ISO8601 date
            modified_before: Limit response to resources modified before a given ISO8601 date
            status: Limit result set to products with a specific status
            type: Limit result set to products with a specific type
            sku: Limit result set to products with a specific SKU
            featured: Limit result set to featured products
            category: Limit result set to products assigned a specific category ID
            tag: Limit result set to products assigned a specific tag ID
            on_sale: Limit result set to products on sale
            min_price: Limit result set to products based on a minimum price
            max_price: Limit result set to products based on a maximum price
            stock_status: Limit result set to products with specified stock status
            orderby: Sort collection by attribute
            order: Order sort attribute ascending or descending
            **kwargs: Additional parameters
        
        Returns:
            ProductsListResult

<a id="RefundsQuery"></a>

`RefundsQuery(connector: WoocommerceConnector)`
:   Query class for Refunds entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: RefundsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[RefundsSearchData]`
    :   Search refunds records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (RefundsSearchFilter):
        - amount: Refund amount
        - date_created: The date the refund was created
        - date_created_gmt: The date the refund was created, as GMT
        - id: Unique identifier
        - line_items: Line items data
        - meta_data: Meta data
        - reason: Reason for refund
        - refunded_by: User ID of user who created the refund
        - refunded_payment: If the payment was refunded via the API
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            RefundsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, order_id: str, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.Refund`
    :   Retrieve a refund
        
        Args:
            order_id: Unique identifier for the order
            id: Unique identifier for the refund
            **kwargs: Additional parameters
        
        Returns:
            Refund

    `list(self, order_id: str, page: int | None = None, per_page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[Refund], RefundsListResultMeta]`
    :   List order refunds
        
        Args:
            order_id: Unique identifier for the order
            page: Current page of the collection
            per_page: Maximum number of items to return per page
            **kwargs: Additional parameters
        
        Returns:
            RefundsListResult

<a id="ShippingMethodsQuery"></a>

`ShippingMethodsQuery(connector: WoocommerceConnector)`
:   Query class for ShippingMethods entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ShippingMethodsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[ShippingMethodsSearchData]`
    :   Search shipping_methods records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ShippingMethodsSearchFilter):
        - description: Shipping method description
        - id: Method ID
        - title: Shipping method title
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ShippingMethodsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.ShippingMethod`
    :   Retrieve a shipping method
        
        Args:
            id: Unique identifier for the shipping method
            **kwargs: Additional parameters
        
        Returns:
            ShippingMethod

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[ShippingMethod], ShippingMethodsListResultMeta]`
    :   List shipping methods
        
        Returns:
            ShippingMethodsListResult

<a id="ShippingZonesQuery"></a>

`ShippingZonesQuery(connector: WoocommerceConnector)`
:   Query class for ShippingZones entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ShippingZonesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[ShippingZonesSearchData]`
    :   Search shipping_zones records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ShippingZonesSearchFilter):
        - id: Unique identifier
        - name: Shipping zone name
        - order: Shipping zone order
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ShippingZonesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.ShippingZone`
    :   Retrieve a shipping zone
        
        Args:
            id: Unique identifier for the shipping zone
            **kwargs: Additional parameters
        
        Returns:
            ShippingZone

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[ShippingZone], ShippingZonesListResultMeta]`
    :   List shipping zones
        
        Returns:
            ShippingZonesListResult

<a id="TaxClassesQuery"></a>

`TaxClassesQuery(connector: WoocommerceConnector)`
:   Query class for TaxClasses entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TaxClassesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[TaxClassesSearchData]`
    :   Search tax_classes records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TaxClassesSearchFilter):
        - name: Tax class name
        - slug: Unique identifier
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TaxClassesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[TaxClass], TaxClassesListResultMeta]`
    :   List tax classes
        
        Returns:
            TaxClassesListResult

<a id="TaxRatesQuery"></a>

`TaxRatesQuery(connector: WoocommerceConnector)`
:   Query class for TaxRates entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TaxRatesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.woocommerce.models.AirbyteSearchResult[TaxRatesSearchData]`
    :   Search tax_rates records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TaxRatesSearchFilter):
        - cities: City names
        - city: City name
        - class_: Tax class
        - compound: Whether this is a compound rate
        - country: Country ISO 3166 code
        - id: Unique identifier
        - name: Tax rate name
        - order: Order in queries
        - postcode: Postcode/ZIP
        - postcodes: Postcodes/ZIPs
        - priority: Tax priority
        - rate: Tax rate
        - shipping: Applied to shipping
        - state: State code
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TaxRatesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.TaxRate`
    :   Retrieve a tax rate
        
        Args:
            id: Unique identifier for the tax rate
            **kwargs: Additional parameters
        
        Returns:
            TaxRate

    `list(self, page: int | None = None, per_page: int | None = None, class_: str | None = None, orderby: str | None = None, order: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceExecuteResultWithMeta[list[TaxRate], TaxRatesListResultMeta]`
    :   List tax rates
        
        Args:
            page: Current page of the collection
            per_page: Maximum number of items to return per page
            class_: Sort by tax class
            orderby: Sort collection by attribute
            order: Order sort attribute ascending or descending
            **kwargs: Additional parameters
        
        Returns:
            TaxRatesListResult

<a id="WoocommerceConnector"></a>

`WoocommerceConnector(auth_config: WoocommerceAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, shop: str | None = None)`
:   Type-safe Woocommerce API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new woocommerce connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., WoocommerceAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)            shop: The WooCommerce store domain (e.g., mystore.com)
    Examples:
        # Local mode (direct API calls)
        connector = WoocommerceConnector(auth_config=WoocommerceAuthConfig(api_key="...", api_secret="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = WoocommerceConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = WoocommerceConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'WoocommerceAuthConfig'", name: str | None = None, replication_config: "'WoocommerceReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A WoocommerceConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await WoocommerceConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=WoocommerceAuthConfig(api_key="...", api_secret="..."),
            )
        
            # With replication config (required for this connector):
            connector = await WoocommerceConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=WoocommerceAuthConfig(api_key="...", api_secret="..."),
                replication_config=WoocommerceReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @WoocommerceConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @WoocommerceConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await WoocommerceConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.woocommerce.models.WoocommerceCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            WoocommerceCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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