# Orb full reference

This is the full reference documentation for the Orb agent connector.

## Supported entities and actions

The Orb connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Customers | [List](#customers-list), [Get](#customers-get), [Search](#customers-search) |
| Subscriptions | [List](#subscriptions-list), [Get](#subscriptions-get), [Search](#subscriptions-search) |
| Plans | [List](#plans-list), [Get](#plans-get), [Search](#plans-search) |
| Invoices | [List](#invoices-list), [Get](#invoices-get), [Search](#invoices-search) |

## Customers

### Customers List

Returns a paginated list of customers

#### Python SDK

```python
await orb.customers.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "customers",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Number of items to return per page |
| `cursor` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `external_customer_id` | `string \| null` |  |
| `name` | `string \| null` |  |
| `email` | `string \| null` |  |
| `created_at` | `string \| null` |  |
| `payment_provider` | `string \| null` |  |
| `payment_provider_id` | `string \| null` |  |
| `timezone` | `string \| null` |  |
| `shipping_address` | `object \| any` |  |
| `billing_address` | `object \| any` |  |
| `balance` | `string \| null` |  |
| `currency` | `string \| null` |  |
| `tax_id` | `object \| null` |  |
| `auto_collection` | `boolean \| null` |  |
| `metadata` | `object \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |

</details>

### Customers Get

Get a single customer by ID

#### Python SDK

```python
await orb.customers.get(
    customer_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "customers",
    "action": "get",
    "params": {
        "customer_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `customer_id` | `string` | Yes | Customer ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `external_customer_id` | `string \| null` |  |
| `name` | `string \| null` |  |
| `email` | `string \| null` |  |
| `created_at` | `string \| null` |  |
| `payment_provider` | `string \| null` |  |
| `payment_provider_id` | `string \| null` |  |
| `timezone` | `string \| null` |  |
| `shipping_address` | `object \| any` |  |
| `billing_address` | `object \| any` |  |
| `balance` | `string \| null` |  |
| `currency` | `string \| null` |  |
| `tax_id` | `object \| null` |  |
| `auto_collection` | `boolean \| null` |  |
| `metadata` | `object \| null` |  |


</details>

### Customers Search

Search and filter customers records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await orb.customers.search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "customers",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | The unique identifier of the customer |
| `external_customer_id` | `string` | The ID of the customer in an external system |
| `name` | `string` | The name of the customer |
| `email` | `string` | The email address of the customer |
| `created_at` | `string` | The date and time when the customer was created |
| `payment_provider` | `string` | The payment provider used by the customer |
| `payment_provider_id` | `string` | The ID of the customer in the payment provider's system |
| `timezone` | `string` | The timezone setting of the customer |
| `shipping_address` | `object` | The shipping address of the customer |
| `billing_address` | `object` | The billing address of the customer |
| `balance` | `string` | The current balance of the customer |
| `currency` | `string` | The currency of the customer |
| `auto_collection` | `boolean` | Whether auto collection is enabled |
| `metadata` | `object` | Additional metadata for the customer |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.id` | `string` | The unique identifier of the customer |
| `hits[].data.external_customer_id` | `string` | The ID of the customer in an external system |
| `hits[].data.name` | `string` | The name of the customer |
| `hits[].data.email` | `string` | The email address of the customer |
| `hits[].data.created_at` | `string` | The date and time when the customer was created |
| `hits[].data.payment_provider` | `string` | The payment provider used by the customer |
| `hits[].data.payment_provider_id` | `string` | The ID of the customer in the payment provider's system |
| `hits[].data.timezone` | `string` | The timezone setting of the customer |
| `hits[].data.shipping_address` | `object` | The shipping address of the customer |
| `hits[].data.billing_address` | `object` | The billing address of the customer |
| `hits[].data.balance` | `string` | The current balance of the customer |
| `hits[].data.currency` | `string` | The currency of the customer |
| `hits[].data.auto_collection` | `boolean` | Whether auto collection is enabled |
| `hits[].data.metadata` | `object` | Additional metadata for the customer |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Subscriptions

### Subscriptions List

Returns a paginated list of subscriptions

#### Python SDK

```python
await orb.subscriptions.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "subscriptions",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Number of items to return per page |
| `cursor` | `string` | No | Cursor for pagination |
| `customer_id` | `string` | No | Filter subscriptions by customer ID |
| `external_customer_id` | `string` | No | Filter subscriptions by external customer ID |
| `status` | `"active" \| "ended" \| "upcoming"` | No | Filter subscriptions by status |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `created_at` | `string \| null` |  |
| `start_date` | `string \| null` |  |
| `end_date` | `string \| null` |  |
| `status` | `string \| null` |  |
| `customer` | `object \| null` |  |
| `plan` | `object \| null` |  |
| `current_billing_period_start_date` | `string \| null` |  |
| `current_billing_period_end_date` | `string \| null` |  |
| `active_plan_phase_order` | `integer \| null` |  |
| `fixed_fee_quantity_schedule` | `array \| null` |  |
| `price_intervals` | `array \| null` |  |
| `redeemed_coupon` | `object \| null` |  |
| `default_invoice_memo` | `string \| null` |  |
| `auto_collection` | `boolean \| null` |  |
| `net_terms` | `integer \| null` |  |
| `invoicing_threshold` | `string \| null` |  |
| `metadata` | `object \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |

</details>

### Subscriptions Get

Get a single subscription by ID

#### Python SDK

```python
await orb.subscriptions.get(
    subscription_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "subscriptions",
    "action": "get",
    "params": {
        "subscription_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `subscription_id` | `string` | Yes | Subscription ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `created_at` | `string \| null` |  |
| `start_date` | `string \| null` |  |
| `end_date` | `string \| null` |  |
| `status` | `string \| null` |  |
| `customer` | `object \| null` |  |
| `plan` | `object \| null` |  |
| `current_billing_period_start_date` | `string \| null` |  |
| `current_billing_period_end_date` | `string \| null` |  |
| `active_plan_phase_order` | `integer \| null` |  |
| `fixed_fee_quantity_schedule` | `array \| null` |  |
| `price_intervals` | `array \| null` |  |
| `redeemed_coupon` | `object \| null` |  |
| `default_invoice_memo` | `string \| null` |  |
| `auto_collection` | `boolean \| null` |  |
| `net_terms` | `integer \| null` |  |
| `invoicing_threshold` | `string \| null` |  |
| `metadata` | `object \| null` |  |


</details>

### Subscriptions Search

Search and filter subscriptions records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await orb.subscriptions.search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "subscriptions",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | The unique identifier of the subscription |
| `created_at` | `string` | The date and time when the subscription was created |
| `start_date` | `string` | The date and time when the subscription starts |
| `end_date` | `string` | The date and time when the subscription ends |
| `status` | `string` | The current status of the subscription |
| `customer` | `object` | The customer associated with the subscription |
| `plan` | `object` | The plan associated with the subscription |
| `current_billing_period_start_date` | `string` | The start date of the current billing period |
| `current_billing_period_end_date` | `string` | The end date of the current billing period |
| `auto_collection` | `boolean` | Whether auto collection is enabled |
| `net_terms` | `integer` | The net terms for the subscription |
| `metadata` | `object` | Additional metadata for the subscription |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.id` | `string` | The unique identifier of the subscription |
| `hits[].data.created_at` | `string` | The date and time when the subscription was created |
| `hits[].data.start_date` | `string` | The date and time when the subscription starts |
| `hits[].data.end_date` | `string` | The date and time when the subscription ends |
| `hits[].data.status` | `string` | The current status of the subscription |
| `hits[].data.customer` | `object` | The customer associated with the subscription |
| `hits[].data.plan` | `object` | The plan associated with the subscription |
| `hits[].data.current_billing_period_start_date` | `string` | The start date of the current billing period |
| `hits[].data.current_billing_period_end_date` | `string` | The end date of the current billing period |
| `hits[].data.auto_collection` | `boolean` | Whether auto collection is enabled |
| `hits[].data.net_terms` | `integer` | The net terms for the subscription |
| `hits[].data.metadata` | `object` | Additional metadata for the subscription |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Plans

### Plans List

Returns a paginated list of plans

#### Python SDK

```python
await orb.plans.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "plans",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Number of items to return per page |
| `cursor` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `created_at` | `string \| null` |  |
| `name` | `string \| null` |  |
| `description` | `string \| null` |  |
| `status` | `string \| null` |  |
| `default_invoice_memo` | `string \| null` |  |
| `net_terms` | `integer \| null` |  |
| `currency` | `string \| null` |  |
| `prices` | `array \| null` |  |
| `product` | `object \| null` |  |
| `minimum` | `object \| null` |  |
| `maximum` | `object \| null` |  |
| `discount` | `object \| null` |  |
| `trial_config` | `object \| null` |  |
| `plan_phases` | `array \| null` |  |
| `external_plan_id` | `string \| null` |  |
| `invoicing_currency` | `string \| null` |  |
| `metadata` | `object \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |

</details>

### Plans Get

Get a single plan by ID

#### Python SDK

```python
await orb.plans.get(
    plan_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "plans",
    "action": "get",
    "params": {
        "plan_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `plan_id` | `string` | Yes | Plan ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `created_at` | `string \| null` |  |
| `name` | `string \| null` |  |
| `description` | `string \| null` |  |
| `status` | `string \| null` |  |
| `default_invoice_memo` | `string \| null` |  |
| `net_terms` | `integer \| null` |  |
| `currency` | `string \| null` |  |
| `prices` | `array \| null` |  |
| `product` | `object \| null` |  |
| `minimum` | `object \| null` |  |
| `maximum` | `object \| null` |  |
| `discount` | `object \| null` |  |
| `trial_config` | `object \| null` |  |
| `plan_phases` | `array \| null` |  |
| `external_plan_id` | `string \| null` |  |
| `invoicing_currency` | `string \| null` |  |
| `metadata` | `object \| null` |  |


</details>

### Plans Search

Search and filter plans records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await orb.plans.search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "plans",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | The unique identifier of the plan |
| `created_at` | `string` | The date and time when the plan was created |
| `name` | `string` | The name of the plan |
| `description` | `string` | A description of the plan |
| `status` | `string` | The status of the plan |
| `currency` | `string` | The currency of the plan |
| `prices` | `array` | The pricing options for the plan |
| `product` | `object` | The product associated with the plan |
| `external_plan_id` | `string` | The external plan ID |
| `metadata` | `object` | Additional metadata for the plan |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.id` | `string` | The unique identifier of the plan |
| `hits[].data.created_at` | `string` | The date and time when the plan was created |
| `hits[].data.name` | `string` | The name of the plan |
| `hits[].data.description` | `string` | A description of the plan |
| `hits[].data.status` | `string` | The status of the plan |
| `hits[].data.currency` | `string` | The currency of the plan |
| `hits[].data.prices` | `array` | The pricing options for the plan |
| `hits[].data.product` | `object` | The product associated with the plan |
| `hits[].data.external_plan_id` | `string` | The external plan ID |
| `hits[].data.metadata` | `object` | Additional metadata for the plan |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Invoices

### Invoices List

Returns a paginated list of invoices

#### Python SDK

```python
await orb.invoices.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "invoices",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Number of items to return per page |
| `cursor` | `string` | No | Cursor for pagination |
| `customer_id` | `string` | No | Filter invoices by customer ID |
| `external_customer_id` | `string` | No | Filter invoices by external customer ID |
| `subscription_id` | `string` | No | Filter invoices by subscription ID |
| `invoice_date_gt` | `string` | No | Filter invoices with invoice date greater than this value (ISO 8601 format) |
| `invoice_date_gte` | `string` | No | Filter invoices with invoice date greater than or equal to this value (ISO 8601 format) |
| `invoice_date_lt` | `string` | No | Filter invoices with invoice date less than this value (ISO 8601 format) |
| `invoice_date_lte` | `string` | No | Filter invoices with invoice date less than or equal to this value (ISO 8601 format) |
| `status` | `"draft" \| "issued" \| "paid" \| "synced" \| "void"` | No | Filter invoices by status |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `created_at` | `string \| null` |  |
| `invoice_date` | `string \| null` |  |
| `due_date` | `string \| null` |  |
| `invoice_pdf` | `string \| null` |  |
| `subtotal` | `string \| null` |  |
| `total` | `string \| null` |  |
| `amount_due` | `string \| null` |  |
| `status` | `string \| null` |  |
| `memo` | `string \| null` |  |
| `issue_failed_at` | `string \| null` |  |
| `sync_failed_at` | `string \| null` |  |
| `payment_failed_at` | `string \| null` |  |
| `payment_started_at` | `string \| null` |  |
| `voided_at` | `string \| null` |  |
| `paid_at` | `string \| null` |  |
| `issued_at` | `string \| null` |  |
| `hosted_invoice_url` | `string \| null` |  |
| `line_items` | `array \| null` |  |
| `subscription` | `object \| null` |  |
| `customer` | `object \| null` |  |
| `currency` | `string \| null` |  |
| `discount` | `object \| null` |  |
| `minimum` | `object \| null` |  |
| `maximum` | `object \| null` |  |
| `credit_notes` | `array \| null` |  |
| `will_auto_issue` | `boolean \| null` |  |
| `eligible_to_issue_at` | `string \| null` |  |
| `customer_balance_transactions` | `array \| null` |  |
| `auto_collection` | `object \| null` |  |
| `invoice_number` | `string \| null` |  |
| `billing_address` | `object \| any` |  |
| `shipping_address` | `object \| any` |  |
| `metadata` | `object \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |

</details>

### Invoices Get

Get a single invoice by ID

#### Python SDK

```python
await orb.invoices.get(
    invoice_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "invoices",
    "action": "get",
    "params": {
        "invoice_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `invoice_id` | `string` | Yes | Invoice ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `created_at` | `string \| null` |  |
| `invoice_date` | `string \| null` |  |
| `due_date` | `string \| null` |  |
| `invoice_pdf` | `string \| null` |  |
| `subtotal` | `string \| null` |  |
| `total` | `string \| null` |  |
| `amount_due` | `string \| null` |  |
| `status` | `string \| null` |  |
| `memo` | `string \| null` |  |
| `issue_failed_at` | `string \| null` |  |
| `sync_failed_at` | `string \| null` |  |
| `payment_failed_at` | `string \| null` |  |
| `payment_started_at` | `string \| null` |  |
| `voided_at` | `string \| null` |  |
| `paid_at` | `string \| null` |  |
| `issued_at` | `string \| null` |  |
| `hosted_invoice_url` | `string \| null` |  |
| `line_items` | `array \| null` |  |
| `subscription` | `object \| null` |  |
| `customer` | `object \| null` |  |
| `currency` | `string \| null` |  |
| `discount` | `object \| null` |  |
| `minimum` | `object \| null` |  |
| `maximum` | `object \| null` |  |
| `credit_notes` | `array \| null` |  |
| `will_auto_issue` | `boolean \| null` |  |
| `eligible_to_issue_at` | `string \| null` |  |
| `customer_balance_transactions` | `array \| null` |  |
| `auto_collection` | `object \| null` |  |
| `invoice_number` | `string \| null` |  |
| `billing_address` | `object \| any` |  |
| `shipping_address` | `object \| any` |  |
| `metadata` | `object \| null` |  |


</details>

### Invoices Search

Search and filter invoices records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await orb.invoices.search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "invoices",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | The unique identifier of the invoice |
| `created_at` | `string` | The date and time when the invoice was created |
| `invoice_date` | `string` | The date of the invoice |
| `due_date` | `string` | The due date for the invoice |
| `invoice_pdf` | `string` | The URL to download the PDF version of the invoice |
| `subtotal` | `string` | The subtotal amount of the invoice |
| `total` | `string` | The total amount of the invoice |
| `amount_due` | `string` | The amount due on the invoice |
| `status` | `string` | The current status of the invoice |
| `memo` | `string` | Any additional notes or comments on the invoice |
| `paid_at` | `string` | The date and time when the invoice was paid |
| `issued_at` | `string` | The date and time when the invoice was issued |
| `hosted_invoice_url` | `string` | The URL to view the hosted invoice |
| `line_items` | `array` | The line items on the invoice |
| `subscription` | `object` | The subscription associated with the invoice |
| `customer` | `object` | The customer associated with the invoice |
| `currency` | `string` | The currency of the invoice |
| `invoice_number` | `string` | The invoice number |
| `metadata` | `object` | Additional metadata for the invoice |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.id` | `string` | The unique identifier of the invoice |
| `hits[].data.created_at` | `string` | The date and time when the invoice was created |
| `hits[].data.invoice_date` | `string` | The date of the invoice |
| `hits[].data.due_date` | `string` | The due date for the invoice |
| `hits[].data.invoice_pdf` | `string` | The URL to download the PDF version of the invoice |
| `hits[].data.subtotal` | `string` | The subtotal amount of the invoice |
| `hits[].data.total` | `string` | The total amount of the invoice |
| `hits[].data.amount_due` | `string` | The amount due on the invoice |
| `hits[].data.status` | `string` | The current status of the invoice |
| `hits[].data.memo` | `string` | Any additional notes or comments on the invoice |
| `hits[].data.paid_at` | `string` | The date and time when the invoice was paid |
| `hits[].data.issued_at` | `string` | The date and time when the invoice was issued |
| `hits[].data.hosted_invoice_url` | `string` | The URL to view the hosted invoice |
| `hits[].data.line_items` | `array` | The line items on the invoice |
| `hits[].data.subscription` | `object` | The subscription associated with the invoice |
| `hits[].data.customer` | `object` | The customer associated with the invoice |
| `hits[].data.currency` | `string` | The currency of the invoice |
| `hits[].data.invoice_number` | `string` | The invoice number |
| `hits[].data.metadata` | `object` | Additional metadata for the invoice |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

