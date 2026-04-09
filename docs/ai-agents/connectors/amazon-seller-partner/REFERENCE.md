# Amazon-Seller-Partner full reference

This is the full reference documentation for the Amazon-Seller-Partner agent connector.

## Supported entities and actions

The Amazon-Seller-Partner connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Orders | [List](#orders-list), [Get](#orders-get), [Search](#orders-search) |
| Order Items | [List](#order-items-list), [Search](#order-items-search) |
| List Financial Event Groups | [List](#list-financial-event-groups-list), [Search](#list-financial-event-groups-search) |
| List Financial Events | [List](#list-financial-events-list), [Search](#list-financial-events-search) |
| Catalog Items | [List](#catalog-items-list), [Get](#catalog-items-get) |
| Reports | [List](#reports-list), [Get](#reports-get) |

## Orders

### Orders List

Returns a list of orders based on the specified parameters.

#### Python SDK

```python
await amazon_seller_partner.orders.list(
    marketplace_ids="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "orders",
    "action": "list",
    "params": {
        "MarketplaceIds": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `MarketplaceIds` | `string` | Yes | A list of MarketplaceId values. Used to select orders placed in the specified marketplaces. |
| `CreatedAfter` | `string` | No | A date used for selecting orders created after the specified date (ISO 8601 format). Required if LastUpdatedAfter is not set. |
| `CreatedBefore` | `string` | No | A date used for selecting orders created before the specified date (ISO 8601 format). |
| `LastUpdatedAfter` | `string` | No | A date used for selecting orders that were last updated after the specified date (ISO 8601 format). |
| `LastUpdatedBefore` | `string` | No | A date used for selecting orders that were last updated before the specified date (ISO 8601 format). |
| `OrderStatuses` | `string` | No | Filter by order status values. |
| `MaxResultsPerPage` | `integer` | No | Maximum number of results to return per page. |
| `NextToken` | `string` | No | A string token returned in a previous response for pagination. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `AmazonOrderId` | `string` |  |
| `SellerOrderId` | `string` |  |
| `PurchaseDate` | `string` |  |
| `LastUpdateDate` | `string` |  |
| `OrderStatus` | `"Pending" \| "Unshipped" \| "PartiallyShipped" \| "Shipped" \| "Canceled" \| "Unfulfillable" \| "InvoiceUnconfirmed" \| "PendingAvailability"` |  |
| `FulfillmentChannel` | `string` |  |
| `SalesChannel` | `string` |  |
| `ShipServiceLevel` | `string` |  |
| `OrderTotal` | `object` |  |
| `NumberOfItemsShipped` | `integer` |  |
| `NumberOfItemsUnshipped` | `integer` |  |
| `PaymentMethod` | `string` |  |
| `PaymentMethodDetails` | `array<string>` |  |
| `MarketplaceId` | `string` |  |
| `ShipmentServiceLevelCategory` | `string` |  |
| `OrderType` | `string` |  |
| `EarliestShipDate` | `string` |  |
| `LatestShipDate` | `string` |  |
| `EarliestDeliveryDate` | `string` |  |
| `LatestDeliveryDate` | `string` |  |
| `IsBusinessOrder` | `boolean` |  |
| `IsPrime` | `boolean` |  |
| `IsGlobalExpressEnabled` | `boolean` |  |
| `IsPremiumOrder` | `boolean` |  |
| `IsSoldByAB` | `boolean` |  |
| `IsReplacementOrder` | `string` |  |
| `IsISPU` | `boolean` |  |
| `IsAccessPointOrder` | `boolean` |  |
| `HasRegulatedItems` | `boolean` |  |
| `ShippingAddress` | `object` |  |
| `DefaultShipFromLocationAddress` | `object` |  |
| `AutomatedShippingSettings` | `object` |  |
| `BuyerInfo` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_token` | `string` |  |

</details>

### Orders Get

Returns the order indicated by the specified order ID.

#### Python SDK

```python
await amazon_seller_partner.orders.get(
    order_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "orders",
    "action": "get",
    "params": {
        "orderId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `orderId` | `string` | Yes | An Amazon order identifier in 3-7-7 format. |


### Orders Search

Search and filter orders records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await amazon_seller_partner.orders.search(
    query={"filter": {"eq": {"AmazonOrderId": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "orders",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"AmazonOrderId": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `AmazonOrderId` | `string` | Unique identifier for the Amazon order |
| `AutomatedShippingSettings` | `object` | Settings related to automated shipping processes |
| `BuyerInfo` | `object` | Information about the buyer |
| `DefaultShipFromLocationAddress` | `object` | The default address from which orders are shipped |
| `EarliestDeliveryDate` | `string` | Earliest estimated delivery date of the order |
| `EarliestShipDate` | `string` | Earliest shipment date for the order |
| `FulfillmentChannel` | `string` | Channel through which the order is fulfilled |
| `HasRegulatedItems` | `boolean` | Indicates if the order has regulated items |
| `IsAccessPointOrder` | `boolean` | Indicates if the order is an Amazon Hub Counter order |
| `IsBusinessOrder` | `boolean` | Indicates if the order is a business order |
| `IsGlobalExpressEnabled` | `boolean` | Indicates if global express is enabled for the order |
| `IsISPU` | `boolean` | Indicates if the order is for In-Store Pickup |
| `IsPremiumOrder` | `boolean` | Indicates if the order is a premium order |
| `IsPrime` | `boolean` | Indicates if the order is a Prime order |
| `IsReplacementOrder` | `string` | Indicates if the order is a replacement order |
| `IsSoldByAB` | `boolean` | Indicates if the order is sold by Amazon Business |
| `LastUpdateDate` | `string` | Date and time when the order was last updated |
| `LatestDeliveryDate` | `string` | Latest estimated delivery date of the order |
| `LatestShipDate` | `string` | Latest shipment date for the order |
| `MarketplaceId` | `string` | Identifier for the marketplace where the order was placed |
| `NumberOfItemsShipped` | `integer` | Number of items shipped in the order |
| `NumberOfItemsUnshipped` | `integer` | Number of items yet to be shipped in the order |
| `OrderStatus` | `string` | Status of the order |
| `OrderTotal` | `object` | Total amount of the order |
| `OrderType` | `string` | Type of the order |
| `PaymentMethod` | `string` | Payment method used for the order |
| `PaymentMethodDetails` | `array` | Details of the payment method used for the order |
| `PurchaseDate` | `string` | Date and time when the order was purchased |
| `SalesChannel` | `string` | Channel through which the order was sold |
| `SellerOrderId` | `string` | Unique identifier given by the seller for the order |
| `ShipServiceLevel` | `string` | Service level for shipping the order |
| `ShipmentServiceLevelCategory` | `string` | Service level category for shipping the order |
| `ShippingAddress` | `object` | The address to which the order will be shipped |
| `seller_id` | `string` | Identifier for the seller associated with the order |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].AmazonOrderId` | `string` | Unique identifier for the Amazon order |
| `data[].AutomatedShippingSettings` | `object` | Settings related to automated shipping processes |
| `data[].BuyerInfo` | `object` | Information about the buyer |
| `data[].DefaultShipFromLocationAddress` | `object` | The default address from which orders are shipped |
| `data[].EarliestDeliveryDate` | `string` | Earliest estimated delivery date of the order |
| `data[].EarliestShipDate` | `string` | Earliest shipment date for the order |
| `data[].FulfillmentChannel` | `string` | Channel through which the order is fulfilled |
| `data[].HasRegulatedItems` | `boolean` | Indicates if the order has regulated items |
| `data[].IsAccessPointOrder` | `boolean` | Indicates if the order is an Amazon Hub Counter order |
| `data[].IsBusinessOrder` | `boolean` | Indicates if the order is a business order |
| `data[].IsGlobalExpressEnabled` | `boolean` | Indicates if global express is enabled for the order |
| `data[].IsISPU` | `boolean` | Indicates if the order is for In-Store Pickup |
| `data[].IsPremiumOrder` | `boolean` | Indicates if the order is a premium order |
| `data[].IsPrime` | `boolean` | Indicates if the order is a Prime order |
| `data[].IsReplacementOrder` | `string` | Indicates if the order is a replacement order |
| `data[].IsSoldByAB` | `boolean` | Indicates if the order is sold by Amazon Business |
| `data[].LastUpdateDate` | `string` | Date and time when the order was last updated |
| `data[].LatestDeliveryDate` | `string` | Latest estimated delivery date of the order |
| `data[].LatestShipDate` | `string` | Latest shipment date for the order |
| `data[].MarketplaceId` | `string` | Identifier for the marketplace where the order was placed |
| `data[].NumberOfItemsShipped` | `integer` | Number of items shipped in the order |
| `data[].NumberOfItemsUnshipped` | `integer` | Number of items yet to be shipped in the order |
| `data[].OrderStatus` | `string` | Status of the order |
| `data[].OrderTotal` | `object` | Total amount of the order |
| `data[].OrderType` | `string` | Type of the order |
| `data[].PaymentMethod` | `string` | Payment method used for the order |
| `data[].PaymentMethodDetails` | `array` | Details of the payment method used for the order |
| `data[].PurchaseDate` | `string` | Date and time when the order was purchased |
| `data[].SalesChannel` | `string` | Channel through which the order was sold |
| `data[].SellerOrderId` | `string` | Unique identifier given by the seller for the order |
| `data[].ShipServiceLevel` | `string` | Service level for shipping the order |
| `data[].ShipmentServiceLevelCategory` | `string` | Service level category for shipping the order |
| `data[].ShippingAddress` | `object` | The address to which the order will be shipped |
| `data[].seller_id` | `string` | Identifier for the seller associated with the order |

</details>

## Order Items

### Order Items List

Returns detailed order item information for the order indicated by the specified order ID.

#### Python SDK

```python
await amazon_seller_partner.order_items.list(
    order_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "order_items",
    "action": "list",
    "params": {
        "orderId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `orderId` | `string` | Yes | An Amazon order identifier in 3-7-7 format. |
| `NextToken` | `string` | No | A string token returned in a previous response for pagination. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `OrderItemId` | `string` |  |
| `AmazonOrderId` | `string` |  |
| `ASIN` | `string` |  |
| `SellerSKU` | `string` |  |
| `Title` | `string` |  |
| `QuantityOrdered` | `integer` |  |
| `QuantityShipped` | `integer` |  |
| `ItemPrice` | `object` |  |
| `ItemTax` | `object` |  |
| `ShippingPrice` | `object` |  |
| `ShippingTax` | `object` |  |
| `ShippingDiscount` | `object` |  |
| `ShippingDiscountTax` | `object` |  |
| `PromotionDiscount` | `object` |  |
| `PromotionDiscountTax` | `object` |  |
| `PromotionIds` | `array<string>` |  |
| `CODFee` | `object` |  |
| `CODFeeDiscount` | `object` |  |
| `IsGift` | `string` |  |
| `ConditionId` | `string` |  |
| `ConditionSubtypeId` | `string` |  |
| `ConditionNote` | `string` |  |
| `IsTransparency` | `boolean` |  |
| `SerialNumberRequired` | `boolean` |  |
| `IossNumber` | `string` |  |
| `DeemedResellerCategory` | `string` |  |
| `StoreChainStoreId` | `string` |  |
| `ProductInfo` | `object` |  |
| `BuyerInfo` | `object` |  |
| `BuyerRequestedCancel` | `object` |  |
| `PointsGranted` | `object` |  |
| `TaxCollection` | `object` |  |
| `PriceDesignation` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_token` | `string` |  |

</details>

### Order Items Search

Search and filter order items records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await amazon_seller_partner.order_items.search(
    query={"filter": {"eq": {"ASIN": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "order_items",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"ASIN": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `ASIN` | `string` | Amazon Standard Identification Number of the product |
| `AmazonOrderId` | `string` | ID of the Amazon order |
| `BuyerInfo` | `object` | Information about the buyer |
| `BuyerRequestedCancel` | `object` | Information about buyer's request for cancellation |
| `CODFee` | `object` | Cash on delivery fee |
| `CODFeeDiscount` | `object` | Discount on cash on delivery fee |
| `ConditionId` | `string` | Condition ID of the product |
| `ConditionNote` | `string` | Additional notes on the condition of the product |
| `ConditionSubtypeId` | `string` | Subtype ID of the product condition |
| `DeemedResellerCategory` | `string` | Category indicating if the seller is considered a reseller |
| `IossNumber` | `string` | Import One Stop Shop number |
| `IsGift` | `string` | Flag indicating if the order is a gift |
| `IsTransparency` | `boolean` | Flag indicating if transparency is applied |
| `ItemPrice` | `object` | Price of the item |
| `ItemTax` | `object` | Tax applied on the item |
| `LastUpdateDate` | `string` | Date and time of the last update |
| `OrderItemId` | `string` | ID of the order item |
| `PointsGranted` | `object` | Points granted for the purchase |
| `PriceDesignation` | `string` | Designation of the price |
| `ProductInfo` | `object` | Information about the product |
| `PromotionDiscount` | `object` | Discount applied due to promotion |
| `PromotionDiscountTax` | `object` | Tax applied on the promotion discount |
| `PromotionIds` | `array` | IDs of promotions applied |
| `QuantityOrdered` | `integer` | Quantity of the item ordered |
| `QuantityShipped` | `integer` | Quantity of the item shipped |
| `ScheduledDeliveryEndDate` | `string` | End date for scheduled delivery |
| `ScheduledDeliveryStartDate` | `string` | Start date for scheduled delivery |
| `SellerSKU` | `string` | SKU of the seller |
| `SerialNumberRequired` | `boolean` | Flag indicating if serial number is required |
| `SerialNumbers` | `array` | List of serial numbers |
| `ShippingDiscount` | `object` | Discount applied on shipping |
| `ShippingDiscountTax` | `object` | Tax applied on the shipping discount |
| `ShippingPrice` | `object` | Price of shipping |
| `ShippingTax` | `object` | Tax applied on shipping |
| `StoreChainStoreId` | `string` | ID of the store chain |
| `TaxCollection` | `object` | Information about tax collection |
| `Title` | `string` | Title of the product |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].ASIN` | `string` | Amazon Standard Identification Number of the product |
| `data[].AmazonOrderId` | `string` | ID of the Amazon order |
| `data[].BuyerInfo` | `object` | Information about the buyer |
| `data[].BuyerRequestedCancel` | `object` | Information about buyer's request for cancellation |
| `data[].CODFee` | `object` | Cash on delivery fee |
| `data[].CODFeeDiscount` | `object` | Discount on cash on delivery fee |
| `data[].ConditionId` | `string` | Condition ID of the product |
| `data[].ConditionNote` | `string` | Additional notes on the condition of the product |
| `data[].ConditionSubtypeId` | `string` | Subtype ID of the product condition |
| `data[].DeemedResellerCategory` | `string` | Category indicating if the seller is considered a reseller |
| `data[].IossNumber` | `string` | Import One Stop Shop number |
| `data[].IsGift` | `string` | Flag indicating if the order is a gift |
| `data[].IsTransparency` | `boolean` | Flag indicating if transparency is applied |
| `data[].ItemPrice` | `object` | Price of the item |
| `data[].ItemTax` | `object` | Tax applied on the item |
| `data[].LastUpdateDate` | `string` | Date and time of the last update |
| `data[].OrderItemId` | `string` | ID of the order item |
| `data[].PointsGranted` | `object` | Points granted for the purchase |
| `data[].PriceDesignation` | `string` | Designation of the price |
| `data[].ProductInfo` | `object` | Information about the product |
| `data[].PromotionDiscount` | `object` | Discount applied due to promotion |
| `data[].PromotionDiscountTax` | `object` | Tax applied on the promotion discount |
| `data[].PromotionIds` | `array` | IDs of promotions applied |
| `data[].QuantityOrdered` | `integer` | Quantity of the item ordered |
| `data[].QuantityShipped` | `integer` | Quantity of the item shipped |
| `data[].ScheduledDeliveryEndDate` | `string` | End date for scheduled delivery |
| `data[].ScheduledDeliveryStartDate` | `string` | Start date for scheduled delivery |
| `data[].SellerSKU` | `string` | SKU of the seller |
| `data[].SerialNumberRequired` | `boolean` | Flag indicating if serial number is required |
| `data[].SerialNumbers` | `array` | List of serial numbers |
| `data[].ShippingDiscount` | `object` | Discount applied on shipping |
| `data[].ShippingDiscountTax` | `object` | Tax applied on the shipping discount |
| `data[].ShippingPrice` | `object` | Price of shipping |
| `data[].ShippingTax` | `object` | Tax applied on shipping |
| `data[].StoreChainStoreId` | `string` | ID of the store chain |
| `data[].TaxCollection` | `object` | Information about tax collection |
| `data[].Title` | `string` | Title of the product |

</details>

## List Financial Event Groups

### List Financial Event Groups List

Returns financial event groups for a given date range.

#### Python SDK

```python
await amazon_seller_partner.list_financial_event_groups.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "list_financial_event_groups",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `FinancialEventGroupStartedAfter` | `string` | No | Return groups opened after this date (ISO 8601 format). |
| `FinancialEventGroupStartedBefore` | `string` | No | Return groups opened before this date (ISO 8601 format). |
| `MaxResultsPerPage` | `integer` | No | Maximum number of results to return per page. |
| `NextToken` | `string` | No | A string token returned in a previous response for pagination. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `FinancialEventGroupId` | `string` |  |
| `ProcessingStatus` | `string` |  |
| `FundTransferStatus` | `string` |  |
| `OriginalTotal` | `object` |  |
| `ConvertedTotal` | `object` |  |
| `FundTransferDate` | `string` |  |
| `TraceId` | `string` |  |
| `AccountTail` | `string` |  |
| `BeginningBalance` | `object` |  |
| `FinancialEventGroupStart` | `string` |  |
| `FinancialEventGroupEnd` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_token` | `string` |  |

</details>

### List Financial Event Groups Search

Search and filter list financial event groups records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await amazon_seller_partner.list_financial_event_groups.search(
    query={"filter": {"eq": {"AccountTail": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "list_financial_event_groups",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"AccountTail": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `AccountTail` | `string` | The last digits of the account number |
| `BeginningBalance` | `object` | Beginning balance |
| `ConvertedTotal` | `object` | Converted total |
| `FinancialEventGroupEnd` | `string` | End datetime of the financial event group |
| `FinancialEventGroupId` | `string` | Unique identifier for the financial event group |
| `FinancialEventGroupStart` | `string` | Start datetime of the financial event group |
| `FundTransferDate` | `string` | Date the fund transfer occurred |
| `FundTransferStatus` | `string` | Status of the fund transfer |
| `OriginalTotal` | `object` | Original total amount |
| `ProcessingStatus` | `string` | Processing status of the financial event group |
| `TraceId` | `string` | Unique identifier for tracing |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].AccountTail` | `string` | The last digits of the account number |
| `data[].BeginningBalance` | `object` | Beginning balance |
| `data[].ConvertedTotal` | `object` | Converted total |
| `data[].FinancialEventGroupEnd` | `string` | End datetime of the financial event group |
| `data[].FinancialEventGroupId` | `string` | Unique identifier for the financial event group |
| `data[].FinancialEventGroupStart` | `string` | Start datetime of the financial event group |
| `data[].FundTransferDate` | `string` | Date the fund transfer occurred |
| `data[].FundTransferStatus` | `string` | Status of the fund transfer |
| `data[].OriginalTotal` | `object` | Original total amount |
| `data[].ProcessingStatus` | `string` | Processing status of the financial event group |
| `data[].TraceId` | `string` | Unique identifier for tracing |

</details>

## List Financial Events

### List Financial Events List

Returns financial events for a given date range.

#### Python SDK

```python
await amazon_seller_partner.list_financial_events.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "list_financial_events",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `PostedAfter` | `string` | No | Return events posted after this date (ISO 8601 format). |
| `PostedBefore` | `string` | No | Return events posted before this date (ISO 8601 format). |
| `MaxResultsPerPage` | `integer` | No | Maximum number of results to return per page. |
| `NextToken` | `string` | No | A string token returned in a previous response for pagination. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `ShipmentEventList` | `array<object>` |  |
| `ShipmentSettleEventList` | `array<object>` |  |
| `RefundEventList` | `array<object>` |  |
| `GuaranteeClaimEventList` | `array<object>` |  |
| `ChargebackEventList` | `array<object>` |  |
| `ChargeRefundEventList` | `array<object>` |  |
| `PayWithAmazonEventList` | `array<object>` |  |
| `ServiceProviderCreditEventList` | `array<object>` |  |
| `RetrochargeEventList` | `array<object>` |  |
| `RentalTransactionEventList` | `array<object>` |  |
| `ProductAdsPaymentEventList` | `array<object>` |  |
| `ServiceFeeEventList` | `array<object>` |  |
| `SellerDealPaymentEventList` | `array<object>` |  |
| `DebtRecoveryEventList` | `array<object>` |  |
| `LoanServicingEventList` | `array<object>` |  |
| `AdjustmentEventList` | `array<object>` |  |
| `SAFETReimbursementEventList` | `array<object>` |  |
| `SellerReviewEnrollmentPaymentEventList` | `array<object>` |  |
| `FBALiquidationEventList` | `array<object>` |  |
| `CouponPaymentEventList` | `array<object>` |  |
| `ImagingServicesFeeEventList` | `array<object>` |  |
| `NetworkComminglingTransactionEventList` | `array<object>` |  |
| `AffordabilityExpenseEventList` | `array<object>` |  |
| `AffordabilityExpenseReversalEventList` | `array<object>` |  |
| `TrialShipmentEventList` | `array<object>` |  |
| `TDSReimbursementEventList` | `array<object>` |  |
| `TaxWithholdingEventList` | `array<object>` |  |
| `RemovalShipmentEventList` | `array<object>` |  |
| `RemovalShipmentAdjustmentEventList` | `array<object>` |  |
| `ValueAddedServiceChargeEventList` | `array<object>` |  |
| `CapacityReservationBillingEventList` | `array<object>` |  |
| `FailedAdhocDisbursementEventList` | `array<object>` |  |
| `AdhocDisbursementEventList` | `array<object>` |  |
| `PerformanceBondRefundEventList` | `array<object>` |  |
| `EBTRefundReimbursementOnlyEventList` | `array<object>` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_token` | `string` |  |

</details>

### List Financial Events Search

Search and filter list financial events records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await amazon_seller_partner.list_financial_events.search(
    query={"filter": {"eq": {"AdhocDisbursementEventList": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "list_financial_events",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"AdhocDisbursementEventList": []}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `AdhocDisbursementEventList` | `array` | List of adhoc disbursement events |
| `AdjustmentEventList` | `array` | List of adjustment events |
| `AffordabilityExpenseEventList` | `array` | List of affordability expense events |
| `AffordabilityExpenseReversalEventList` | `array` | List of affordability expense reversal events |
| `CapacityReservationBillingEventList` | `array` | List of capacity reservation billing events |
| `ChargeRefundEventList` | `array` | List of charge refund events |
| `ChargebackEventList` | `array` | List of chargeback events |
| `CouponPaymentEventList` | `array` | List of coupon payment events |
| `DebtRecoveryEventList` | `array` | List of debt recovery events |
| `FBALiquidationEventList` | `array` | List of FBA liquidation events |
| `FailedAdhocDisbursementEventList` | `array` | List of failed adhoc disbursement events |
| `GuaranteeClaimEventList` | `array` | List of guarantee claim events |
| `ImagingServicesFeeEventList` | `array` | List of imaging services fee events |
| `LoanServicingEventList` | `array` | List of loan servicing events |
| `NetworkComminglingTransactionEventList` | `array` | List of network commingling events |
| `PayWithAmazonEventList` | `array` | List of Pay with Amazon events |
| `PerformanceBondRefundEventList` | `array` | List of performance bond refund events |
| `PostedBefore` | `string` | Date filter for events posted before |
| `ProductAdsPaymentEventList` | `array` | List of product ads payment events |
| `RefundEventList` | `array` | List of refund events |
| `RemovalShipmentAdjustmentEventList` | `array` | List of removal shipment adjustment events |
| `RemovalShipmentEventList` | `array` | List of removal shipment events |
| `RentalTransactionEventList` | `array` | List of rental transaction events |
| `RetrochargeEventList` | `array` | List of retrocharge events |
| `SAFETReimbursementEventList` | `array` | List of SAFET reimbursement events |
| `SellerDealPaymentEventList` | `array` | List of seller deal payment events |
| `SellerReviewEnrollmentPaymentEventList` | `array` | List of seller review enrollment events |
| `ServiceFeeEventList` | `array` | List of service fee events |
| `ServiceProviderCreditEventList` | `array` | List of service provider credit events |
| `ShipmentEventList` | `array` | List of shipment events |
| `ShipmentSettleEventList` | `array` | List of shipment settlement events |
| `TDSReimbursementEventList` | `array` | List of TDS reimbursement events |
| `TaxWithholdingEventList` | `array` | List of tax withholding events |
| `TrialShipmentEventList` | `array` | List of trial shipment events |
| `ValueAddedServiceChargeEventList` | `array` | List of value-added service charge events |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].AdhocDisbursementEventList` | `array` | List of adhoc disbursement events |
| `data[].AdjustmentEventList` | `array` | List of adjustment events |
| `data[].AffordabilityExpenseEventList` | `array` | List of affordability expense events |
| `data[].AffordabilityExpenseReversalEventList` | `array` | List of affordability expense reversal events |
| `data[].CapacityReservationBillingEventList` | `array` | List of capacity reservation billing events |
| `data[].ChargeRefundEventList` | `array` | List of charge refund events |
| `data[].ChargebackEventList` | `array` | List of chargeback events |
| `data[].CouponPaymentEventList` | `array` | List of coupon payment events |
| `data[].DebtRecoveryEventList` | `array` | List of debt recovery events |
| `data[].FBALiquidationEventList` | `array` | List of FBA liquidation events |
| `data[].FailedAdhocDisbursementEventList` | `array` | List of failed adhoc disbursement events |
| `data[].GuaranteeClaimEventList` | `array` | List of guarantee claim events |
| `data[].ImagingServicesFeeEventList` | `array` | List of imaging services fee events |
| `data[].LoanServicingEventList` | `array` | List of loan servicing events |
| `data[].NetworkComminglingTransactionEventList` | `array` | List of network commingling events |
| `data[].PayWithAmazonEventList` | `array` | List of Pay with Amazon events |
| `data[].PerformanceBondRefundEventList` | `array` | List of performance bond refund events |
| `data[].PostedBefore` | `string` | Date filter for events posted before |
| `data[].ProductAdsPaymentEventList` | `array` | List of product ads payment events |
| `data[].RefundEventList` | `array` | List of refund events |
| `data[].RemovalShipmentAdjustmentEventList` | `array` | List of removal shipment adjustment events |
| `data[].RemovalShipmentEventList` | `array` | List of removal shipment events |
| `data[].RentalTransactionEventList` | `array` | List of rental transaction events |
| `data[].RetrochargeEventList` | `array` | List of retrocharge events |
| `data[].SAFETReimbursementEventList` | `array` | List of SAFET reimbursement events |
| `data[].SellerDealPaymentEventList` | `array` | List of seller deal payment events |
| `data[].SellerReviewEnrollmentPaymentEventList` | `array` | List of seller review enrollment events |
| `data[].ServiceFeeEventList` | `array` | List of service fee events |
| `data[].ServiceProviderCreditEventList` | `array` | List of service provider credit events |
| `data[].ShipmentEventList` | `array` | List of shipment events |
| `data[].ShipmentSettleEventList` | `array` | List of shipment settlement events |
| `data[].TDSReimbursementEventList` | `array` | List of TDS reimbursement events |
| `data[].TaxWithholdingEventList` | `array` | List of tax withholding events |
| `data[].TrialShipmentEventList` | `array` | List of trial shipment events |
| `data[].ValueAddedServiceChargeEventList` | `array` | List of value-added service charge events |

</details>

## Catalog Items

### Catalog Items List

Search for items in the Amazon catalog by keywords or identifiers.

#### Python SDK

```python
await amazon_seller_partner.catalog_items.list(
    marketplace_ids="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "catalog_items",
    "action": "list",
    "params": {
        "marketplaceIds": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `marketplaceIds` | `string` | Yes | A marketplace identifier. |
| `keywords` | `string` | No | Keywords to search for in the Amazon catalog. |
| `identifiers` | `string` | No | Product identifiers to search for (ASIN, EAN, UPC, etc.). |
| `identifiersType` | `"ASIN" \| "EAN" \| "GTIN" \| "ISBN" \| "JAN" \| "MINSAN" \| "SKU" \| "UPC"` | No | Type of identifiers (required when identifiers is set). |
| `includedData` | `string` | No | Data sets to include in the response. |
| `pageSize` | `integer` | No | Number of items to return per page. |
| `pageToken` | `string` | No | Token for pagination returned by a previous request. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `asin` | `string` |  |
| `attributes` | `object` |  |
| `classifications` | `array<object>` |  |
| `dimensions` | `array<object>` |  |
| `identifiers` | `array<object>` |  |
| `images` | `array<object>` |  |
| `productTypes` | `array<object>` |  |
| `relationships` | `array<object>` |  |
| `salesRanks` | `array<object>` |  |
| `summaries` | `array<object>` |  |
| `vendorDetails` | `array<object>` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_token` | `string` |  |
| `number_of_results` | `integer` |  |

</details>

### Catalog Items Get

Retrieves details for an item in the Amazon catalog by ASIN.

#### Python SDK

```python
await amazon_seller_partner.catalog_items.get(
    asin="<str>",
    marketplace_ids="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "catalog_items",
    "action": "get",
    "params": {
        "asin": "<str>",
        "marketplaceIds": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `asin` | `string` | Yes | The Amazon Standard Identification Number (ASIN) of the item. |
| `marketplaceIds` | `string` | Yes | A marketplace identifier. |
| `includedData` | `string` | No | Data sets to include in the response. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `asin` | `string` |  |
| `attributes` | `object` |  |
| `classifications` | `array<object>` |  |
| `dimensions` | `array<object>` |  |
| `identifiers` | `array<object>` |  |
| `images` | `array<object>` |  |
| `productTypes` | `array<object>` |  |
| `relationships` | `array<object>` |  |
| `salesRanks` | `array<object>` |  |
| `summaries` | `array<object>` |  |
| `vendorDetails` | `array<object>` |  |


</details>

## Reports

### Reports List

Returns report details for the reports that match the specified filters.

#### Python SDK

```python
await amazon_seller_partner.reports.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "reports",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `reportTypes` | `string` | No | A list of report types used to filter reports. |
| `processingStatuses` | `string` | No | A list of processing statuses used to filter reports. |
| `marketplaceIds` | `string` | No | A list of marketplace identifiers used to filter reports. |
| `pageSize` | `integer` | No | Maximum number of reports to return per page. |
| `createdSince` | `string` | No | Earliest report creation date and time (ISO 8601 format). |
| `createdUntil` | `string` | No | Latest report creation date and time (ISO 8601 format). |
| `nextToken` | `string` | No | A string token returned in a previous response for pagination. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `reportId` | `string` |  |
| `reportType` | `string` |  |
| `createdTime` | `string` |  |
| `processingStatus` | `"IN_QUEUE" \| "IN_PROGRESS" \| "DONE" \| "CANCELLED" \| "FATAL"` |  |
| `dataStartTime` | `string` |  |
| `dataEndTime` | `string` |  |
| `reportScheduleId` | `string` |  |
| `processingStartTime` | `string` |  |
| `processingEndTime` | `string` |  |
| `reportDocumentId` | `string` |  |
| `marketplaceIds` | `array<string>` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_token` | `string` |  |

</details>

### Reports Get

Returns report details including status and report document ID for a specified report.

#### Python SDK

```python
await amazon_seller_partner.reports.get(
    report_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "reports",
    "action": "get",
    "params": {
        "reportId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `reportId` | `string` | Yes | The identifier for the report. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `reportId` | `string` |  |
| `reportType` | `string` |  |
| `createdTime` | `string` |  |
| `processingStatus` | `"IN_QUEUE" \| "IN_PROGRESS" \| "DONE" \| "CANCELLED" \| "FATAL"` |  |
| `dataStartTime` | `string` |  |
| `dataEndTime` | `string` |  |
| `reportScheduleId` | `string` |  |
| `processingStartTime` | `string` |  |
| `processingEndTime` | `string` |  |
| `reportDocumentId` | `string` |  |
| `marketplaceIds` | `array<string>` |  |


</details>

