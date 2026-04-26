---
id: airbyte_agent_sdk-connectors-amazon_seller_partner-models
title: airbyte_agent_sdk.connectors.amazon_seller_partner.models
---

Module airbyte_agent_sdk.connectors.amazon_seller_partner.models
================================================================
Pydantic models for amazon-seller-partner connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

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

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchResult[ListFinancialEventGroupsSearchData]
    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchResult[ListFinancialEventsSearchData]
    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchResult[OrderItemsSearchData]
    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchResult[OrdersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[ListFinancialEventGroupsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ListFinancialEventGroupsSearchResult"></a>

`ListFinancialEventGroupsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ListFinancialEventsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ListFinancialEventsSearchResult"></a>

`ListFinancialEventsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[OrderItemsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="OrderItemsSearchResult"></a>

`OrderItemsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[OrdersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="OrdersSearchResult"></a>

`OrdersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AmazonSellerPartnerAuthConfig"></a>

`AmazonSellerPartnerAuthConfig(**data: Any)`
:   Login with Amazon OAuth 2.0
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str | None`
    :   Access token (optional if refresh_token is provided).

    `lwa_app_id: str`
    :   Your Login with Amazon Client ID.

    `lwa_client_secret: str`
    :   Your Login with Amazon Client Secret.

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str`
    :   The Refresh Token obtained via the OAuth authorization flow.

<a id="AmazonSellerPartnerCheckResult"></a>

`AmazonSellerPartnerCheckResult(**data: Any)`
:   Result of a health check operation.
    
    Returned by the check() method to indicate connectivity and credential status.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `checked_action: str | None`
    :   Action name used for the health check.

    `checked_entity: str | None`
    :   Entity name used for the health check.

    `error: str | None`
    :   Error message if status is 'unhealthy', None otherwise.

    `model_config`
    :   The type of the None singleton.

    `status: str`
    :   Health check status: 'healthy' or 'unhealthy'.

<a id="AmazonSellerPartnerExecuteResult"></a>

`AmazonSellerPartnerExecuteResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="AmazonSellerPartnerExecuteResultWithMeta"></a>

`AmazonSellerPartnerExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta[FinancialEvents, ListFinancialEventsListResultMeta]
    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta[list[CatalogItem], CatalogItemsListResultMeta]
    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta[list[FinancialEventGroup], ListFinancialEventGroupsListResultMeta]
    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta[list[OrderItem], OrderItemsListResultMeta]
    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta[list[Order], OrdersListResultMeta]
    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta[list[Report], ReportsListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`AmazonSellerPartnerExecuteResultWithMeta[FinancialEvents, ListFinancialEventsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ListFinancialEventsListResult"></a>

`ListFinancialEventsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AmazonSellerPartnerExecuteResultWithMeta[list[CatalogItem], CatalogItemsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CatalogItemsListResult"></a>

`CatalogItemsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AmazonSellerPartnerExecuteResultWithMeta[list[FinancialEventGroup], ListFinancialEventGroupsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ListFinancialEventGroupsListResult"></a>

`ListFinancialEventGroupsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AmazonSellerPartnerExecuteResultWithMeta[list[OrderItem], OrderItemsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="OrderItemsListResult"></a>

`OrderItemsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AmazonSellerPartnerExecuteResultWithMeta[list[Order], OrdersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="OrdersListResult"></a>

`OrdersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AmazonSellerPartnerExecuteResultWithMeta[list[Report], ReportsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ReportsListResult"></a>

`ReportsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.amazon_seller_partner.models.AmazonSellerPartnerExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AmazonSellerPartnerReplicationConfig"></a>

`AmazonSellerPartnerReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Amazon Seller Partner.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `replication_start_date: str`
    :   UTC date and time in ISO 8601 format (e.g. 2024-01-01T00:00:00Z). Any data before this date will not be replicated. This sets the earliest date for order creation and financial event queries. For most sellers, a start date of 1-2 years ago is a good default. Must include the time component and Z timezone suffix.

<a id="CatalogItem"></a>

`CatalogItem(**data: Any)`
:   Amazon catalog item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `asin: str | Any`
    :   The type of the None singleton.

    `attributes: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `classifications: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `dimensions: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `identifiers: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `images: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `product_types: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `relationships: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `sales_ranks: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `summaries: list[airbyte_agent_sdk.connectors.amazon_seller_partner.models.CatalogItemSummariesItem] | Any`
    :   The type of the None singleton.

    `vendor_details: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

<a id="CatalogItemSummariesItem"></a>

`CatalogItemSummariesItem(**data: Any)`
:   Nested schema for CatalogItem.summaries_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `adult_product: bool | Any`
    :   The type of the None singleton.

    `autographed: bool | Any`
    :   The type of the None singleton.

    `brand: str | Any`
    :   The type of the None singleton.

    `browse_classification: airbyte_agent_sdk.connectors.amazon_seller_partner.models.CatalogItemSummariesItemBrowseclassification | Any`
    :   The type of the None singleton.

    `color: str | Any`
    :   The type of the None singleton.

    `item_classification: str | Any`
    :   The type of the None singleton.

    `item_name: str | Any`
    :   The type of the None singleton.

    `manufacturer: str | Any`
    :   The type of the None singleton.

    `marketplace_id: str | Any`
    :   The type of the None singleton.

    `memorabilia: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `model_number: str | Any`
    :   The type of the None singleton.

    `package_quantity: int | Any`
    :   The type of the None singleton.

    `part_number: str | Any`
    :   The type of the None singleton.

    `size: str | Any`
    :   The type of the None singleton.

    `style: str | Any`
    :   The type of the None singleton.

    `trade_in_eligible: bool | Any`
    :   The type of the None singleton.

    `website_display_group: str | Any`
    :   The type of the None singleton.

    `website_display_group_name: str | Any`
    :   The type of the None singleton.

<a id="CatalogItemSummariesItemBrowseclassification"></a>

`CatalogItemSummariesItemBrowseclassification(**data: Any)`
:   Nested schema for CatalogItemSummariesItem.browseClassification
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `classification_id: str | Any`
    :   The type of the None singleton.

    `display_name: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CatalogItemsList"></a>

`CatalogItemsList(**data: Any)`
:   Catalog items search results
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `items: list[airbyte_agent_sdk.connectors.amazon_seller_partner.models.CatalogItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `number_of_results: int | Any`
    :   The type of the None singleton.

    `pagination: airbyte_agent_sdk.connectors.amazon_seller_partner.models.CatalogItemsListPagination | Any`
    :   The type of the None singleton.

    `refinements: airbyte_agent_sdk.connectors.amazon_seller_partner.models.CatalogItemsListRefinements | Any`
    :   The type of the None singleton.

<a id="CatalogItemsListPagination"></a>

`CatalogItemsListPagination(**data: Any)`
:   Nested schema for CatalogItemsList.pagination
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_token: str | Any`
    :   The type of the None singleton.

    `previous_token: str | Any`
    :   The type of the None singleton.

<a id="CatalogItemsListRefinements"></a>

`CatalogItemsListRefinements(**data: Any)`
:   Nested schema for CatalogItemsList.refinements
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `brands: list[airbyte_agent_sdk.connectors.amazon_seller_partner.models.CatalogItemsListRefinementsBrandsItem] | Any`
    :   The type of the None singleton.

    `classifications: list[airbyte_agent_sdk.connectors.amazon_seller_partner.models.CatalogItemsListRefinementsClassificationsItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CatalogItemsListRefinementsBrandsItem"></a>

`CatalogItemsListRefinementsBrandsItem(**data: Any)`
:   Nested schema for CatalogItemsListRefinements.brands_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `brand_name: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `number_of_results: int | Any`
    :   The type of the None singleton.

<a id="CatalogItemsListRefinementsClassificationsItem"></a>

`CatalogItemsListRefinementsClassificationsItem(**data: Any)`
:   Nested schema for CatalogItemsListRefinements.classifications_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `classification_id: str | Any`
    :   The type of the None singleton.

    `display_name: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `number_of_results: int | Any`
    :   The type of the None singleton.

<a id="CatalogItemsListResultMeta"></a>

`CatalogItemsListResultMeta(**data: Any)`
:   Metadata for catalog_items.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_token: str | Any`
    :   The type of the None singleton.

    `number_of_results: int | Any`
    :   The type of the None singleton.

<a id="FinancialEventGroup"></a>

`FinancialEventGroup(**data: Any)`
:   A financial event group
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_tail: str | Any`
    :   The type of the None singleton.

    `beginning_balance: airbyte_agent_sdk.connectors.amazon_seller_partner.models.FinancialEventGroupBeginningbalance | Any`
    :   The type of the None singleton.

    `converted_total: airbyte_agent_sdk.connectors.amazon_seller_partner.models.FinancialEventGroupConvertedtotal | Any`
    :   The type of the None singleton.

    `financial_event_group_end: str | Any`
    :   The type of the None singleton.

    `financial_event_group_id: str | Any`
    :   The type of the None singleton.

    `financial_event_group_start: str | Any`
    :   The type of the None singleton.

    `fund_transfer_date: str | Any`
    :   The type of the None singleton.

    `fund_transfer_status: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `original_total: airbyte_agent_sdk.connectors.amazon_seller_partner.models.FinancialEventGroupOriginaltotal | Any`
    :   The type of the None singleton.

    `processing_status: str | Any`
    :   The type of the None singleton.

    `trace_id: str | Any`
    :   The type of the None singleton.

<a id="FinancialEventGroupBeginningbalance"></a>

`FinancialEventGroupBeginningbalance(**data: Any)`
:   Beginning balance
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `currency_amount: float | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FinancialEventGroupConvertedtotal"></a>

`FinancialEventGroupConvertedtotal(**data: Any)`
:   Converted total
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `currency_amount: float | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FinancialEventGroupList"></a>

`FinancialEventGroupList(**data: Any)`
:   Paginated list of financial event groups
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `payload: airbyte_agent_sdk.connectors.amazon_seller_partner.models.FinancialEventGroupListPayload | Any`
    :   The type of the None singleton.

<a id="FinancialEventGroupListPayload"></a>

`FinancialEventGroupListPayload(**data: Any)`
:   Nested schema for FinancialEventGroupList.payload
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `financial_event_group_list: list[airbyte_agent_sdk.connectors.amazon_seller_partner.models.FinancialEventGroup] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_token: str | Any`
    :   The type of the None singleton.

<a id="FinancialEventGroupOriginaltotal"></a>

`FinancialEventGroupOriginaltotal(**data: Any)`
:   Original total in seller's currency
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `currency_amount: float | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FinancialEvents"></a>

`FinancialEvents(**data: Any)`
:   A collection of financial events grouped by type
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `adhoc_disbursement_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `adjustment_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `affordability_expense_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `affordability_expense_reversal_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `capacity_reservation_billing_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `charge_refund_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `chargeback_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `coupon_payment_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `debt_recovery_event_list: list[airbyte_agent_sdk.connectors.amazon_seller_partner.models.FinancialEventsDebtrecoveryeventlistItem] | Any`
    :   The type of the None singleton.

    `ebt_refund_reimbursement_only_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `failed_adhoc_disbursement_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `fba_liquidation_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `guarantee_claim_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `imaging_services_fee_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `loan_servicing_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `network_commingling_transaction_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `pay_with_amazon_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `performance_bond_refund_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `product_ads_payment_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `refund_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `removal_shipment_adjustment_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `removal_shipment_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `rental_transaction_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `retrocharge_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `safet_reimbursement_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `seller_deal_payment_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `seller_review_enrollment_payment_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `service_fee_event_list: list[airbyte_agent_sdk.connectors.amazon_seller_partner.models.FinancialEventsServicefeeeventlistItem] | Any`
    :   The type of the None singleton.

    `service_provider_credit_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `shipment_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `shipment_settle_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `tax_withholding_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `tds_reimbursement_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `trial_shipment_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `value_added_service_charge_event_list: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

<a id="FinancialEventsDebtrecoveryeventlistItem"></a>

`FinancialEventsDebtrecoveryeventlistItem(**data: Any)`
:   Nested schema for FinancialEvents.DebtRecoveryEventList_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `charge_instrument_list: list[airbyte_agent_sdk.connectors.amazon_seller_partner.models.FinancialEventsDebtrecoveryeventlistItemChargeinstrumentlistItem] | Any`
    :   The type of the None singleton.

    `debt_recovery_item_list: list[airbyte_agent_sdk.connectors.amazon_seller_partner.models.FinancialEventsDebtrecoveryeventlistItemDebtrecoveryitemlistItem] | Any`
    :   The type of the None singleton.

    `debt_recovery_type: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `recovery_amount: airbyte_agent_sdk.connectors.amazon_seller_partner.models.FinancialEventsDebtrecoveryeventlistItemRecoveryamount | Any`
    :   The type of the None singleton.

<a id="FinancialEventsDebtrecoveryeventlistItemChargeinstrumentlistItem"></a>

`FinancialEventsDebtrecoveryeventlistItemChargeinstrumentlistItem(**data: Any)`
:   Nested schema for FinancialEventsDebtrecoveryeventlistItem.ChargeInstrumentList_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: airbyte_agent_sdk.connectors.amazon_seller_partner.models.FinancialEventsDebtrecoveryeventlistItemChargeinstrumentlistItemAmount | Any`
    :   The type of the None singleton.

    `description: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `tail: str | Any`
    :   The type of the None singleton.

<a id="FinancialEventsDebtrecoveryeventlistItemChargeinstrumentlistItemAmount"></a>

`FinancialEventsDebtrecoveryeventlistItemChargeinstrumentlistItemAmount(**data: Any)`
:   Nested schema for FinancialEventsDebtrecoveryeventlistItemChargeinstrumentlistItem.Amount
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `currency_amount: float | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FinancialEventsDebtrecoveryeventlistItemDebtrecoveryitemlistItem"></a>

`FinancialEventsDebtrecoveryeventlistItemDebtrecoveryitemlistItem(**data: Any)`
:   Nested schema for FinancialEventsDebtrecoveryeventlistItem.DebtRecoveryItemList_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `group_begin_date: str | Any`
    :   The type of the None singleton.

    `group_end_date: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `original_amount: airbyte_agent_sdk.connectors.amazon_seller_partner.models.FinancialEventsDebtrecoveryeventlistItemDebtrecoveryitemlistItemOriginalamount | Any`
    :   The type of the None singleton.

    `recovery_amount: airbyte_agent_sdk.connectors.amazon_seller_partner.models.FinancialEventsDebtrecoveryeventlistItemDebtrecoveryitemlistItemRecoveryamount | Any`
    :   The type of the None singleton.

<a id="FinancialEventsDebtrecoveryeventlistItemDebtrecoveryitemlistItemOriginalamount"></a>

`FinancialEventsDebtrecoveryeventlistItemDebtrecoveryitemlistItemOriginalamount(**data: Any)`
:   Nested schema for FinancialEventsDebtrecoveryeventlistItemDebtrecoveryitemlistItem.OriginalAmount
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `currency_amount: float | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FinancialEventsDebtrecoveryeventlistItemDebtrecoveryitemlistItemRecoveryamount"></a>

`FinancialEventsDebtrecoveryeventlistItemDebtrecoveryitemlistItemRecoveryamount(**data: Any)`
:   Nested schema for FinancialEventsDebtrecoveryeventlistItemDebtrecoveryitemlistItem.RecoveryAmount
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `currency_amount: float | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FinancialEventsDebtrecoveryeventlistItemRecoveryamount"></a>

`FinancialEventsDebtrecoveryeventlistItemRecoveryamount(**data: Any)`
:   Nested schema for FinancialEventsDebtrecoveryeventlistItem.RecoveryAmount
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `currency_amount: float | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FinancialEventsResponse"></a>

`FinancialEventsResponse(**data: Any)`
:   Response wrapper for financial events
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `payload: airbyte_agent_sdk.connectors.amazon_seller_partner.models.FinancialEventsResponsePayload | Any`
    :   The type of the None singleton.

<a id="FinancialEventsResponsePayload"></a>

`FinancialEventsResponsePayload(**data: Any)`
:   Nested schema for FinancialEventsResponse.payload
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `financial_events: airbyte_agent_sdk.connectors.amazon_seller_partner.models.FinancialEvents | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_token: str | Any`
    :   The type of the None singleton.

<a id="FinancialEventsServicefeeeventlistItem"></a>

`FinancialEventsServicefeeeventlistItem(**data: Any)`
:   Nested schema for FinancialEvents.ServiceFeeEventList_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `fee_list: list[airbyte_agent_sdk.connectors.amazon_seller_partner.models.FinancialEventsServicefeeeventlistItemFeelistItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FinancialEventsServicefeeeventlistItemFeelistItem"></a>

`FinancialEventsServicefeeeventlistItemFeelistItem(**data: Any)`
:   Nested schema for FinancialEventsServicefeeeventlistItem.FeeList_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `fee_amount: airbyte_agent_sdk.connectors.amazon_seller_partner.models.FinancialEventsServicefeeeventlistItemFeelistItemFeeamount | Any`
    :   The type of the None singleton.

    `fee_type: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FinancialEventsServicefeeeventlistItemFeelistItemFeeamount"></a>

`FinancialEventsServicefeeeventlistItemFeelistItemFeeamount(**data: Any)`
:   Nested schema for FinancialEventsServicefeeeventlistItemFeelistItem.FeeAmount
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `currency_amount: float | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ListFinancialEventGroupsListResultMeta"></a>

`ListFinancialEventGroupsListResultMeta(**data: Any)`
:   Metadata for list_financial_event_groups.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_token: str | Any`
    :   The type of the None singleton.

<a id="ListFinancialEventGroupsSearchData"></a>

`ListFinancialEventGroupsSearchData(**data: Any)`
:   Search result data for list_financial_event_groups entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_tail: str | None`
    :   The last digits of the account number

    `beginning_balance: dict[str, typing.Any] | None`
    :   Beginning balance

    `converted_total: dict[str, typing.Any] | None`
    :   Converted total

    `financial_event_group_end: str | None`
    :   End datetime of the financial event group

    `financial_event_group_id: str | None`
    :   Unique identifier for the financial event group

    `financial_event_group_start: str | None`
    :   Start datetime of the financial event group

    `fund_transfer_date: str | None`
    :   Date the fund transfer occurred

    `fund_transfer_status: str | None`
    :   Status of the fund transfer

    `model_config`
    :   The type of the None singleton.

    `original_total: dict[str, typing.Any] | None`
    :   Original total amount

    `processing_status: str | None`
    :   Processing status of the financial event group

    `trace_id: str | None`
    :   Unique identifier for tracing

<a id="ListFinancialEventsListResultMeta"></a>

`ListFinancialEventsListResultMeta(**data: Any)`
:   Metadata for list_financial_events.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_token: str | Any`
    :   The type of the None singleton.

<a id="ListFinancialEventsSearchData"></a>

`ListFinancialEventsSearchData(**data: Any)`
:   Search result data for list_financial_events entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `adhoc_disbursement_event_list: list[typing.Any] | None`
    :   List of adhoc disbursement events

    `adjustment_event_list: list[typing.Any] | None`
    :   List of adjustment events

    `affordability_expense_event_list: list[typing.Any] | None`
    :   List of affordability expense events

    `affordability_expense_reversal_event_list: list[typing.Any] | None`
    :   List of affordability expense reversal events

    `capacity_reservation_billing_event_list: list[typing.Any] | None`
    :   List of capacity reservation billing events

    `charge_refund_event_list: list[typing.Any] | None`
    :   List of charge refund events

    `chargeback_event_list: list[typing.Any] | None`
    :   List of chargeback events

    `coupon_payment_event_list: list[typing.Any] | None`
    :   List of coupon payment events

    `debt_recovery_event_list: list[typing.Any] | None`
    :   List of debt recovery events

    `failed_adhoc_disbursement_event_list: list[typing.Any] | None`
    :   List of failed adhoc disbursement events

    `fba_liquidation_event_list: list[typing.Any] | None`
    :   List of FBA liquidation events

    `guarantee_claim_event_list: list[typing.Any] | None`
    :   List of guarantee claim events

    `imaging_services_fee_event_list: list[typing.Any] | None`
    :   List of imaging services fee events

    `loan_servicing_event_list: list[typing.Any] | None`
    :   List of loan servicing events

    `model_config`
    :   The type of the None singleton.

    `network_commingling_transaction_event_list: list[typing.Any] | None`
    :   List of network commingling events

    `pay_with_amazon_event_list: list[typing.Any] | None`
    :   List of Pay with Amazon events

    `performance_bond_refund_event_list: list[typing.Any] | None`
    :   List of performance bond refund events

    `posted_before: str | None`
    :   Date filter for events posted before

    `product_ads_payment_event_list: list[typing.Any] | None`
    :   List of product ads payment events

    `refund_event_list: list[typing.Any] | None`
    :   List of refund events

    `removal_shipment_adjustment_event_list: list[typing.Any] | None`
    :   List of removal shipment adjustment events

    `removal_shipment_event_list: list[typing.Any] | None`
    :   List of removal shipment events

    `rental_transaction_event_list: list[typing.Any] | None`
    :   List of rental transaction events

    `retrocharge_event_list: list[typing.Any] | None`
    :   List of retrocharge events

    `safet_reimbursement_event_list: list[typing.Any] | None`
    :   List of SAFET reimbursement events

    `seller_deal_payment_event_list: list[typing.Any] | None`
    :   List of seller deal payment events

    `seller_review_enrollment_payment_event_list: list[typing.Any] | None`
    :   List of seller review enrollment events

    `service_fee_event_list: list[typing.Any] | None`
    :   List of service fee events

    `service_provider_credit_event_list: list[typing.Any] | None`
    :   List of service provider credit events

    `shipment_event_list: list[typing.Any] | None`
    :   List of shipment events

    `shipment_settle_event_list: list[typing.Any] | None`
    :   List of shipment settlement events

    `tax_withholding_event_list: list[typing.Any] | None`
    :   List of tax withholding events

    `tds_reimbursement_event_list: list[typing.Any] | None`
    :   List of TDS reimbursement events

    `trial_shipment_event_list: list[typing.Any] | None`
    :   List of trial shipment events

    `value_added_service_charge_event_list: list[typing.Any] | None`
    :   List of value-added service charge events

<a id="Order"></a>

`Order(**data: Any)`
:   Amazon order object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amazon_order_id: str | Any`
    :   The type of the None singleton.

    `automated_shipping_settings: airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrderAutomatedshippingsettings | Any`
    :   The type of the None singleton.

    `buyer_info: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `default_ship_from_location_address: airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrderDefaultshipfromlocationaddress | Any`
    :   The type of the None singleton.

    `earliest_delivery_date: str | Any`
    :   The type of the None singleton.

    `earliest_ship_date: str | Any`
    :   The type of the None singleton.

    `fulfillment_channel: str | Any`
    :   The type of the None singleton.

    `has_regulated_items: bool | Any`
    :   The type of the None singleton.

    `is_access_point_order: bool | Any`
    :   The type of the None singleton.

    `is_business_order: bool | Any`
    :   The type of the None singleton.

    `is_global_express_enabled: bool | Any`
    :   The type of the None singleton.

    `is_ispu: bool | Any`
    :   The type of the None singleton.

    `is_premium_order: bool | Any`
    :   The type of the None singleton.

    `is_prime: bool | Any`
    :   The type of the None singleton.

    `is_replacement_order: str | Any`
    :   The type of the None singleton.

    `is_sold_by_ab: bool | Any`
    :   The type of the None singleton.

    `last_update_date: str | Any`
    :   The type of the None singleton.

    `latest_delivery_date: str | Any`
    :   The type of the None singleton.

    `latest_ship_date: str | Any`
    :   The type of the None singleton.

    `marketplace_id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `number_of_items_shipped: int | Any`
    :   The type of the None singleton.

    `number_of_items_unshipped: int | Any`
    :   The type of the None singleton.

    `order_status: str | Any`
    :   The type of the None singleton.

    `order_total: airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrderOrdertotal | Any`
    :   The type of the None singleton.

    `order_type: str | Any`
    :   The type of the None singleton.

    `payment_method: str | Any`
    :   The type of the None singleton.

    `payment_method_details: list[str] | Any`
    :   The type of the None singleton.

    `purchase_date: str | Any`
    :   The type of the None singleton.

    `sales_channel: str | Any`
    :   The type of the None singleton.

    `seller_order_id: str | Any`
    :   The type of the None singleton.

    `ship_service_level: str | Any`
    :   The type of the None singleton.

    `shipment_service_level_category: str | Any`
    :   The type of the None singleton.

    `shipping_address: airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrderShippingaddress | Any`
    :   The type of the None singleton.

<a id="OrderAutomatedshippingsettings"></a>

`OrderAutomatedshippingsettings(**data: Any)`
:   Automated shipping settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_automated_shipping_settings: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderDefaultshipfromlocationaddress"></a>

`OrderDefaultshipfromlocationaddress(**data: Any)`
:   Default ship-from address
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address_line1: str | Any`
    :   The type of the None singleton.

    `city: str | Any`
    :   The type of the None singleton.

    `country_code: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `postal_code: str | Any`
    :   The type of the None singleton.

    `state_or_region: str | Any`
    :   The type of the None singleton.

<a id="OrderItem"></a>

`OrderItem(**data: Any)`
:   Amazon order item object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amazon_order_id: str | Any`
    :   The type of the None singleton.

    `asin: str | Any`
    :   The type of the None singleton.

    `buyer_info: airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrderItemBuyerinfo | Any`
    :   The type of the None singleton.

    `buyer_requested_cancel: airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrderItemBuyerrequestedcancel | Any`
    :   The type of the None singleton.

    `cod_fee: airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrderItemCodfee | Any`
    :   The type of the None singleton.

    `cod_fee_discount: airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrderItemCodfeediscount | Any`
    :   The type of the None singleton.

    `condition_id: str | Any`
    :   The type of the None singleton.

    `condition_note: str | Any`
    :   The type of the None singleton.

    `condition_subtype_id: str | Any`
    :   The type of the None singleton.

    `deemed_reseller_category: str | Any`
    :   The type of the None singleton.

    `ioss_number: str | Any`
    :   The type of the None singleton.

    `is_gift: str | Any`
    :   The type of the None singleton.

    `is_transparency: bool | Any`
    :   The type of the None singleton.

    `item_price: airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrderItemItemprice | Any`
    :   The type of the None singleton.

    `item_tax: airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrderItemItemtax | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `order_item_id: str | Any`
    :   The type of the None singleton.

    `points_granted: airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrderItemPointsgranted | Any`
    :   The type of the None singleton.

    `price_designation: str | Any`
    :   The type of the None singleton.

    `product_info: airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrderItemProductinfo | Any`
    :   The type of the None singleton.

    `promotion_discount: airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrderItemPromotiondiscount | Any`
    :   The type of the None singleton.

    `promotion_discount_tax: airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrderItemPromotiondiscounttax | Any`
    :   The type of the None singleton.

    `promotion_ids: list[str] | Any`
    :   The type of the None singleton.

    `quantity_ordered: int | Any`
    :   The type of the None singleton.

    `quantity_shipped: int | Any`
    :   The type of the None singleton.

    `seller_sku: str | Any`
    :   The type of the None singleton.

    `serial_number_required: bool | Any`
    :   The type of the None singleton.

    `shipping_discount: airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrderItemShippingdiscount | Any`
    :   The type of the None singleton.

    `shipping_discount_tax: airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrderItemShippingdiscounttax | Any`
    :   The type of the None singleton.

    `shipping_price: airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrderItemShippingprice | Any`
    :   The type of the None singleton.

    `shipping_tax: airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrderItemShippingtax | Any`
    :   The type of the None singleton.

    `store_chain_store_id: str | Any`
    :   The type of the None singleton.

    `tax_collection: airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrderItemTaxcollection | Any`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

<a id="OrderItemBuyerinfo"></a>

`OrderItemBuyerinfo(**data: Any)`
:   Buyer information for the item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `buyer_customized_info: airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrderItemBuyerinfoBuyercustomizedinfo | Any`
    :   The type of the None singleton.

    `gift_message_text: str | Any`
    :   The type of the None singleton.

    `gift_wrap_level: str | Any`
    :   The type of the None singleton.

    `gift_wrap_price: airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrderItemBuyerinfoGiftwrapprice | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderItemBuyerinfoBuyercustomizedinfo"></a>

`OrderItemBuyerinfoBuyercustomizedinfo(**data: Any)`
:   Nested schema for OrderItemBuyerinfo.BuyerCustomizedInfo
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `customized_url: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderItemBuyerinfoGiftwrapprice"></a>

`OrderItemBuyerinfoGiftwrapprice(**data: Any)`
:   Nested schema for OrderItemBuyerinfo.GiftWrapPrice
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderItemBuyerrequestedcancel"></a>

`OrderItemBuyerrequestedcancel(**data: Any)`
:   Buyer cancellation request information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `buyer_cancel_reason: str | Any`
    :   The type of the None singleton.

    `is_buyer_requested_cancel: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderItemCodfee"></a>

`OrderItemCodfee(**data: Any)`
:   Cash on delivery fee
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderItemCodfeediscount"></a>

`OrderItemCodfeediscount(**data: Any)`
:   Cash on delivery fee discount
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderItemItemprice"></a>

`OrderItemItemprice(**data: Any)`
:   Item price
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderItemItemtax"></a>

`OrderItemItemtax(**data: Any)`
:   Item tax
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderItemPointsgranted"></a>

`OrderItemPointsgranted(**data: Any)`
:   Points granted for the purchase
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `points_monetary_value: airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrderItemPointsgrantedPointsmonetaryvalue | Any`
    :   The type of the None singleton.

    `points_number: int | Any`
    :   The type of the None singleton.

<a id="OrderItemPointsgrantedPointsmonetaryvalue"></a>

`OrderItemPointsgrantedPointsmonetaryvalue(**data: Any)`
:   Nested schema for OrderItemPointsgranted.PointsMonetaryValue
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderItemProductinfo"></a>

`OrderItemProductinfo(**data: Any)`
:   Product information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `number_of_items: str | Any`
    :   The type of the None singleton.

<a id="OrderItemPromotiondiscount"></a>

`OrderItemPromotiondiscount(**data: Any)`
:   Promotion discount
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderItemPromotiondiscounttax"></a>

`OrderItemPromotiondiscounttax(**data: Any)`
:   Promotion discount tax
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderItemShippingdiscount"></a>

`OrderItemShippingdiscount(**data: Any)`
:   Shipping discount
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderItemShippingdiscounttax"></a>

`OrderItemShippingdiscounttax(**data: Any)`
:   Shipping discount tax
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderItemShippingprice"></a>

`OrderItemShippingprice(**data: Any)`
:   Shipping price
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderItemShippingtax"></a>

`OrderItemShippingtax(**data: Any)`
:   Shipping tax
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderItemTaxcollection"></a>

`OrderItemTaxcollection(**data: Any)`
:   Tax collection information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `responsible_party: str | Any`
    :   The type of the None singleton.

<a id="OrderItemsList"></a>

`OrderItemsList(**data: Any)`
:   Paginated list of order items
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `payload: airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrderItemsListPayload | Any`
    :   The type of the None singleton.

<a id="OrderItemsListPayload"></a>

`OrderItemsListPayload(**data: Any)`
:   Nested schema for OrderItemsList.payload
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amazon_order_id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_token: str | Any`
    :   The type of the None singleton.

    `order_items: list[airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrderItem] | Any`
    :   The type of the None singleton.

<a id="OrderItemsListResultMeta"></a>

`OrderItemsListResultMeta(**data: Any)`
:   Metadata for order_items.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_token: str | Any`
    :   The type of the None singleton.

<a id="OrderItemsSearchData"></a>

`OrderItemsSearchData(**data: Any)`
:   Search result data for order_items entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amazon_order_id: str | None`
    :   ID of the Amazon order

    `asin: str | None`
    :   Amazon Standard Identification Number of the product

    `buyer_info: dict[str, typing.Any] | None`
    :   Information about the buyer

    `buyer_requested_cancel: dict[str, typing.Any] | None`
    :   Information about buyer's request for cancellation

    `cod_fee: dict[str, typing.Any] | None`
    :   Cash on delivery fee

    `cod_fee_discount: dict[str, typing.Any] | None`
    :   Discount on cash on delivery fee

    `condition_id: str | None`
    :   Condition ID of the product

    `condition_note: str | None`
    :   Additional notes on the condition of the product

    `condition_subtype_id: str | None`
    :   Subtype ID of the product condition

    `deemed_reseller_category: str | None`
    :   Category indicating if the seller is considered a reseller

    `ioss_number: str | None`
    :   Import One Stop Shop number

    `is_gift: str | None`
    :   Flag indicating if the order is a gift

    `is_transparency: bool | None`
    :   Flag indicating if transparency is applied

    `item_price: dict[str, typing.Any] | None`
    :   Price of the item

    `item_tax: dict[str, typing.Any] | None`
    :   Tax applied on the item

    `last_update_date: str | None`
    :   Date and time of the last update

    `model_config`
    :   The type of the None singleton.

    `order_item_id: str | None`
    :   ID of the order item

    `points_granted: dict[str, typing.Any] | None`
    :   Points granted for the purchase

    `price_designation: str | None`
    :   Designation of the price

    `product_info: dict[str, typing.Any] | None`
    :   Information about the product

    `promotion_discount: dict[str, typing.Any] | None`
    :   Discount applied due to promotion

    `promotion_discount_tax: dict[str, typing.Any] | None`
    :   Tax applied on the promotion discount

    `promotion_ids: list[typing.Any] | None`
    :   IDs of promotions applied

    `quantity_ordered: int | None`
    :   Quantity of the item ordered

    `quantity_shipped: int | None`
    :   Quantity of the item shipped

    `scheduled_delivery_end_date: str | None`
    :   End date for scheduled delivery

    `scheduled_delivery_start_date: str | None`
    :   Start date for scheduled delivery

    `seller_sku: str | None`
    :   SKU of the seller

    `serial_number_required: bool | None`
    :   Flag indicating if serial number is required

    `serial_numbers: list[typing.Any] | None`
    :   List of serial numbers

    `shipping_discount: dict[str, typing.Any] | None`
    :   Discount applied on shipping

    `shipping_discount_tax: dict[str, typing.Any] | None`
    :   Tax applied on the shipping discount

    `shipping_price: dict[str, typing.Any] | None`
    :   Price of shipping

    `shipping_tax: dict[str, typing.Any] | None`
    :   Tax applied on shipping

    `store_chain_store_id: str | None`
    :   ID of the store chain

    `tax_collection: dict[str, typing.Any] | None`
    :   Information about tax collection

    `title: str | None`
    :   Title of the product

<a id="OrderOrdertotal"></a>

`OrderOrdertotal(**data: Any)`
:   Total amount of the order
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | Any`
    :   The type of the None singleton.

    `currency_code: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrderShippingaddress"></a>

`OrderShippingaddress(**data: Any)`
:   Shipping address for the order
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `city: str | Any`
    :   The type of the None singleton.

    `country_code: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `postal_code: str | Any`
    :   The type of the None singleton.

    `state_or_region: str | Any`
    :   The type of the None singleton.

<a id="OrdersList"></a>

`OrdersList(**data: Any)`
:   Paginated list of orders
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `payload: airbyte_agent_sdk.connectors.amazon_seller_partner.models.OrdersListPayload | Any`
    :   The type of the None singleton.

<a id="OrdersListPayload"></a>

`OrdersListPayload(**data: Any)`
:   Nested schema for OrdersList.payload
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_token: str | Any`
    :   Pagination token for next page

    `orders: list[airbyte_agent_sdk.connectors.amazon_seller_partner.models.Order] | Any`
    :   The type of the None singleton.

<a id="OrdersListResultMeta"></a>

`OrdersListResultMeta(**data: Any)`
:   Metadata for orders.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_token: str | Any`
    :   The type of the None singleton.

<a id="OrdersSearchData"></a>

`OrdersSearchData(**data: Any)`
:   Search result data for orders entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amazon_order_id: str | None`
    :   Unique identifier for the Amazon order

    `automated_shipping_settings: dict[str, typing.Any] | None`
    :   Settings related to automated shipping processes

    `buyer_info: dict[str, typing.Any] | None`
    :   Information about the buyer

    `default_ship_from_location_address: dict[str, typing.Any] | None`
    :   The default address from which orders are shipped

    `earliest_delivery_date: str | None`
    :   Earliest estimated delivery date of the order

    `earliest_ship_date: str | None`
    :   Earliest shipment date for the order

    `fulfillment_channel: str | None`
    :   Channel through which the order is fulfilled

    `has_regulated_items: bool | None`
    :   Indicates if the order has regulated items

    `is_access_point_order: bool | None`
    :   Indicates if the order is an Amazon Hub Counter order

    `is_business_order: bool | None`
    :   Indicates if the order is a business order

    `is_global_express_enabled: bool | None`
    :   Indicates if global express is enabled for the order

    `is_ispu: bool | None`
    :   Indicates if the order is for In-Store Pickup

    `is_premium_order: bool | None`
    :   Indicates if the order is a premium order

    `is_prime: bool | None`
    :   Indicates if the order is a Prime order

    `is_replacement_order: str | None`
    :   Indicates if the order is a replacement order

    `is_sold_by_ab: bool | None`
    :   Indicates if the order is sold by Amazon Business

    `last_update_date: str | None`
    :   Date and time when the order was last updated

    `latest_delivery_date: str | None`
    :   Latest estimated delivery date of the order

    `latest_ship_date: str | None`
    :   Latest shipment date for the order

    `marketplace_id: str | None`
    :   Identifier for the marketplace where the order was placed

    `model_config`
    :   The type of the None singleton.

    `number_of_items_shipped: int | None`
    :   Number of items shipped in the order

    `number_of_items_unshipped: int | None`
    :   Number of items yet to be shipped in the order

    `order_status: str | None`
    :   Status of the order

    `order_total: dict[str, typing.Any] | None`
    :   Total amount of the order

    `order_type: str | None`
    :   Type of the order

    `payment_method: str | None`
    :   Payment method used for the order

    `payment_method_details: list[typing.Any] | None`
    :   Details of the payment method used for the order

    `purchase_date: str | None`
    :   Date and time when the order was purchased

    `sales_channel: str | None`
    :   Channel through which the order was sold

    `seller_id: str | None`
    :   Identifier for the seller associated with the order

    `seller_order_id: str | None`
    :   Unique identifier given by the seller for the order

    `ship_service_level: str | None`
    :   Service level for shipping the order

    `shipment_service_level_category: str | None`
    :   Service level category for shipping the order

    `shipping_address: dict[str, typing.Any] | None`
    :   The address to which the order will be shipped

<a id="Report"></a>

`Report(**data: Any)`
:   Amazon SP-API report
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_time: str | Any`
    :   The type of the None singleton.

    `data_end_time: str | Any`
    :   The type of the None singleton.

    `data_start_time: str | Any`
    :   The type of the None singleton.

    `marketplace_ids: list[str] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `processing_end_time: str | Any`
    :   The type of the None singleton.

    `processing_start_time: str | Any`
    :   The type of the None singleton.

    `processing_status: str | Any`
    :   The type of the None singleton.

    `report_document_id: str | Any`
    :   The type of the None singleton.

    `report_id: str | Any`
    :   The type of the None singleton.

    `report_schedule_id: str | Any`
    :   The type of the None singleton.

    `report_type: str | Any`
    :   The type of the None singleton.

<a id="ReportsList"></a>

`ReportsList(**data: Any)`
:   Paginated list of reports
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_token: str | Any`
    :   The type of the None singleton.

    `reports: list[airbyte_agent_sdk.connectors.amazon_seller_partner.models.Report] | Any`
    :   The type of the None singleton.

<a id="ReportsListResultMeta"></a>

`ReportsListResultMeta(**data: Any)`
:   Metadata for reports.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_token: str | Any`
    :   The type of the None singleton.