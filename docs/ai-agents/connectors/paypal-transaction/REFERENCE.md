# Paypal-Transaction full reference

This is the full reference documentation for the Paypal-Transaction agent connector.

## Supported entities and actions

The Paypal-Transaction connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Balances | [List](#balances-list), [Search](#balances-search) |
| Transactions | [List](#transactions-list), [Search](#transactions-search) |
| List Payments | [List](#list-payments-list), [Search](#list-payments-search) |
| List Disputes | [List](#list-disputes-list), [Search](#list-disputes-search) |
| List Products | [List](#list-products-list), [Search](#list-products-search) |
| Show Product Details | [Get](#show-product-details-get), [Search](#show-product-details-search) |
| Search Invoices | [List](#search-invoices-list), [Search](#search-invoices-search) |

## Balances

### Balances List

List all balances for a PayPal account. Specify date time to list balances for that time. It takes a maximum of three hours for balances to appear. Lists balances up to the previous three years.


#### Python SDK

```python
await paypal_transaction.balances.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "balances",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `as_of_time` | `string` | No | List balances at the date time provided in ISO 8601 format. Returns the last refreshed balance when not provided.
 |
| `currency_code` | `string` | No | Three-character ISO-4217 currency code to filter balances.
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `balances` | `array<object>` |  |
| `balances[].primary` | `boolean` |  |
| `balances[].currency` | `string` |  |
| `balances[].total_balance` | `object` |  |
| `balances[].total_balance.currency_code` | `string` |  |
| `balances[].total_balance.value` | `string` |  |
| `balances[].available_balance` | `object` |  |
| `balances[].available_balance.currency_code` | `string` |  |
| `balances[].available_balance.value` | `string` |  |
| `balances[].withheld_balance` | `object` |  |
| `balances[].withheld_balance.currency_code` | `string` |  |
| `balances[].withheld_balance.value` | `string` |  |
| `account_id` | `string` |  |
| `as_of_time` | `string` |  |
| `last_refresh_time` | `string` |  |


</details>

### Balances Search

Search and filter balances records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await paypal_transaction.balances.search(
    query={"filter": {"eq": {"account_id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "balances",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"account_id": "<str>"}}}
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
| `account_id` | `string` | The unique identifier of the account. |
| `as_of_time` | `string` | The timestamp when the balances data was reported. |
| `balances` | `array` | Object containing information about the account balances. |
| `last_refresh_time` | `string` | The timestamp when the balances data was last refreshed. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].account_id` | `string` | The unique identifier of the account. |
| `data[].as_of_time` | `string` | The timestamp when the balances data was reported. |
| `data[].balances` | `array` | Object containing information about the account balances. |
| `data[].last_refresh_time` | `string` | The timestamp when the balances data was last refreshed. |

</details>

## Transactions

### Transactions List

Lists transactions for a PayPal account. Specify one or more query parameters to filter the transactions. Requires start_date and end_date parameters. The maximum supported date range is 31 days. It takes a maximum of three hours for executed transactions to appear.


#### Python SDK

```python
await paypal_transaction.transactions.list(
    start_date="<str>",
    end_date="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "transactions",
    "action": "list",
    "params": {
        "start_date": "<str>",
        "end_date": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `start_date` | `string` | Yes | Start date and time in ISO 8601 format. Seconds are required.
 |
| `end_date` | `string` | Yes | End date and time in ISO 8601 format. Seconds are required. Maximum supported range is 31 days.
 |
| `transaction_id` | `string` | No | Filters by PayPal transaction ID (17-19 characters). |
| `transaction_type` | `string` | No | Filters by PayPal transaction event code. |
| `transaction_status` | `"D" \| "P" \| "S" \| "V"` | No | Filters by PayPal transaction status code. D=Denied, P=Pending, S=Successful, V=Reversed.
 |
| `transaction_currency` | `string` | No | Three-character ISO-4217 currency code. |
| `fields` | `string` | No | Fields to include in the response. Comma-separated list. Use 'all' to include all fields. Default is transaction_info.
 |
| `page_size` | `integer` | No | Number of items per page (1-500). |
| `page` | `integer` | No | Page number to return. |
| `balance_affecting_records_only` | `"Y" \| "N"` | No | Y to include only balance-impacting transactions (default). N to include all transactions.
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `transaction_info` | `object` |  |
| `transaction_info.paypal_account_id` | `string` |  |
| `transaction_info.transaction_id` | `string` |  |
| `transaction_info.paypal_reference_id` | `string` |  |
| `transaction_info.paypal_reference_id_type` | `string` |  |
| `transaction_info.transaction_event_code` | `string` |  |
| `transaction_info.transaction_initiation_date` | `string` |  |
| `transaction_info.transaction_updated_date` | `string` |  |
| `transaction_info.transaction_amount` | `object` |  |
| `transaction_info.transaction_amount.currency_code` | `string` |  |
| `transaction_info.transaction_amount.value` | `string` |  |
| `transaction_info.fee_amount` | `object` |  |
| `transaction_info.fee_amount.currency_code` | `string` |  |
| `transaction_info.fee_amount.value` | `string` |  |
| `transaction_info.insurance_amount` | `object` |  |
| `transaction_info.insurance_amount.currency_code` | `string` |  |
| `transaction_info.insurance_amount.value` | `string` |  |
| `transaction_info.shipping_amount` | `object` |  |
| `transaction_info.shipping_amount.currency_code` | `string` |  |
| `transaction_info.shipping_amount.value` | `string` |  |
| `transaction_info.shipping_discount_amount` | `object` |  |
| `transaction_info.shipping_discount_amount.currency_code` | `string` |  |
| `transaction_info.shipping_discount_amount.value` | `string` |  |
| `transaction_info.transaction_status` | `string` |  |
| `transaction_info.transaction_subject` | `string` |  |
| `transaction_info.transaction_note` | `string` |  |
| `transaction_info.invoice_id` | `string` |  |
| `transaction_info.custom_field` | `string` |  |
| `transaction_info.protection_eligibility` | `string` |  |
| `payer_info` | `object` |  |
| `payer_info.account_id` | `string` |  |
| `payer_info.email_address` | `string` |  |
| `payer_info.address_status` | `string` |  |
| `payer_info.payer_status` | `string` |  |
| `payer_info.payer_name` | `object` |  |
| `payer_info.payer_name.given_name` | `string` |  |
| `payer_info.payer_name.surname` | `string` |  |
| `payer_info.payer_name.alternate_full_name` | `string` |  |
| `payer_info.country_code` | `string` |  |
| `shipping_info` | `object` |  |
| `shipping_info.name` | `string` |  |
| `shipping_info.address` | `object` |  |
| `shipping_info.address.line1` | `string` |  |
| `shipping_info.address.line2` | `string` |  |
| `shipping_info.address.city` | `string` |  |
| `shipping_info.address.country_code` | `string` |  |
| `shipping_info.address.postal_code` | `string` |  |
| `cart_info` | `object` |  |
| `cart_info.item_details` | `array<object>` |  |
| `cart_info.item_details[].item_code` | `string` |  |
| `cart_info.item_details[].item_name` | `string` |  |
| `cart_info.item_details[].item_description` | `string` |  |
| `cart_info.item_details[].item_quantity` | `string` |  |
| `cart_info.item_details[].item_unit_price` | `object` |  |
| `cart_info.item_details[].item_unit_price.currency_code` | `string` |  |
| `cart_info.item_details[].item_unit_price.value` | `string` |  |
| `cart_info.item_details[].item_amount` | `object` |  |
| `cart_info.item_details[].item_amount.currency_code` | `string` |  |
| `cart_info.item_details[].item_amount.value` | `string` |  |
| `cart_info.item_details[].total_item_amount` | `object` |  |
| `cart_info.item_details[].total_item_amount.currency_code` | `string` |  |
| `cart_info.item_details[].total_item_amount.value` | `string` |  |
| `cart_info.item_details[].tax_amounts` | `array<object>` |  |
| `cart_info.item_details[].invoice_number` | `string` |  |
| `cart_info.tax_inclusive` | `boolean` |  |
| `cart_info.paypal_invoice_id` | `string` |  |
| `auction_info` | `object` |  |
| `auction_info.auction_site` | `string` |  |
| `auction_info.auction_item_site` | `string` |  |
| `auction_info.auction_buyer_id` | `string` |  |
| `auction_info.auction_closing_date` | `string` |  |
| `incentive_info` | `object` |  |
| `incentive_info.incentive_details` | `array<object>` |  |
| `incentive_info.incentive_details[].incentive_type` | `string` |  |
| `incentive_info.incentive_details[].incentive_code` | `string` |  |
| `incentive_info.incentive_details[].incentive_amount` | `object` |  |
| `incentive_info.incentive_details[].incentive_amount.currency_code` | `string` |  |
| `incentive_info.incentive_details[].incentive_amount.value` | `string` |  |
| `incentive_info.incentive_details[].incentive_program_code` | `string` |  |
| `store_info` | `object` |  |
| `store_info.store_id` | `string` |  |
| `store_info.terminal_id` | `string` |  |
| `transaction_id` | `string` |  |
| `transaction_updated_date` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |
| `total_pages` | `integer` |  |
| `page` | `integer` |  |

</details>

### Transactions Search

Search and filter transactions records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await paypal_transaction.transactions.search(
    query={"filter": {"eq": {"auction_info": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "transactions",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"auction_info": {}}}}
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
| `auction_info` | `object` | Information related to an auction |
| `cart_info` | `object` | Details of items in the cart |
| `incentive_info` | `object` | Details of any incentives applied |
| `payer_info` | `object` | Information about the payer |
| `shipping_info` | `object` | Shipping information |
| `store_info` | `object` | Information about the store |
| `transaction_id` | `string` | Unique ID of the transaction |
| `transaction_info` | `object` | Detailed information about the transaction |
| `transaction_initiation_date` | `string` | Date and time when the transaction was initiated |
| `transaction_updated_date` | `string` | Date and time when the transaction was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].auction_info` | `object` | Information related to an auction |
| `data[].cart_info` | `object` | Details of items in the cart |
| `data[].incentive_info` | `object` | Details of any incentives applied |
| `data[].payer_info` | `object` | Information about the payer |
| `data[].shipping_info` | `object` | Shipping information |
| `data[].store_info` | `object` | Information about the store |
| `data[].transaction_id` | `string` | Unique ID of the transaction |
| `data[].transaction_info` | `object` | Detailed information about the transaction |
| `data[].transaction_initiation_date` | `string` | Date and time when the transaction was initiated |
| `data[].transaction_updated_date` | `string` | Date and time when the transaction was last updated |

</details>

## List Payments

### List Payments List

Lists payments for the PayPal account. Supports filtering by start and end times.


#### Python SDK

```python
await paypal_transaction.list_payments.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "list_payments",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `start_time` | `string` | No | Start time in ISO 8601 format. |
| `end_time` | `string` | No | End time in ISO 8601 format. |
| `count` | `integer` | No | Number of items per page (max 20). |
| `start_id` | `string` | No | Starting resource ID for pagination. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `intent` | `string` |  |
| `state` | `string` |  |
| `cart` | `string` |  |
| `payer` | `object` |  |
| `transactions` | `array<object>` |  |
| `create_time` | `string` |  |
| `update_time` | `string` |  |
| `links` | `array<object>` |  |


</details>

### List Payments Search

Search and filter list payments records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await paypal_transaction.list_payments.search(
    query={"filter": {"eq": {"cart": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "list_payments",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"cart": "<str>"}}}
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
| `cart` | `string` | Details of the cart associated with the payment. |
| `create_time` | `string` | The date and time when the payment was created. |
| `id` | `string` | Unique identifier for the payment. |
| `intent` | `string` | The intention or purpose behind the payment. |
| `links` | `array` | Collection of links related to the payment |
| `payer` | `object` | Details of the payer who made the payment |
| `state` | `string` | The state of the payment. |
| `transactions` | `array` | List of transactions associated with the payment |
| `update_time` | `string` | The date and time when the payment was last updated. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].cart` | `string` | Details of the cart associated with the payment. |
| `data[].create_time` | `string` | The date and time when the payment was created. |
| `data[].id` | `string` | Unique identifier for the payment. |
| `data[].intent` | `string` | The intention or purpose behind the payment. |
| `data[].links` | `array` | Collection of links related to the payment |
| `data[].payer` | `object` | Details of the payer who made the payment |
| `data[].state` | `string` | The state of the payment. |
| `data[].transactions` | `array` | List of transactions associated with the payment |
| `data[].update_time` | `string` | The date and time when the payment was last updated. |

</details>

## List Disputes

### List Disputes List

Lists disputes for the PayPal account. Supports filtering by update time range.


#### Python SDK

```python
await paypal_transaction.list_disputes.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "list_disputes",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `update_time_after` | `string` | No | Filter disputes updated after this time in ISO 8601 format. |
| `update_time_before` | `string` | No | Filter disputes updated before this time in ISO 8601 format. |
| `page_size` | `integer` | No | Number of items per page (max 50). |
| `next_page_token` | `string` | No | Token for retrieving the next page of results. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `dispute_id` | `string` |  |
| `create_time` | `string` |  |
| `update_time` | `string` |  |
| `status` | `string` |  |
| `reason` | `string` |  |
| `dispute_state` | `string` |  |
| `dispute_life_cycle_stage` | `string` |  |
| `dispute_channel` | `string` |  |
| `dispute_amount` | `object` |  |
| `dispute_amount.currency_code` | `string` |  |
| `dispute_amount.value` | `string` |  |
| `outcome` | `string` |  |
| `disputed_transactions` | `array<object>` |  |
| `links` | `array<object>` |  |


</details>

### List Disputes Search

Search and filter list disputes records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await paypal_transaction.list_disputes.search(
    query={"filter": {"eq": {"create_time": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "list_disputes",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"create_time": "<str>"}}}
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
| `create_time` | `string` | The timestamp when the dispute was created. |
| `dispute_amount` | `object` | Details about the disputed amount. |
| `dispute_channel` | `string` | The channel through which the dispute was initiated. |
| `dispute_id` | `string` | The unique identifier for the dispute. |
| `dispute_life_cycle_stage` | `string` | The stage in the life cycle of the dispute. |
| `dispute_state` | `string` | The current state of the dispute. |
| `disputed_transactions` | `array` | Details of transactions involved in the dispute. |
| `links` | `array` | Links related to the dispute. |
| `outcome` | `string` | The outcome of the dispute resolution. |
| `reason` | `string` | The reason for the dispute. |
| `status` | `string` | The current status of the dispute. |
| `update_time` | `string` | The timestamp when the dispute was last updated. |
| `updated_time_cut` | `string` | The cut-off timestamp for the last update. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].create_time` | `string` | The timestamp when the dispute was created. |
| `data[].dispute_amount` | `object` | Details about the disputed amount. |
| `data[].dispute_channel` | `string` | The channel through which the dispute was initiated. |
| `data[].dispute_id` | `string` | The unique identifier for the dispute. |
| `data[].dispute_life_cycle_stage` | `string` | The stage in the life cycle of the dispute. |
| `data[].dispute_state` | `string` | The current state of the dispute. |
| `data[].disputed_transactions` | `array` | Details of transactions involved in the dispute. |
| `data[].links` | `array` | Links related to the dispute. |
| `data[].outcome` | `string` | The outcome of the dispute resolution. |
| `data[].reason` | `string` | The reason for the dispute. |
| `data[].status` | `string` | The current status of the dispute. |
| `data[].update_time` | `string` | The timestamp when the dispute was last updated. |
| `data[].updated_time_cut` | `string` | The cut-off timestamp for the last update. |

</details>

## List Products

### List Products List

Lists all catalog products for the PayPal account.

#### Python SDK

```python
await paypal_transaction.list_products.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "list_products",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page_size` | `integer` | No | Number of items per page (max 20). |
| `page` | `integer` | No | Page number starting from 1. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `description` | `string` |  |
| `create_time` | `string` |  |
| `links` | `array<object>` |  |


</details>

### List Products Search

Search and filter list products records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await paypal_transaction.list_products.search(
    query={"filter": {"eq": {"create_time": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "list_products",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"create_time": "<str>"}}}
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
| `create_time` | `string` | The time when the product was created |
| `description` | `string` | Detailed information or features of the product |
| `id` | `string` | Unique identifier for the product |
| `links` | `array` | List of links related to the fetched products. |
| `name` | `string` | The name or title of the product |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].create_time` | `string` | The time when the product was created |
| `data[].description` | `string` | Detailed information or features of the product |
| `data[].id` | `string` | Unique identifier for the product |
| `data[].links` | `array` | List of links related to the fetched products. |
| `data[].name` | `string` | The name or title of the product |

</details>

## Show Product Details

### Show Product Details Get

Shows details for a catalog product by ID.

#### Python SDK

```python
await paypal_transaction.show_product_details.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "show_product_details",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Product ID. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `description` | `string` |  |
| `type` | `string` |  |
| `category` | `string` |  |
| `image_url` | `string` |  |
| `home_url` | `string` |  |
| `create_time` | `string` |  |
| `update_time` | `string` |  |
| `links` | `array<object>` |  |


</details>

### Show Product Details Search

Search and filter show product details records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await paypal_transaction.show_product_details.search(
    query={"filter": {"eq": {"category": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "show_product_details",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"category": "<str>"}}}
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
| `category` | `string` | The category to which the product belongs |
| `create_time` | `string` | The date and time when the product was created |
| `description` | `string` | The detailed description of the product |
| `home_url` | `string` | The URL for the home page of the product |
| `id` | `string` | The unique identifier for the product |
| `image_url` | `string` | The URL to the image representing the product |
| `links` | `array` | Contains links related to the product details. |
| `name` | `string` | The name of the product |
| `type` | `string` | The type or category of the product |
| `update_time` | `string` | The date and time when the product was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].category` | `string` | The category to which the product belongs |
| `data[].create_time` | `string` | The date and time when the product was created |
| `data[].description` | `string` | The detailed description of the product |
| `data[].home_url` | `string` | The URL for the home page of the product |
| `data[].id` | `string` | The unique identifier for the product |
| `data[].image_url` | `string` | The URL to the image representing the product |
| `data[].links` | `array` | Contains links related to the product details. |
| `data[].name` | `string` | The name of the product |
| `data[].type` | `string` | The type or category of the product |
| `data[].update_time` | `string` | The date and time when the product was last updated |

</details>

## Search Invoices

### Search Invoices List

Searches for invoices matching the specified criteria. Uses POST with a JSON body for filtering.


#### Python SDK

```python
await paypal_transaction.search_invoices.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "search_invoices",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `creation_date_range` | `object` | No | Filter by invoice creation date range. |
| `creation_date_range.start` | `string` | No | Start date in ISO 8601 format. |
| `creation_date_range.end` | `string` | No | End date in ISO 8601 format. |
| `page_size` | `integer` | No | Number of items per page (max 100). |
| `page` | `integer` | No | Page number starting from 1. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `status` | `string` |  |
| `detail` | `object` |  |
| `invoicer` | `object` |  |
| `primary_recipients` | `array<object>` |  |
| `additional_recipients` | `array<string>` |  |
| `items` | `array<object>` |  |
| `amount` | `object` |  |
| `configuration` | `object` |  |
| `due_amount` | `object` |  |
| `due_amount.currency_code` | `string` |  |
| `due_amount.value` | `string` |  |
| `payments` | `object` |  |
| `refunds` | `object` |  |
| `links` | `array<object>` |  |


</details>

### Search Invoices Search

Search and filter search invoices records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await paypal_transaction.search_invoices.search(
    query={"filter": {"eq": {"additional_recipients": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "search_invoices",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"additional_recipients": []}}}
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
| `additional_recipients` | `array` | List of additional recipients associated with the invoice |
| `amount` | `object` | Detailed breakdown of the invoice amount |
| `configuration` | `object` | Configuration settings related to the invoice |
| `detail` | `object` | Detailed information about the invoice |
| `due_amount` | `object` | Due amount remaining to be paid for the invoice |
| `gratuity` | `object` | Gratuity amount included in the invoice |
| `id` | `string` | Unique identifier of the invoice |
| `invoicer` | `object` | Information about the invoicer associated with the invoice |
| `last_update_time` | `string` | Date and time of the last update made to the invoice |
| `links` | `array` | Links associated with the invoice |
| `payments` | `object` | Payment transactions associated with the invoice |
| `primary_recipients` | `array` | Primary recipients associated with the invoice |
| `refunds` | `object` | Refund transactions associated with the invoice |
| `status` | `string` | Current status of the invoice |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].additional_recipients` | `array` | List of additional recipients associated with the invoice |
| `data[].amount` | `object` | Detailed breakdown of the invoice amount |
| `data[].configuration` | `object` | Configuration settings related to the invoice |
| `data[].detail` | `object` | Detailed information about the invoice |
| `data[].due_amount` | `object` | Due amount remaining to be paid for the invoice |
| `data[].gratuity` | `object` | Gratuity amount included in the invoice |
| `data[].id` | `string` | Unique identifier of the invoice |
| `data[].invoicer` | `object` | Information about the invoicer associated with the invoice |
| `data[].last_update_time` | `string` | Date and time of the last update made to the invoice |
| `data[].links` | `array` | Links associated with the invoice |
| `data[].payments` | `object` | Payment transactions associated with the invoice |
| `data[].primary_recipients` | `array` | Primary recipients associated with the invoice |
| `data[].refunds` | `object` | Refund transactions associated with the invoice |
| `data[].status` | `string` | Current status of the invoice |

</details>

