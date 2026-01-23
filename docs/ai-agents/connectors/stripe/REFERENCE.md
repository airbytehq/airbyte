# Stripe full reference

This is the full reference documentation for the Stripe agent connector.

## Supported entities and actions

The Stripe connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Customers | [List](#customers-list), [Create](#customers-create), [Get](#customers-get), [Update](#customers-update), [Delete](#customers-delete), [API Search](#customers-api-search), [Search](#customers-search) |
| Invoices | [List](#invoices-list), [Get](#invoices-get), [API Search](#invoices-api-search), [Search](#invoices-search) |
| Charges | [List](#charges-list), [Get](#charges-get), [API Search](#charges-api-search), [Search](#charges-search) |
| Subscriptions | [List](#subscriptions-list), [Get](#subscriptions-get), [API Search](#subscriptions-api-search), [Search](#subscriptions-search) |
| Refunds | [List](#refunds-list), [Create](#refunds-create), [Get](#refunds-get), [Search](#refunds-search) |
| Products | [List](#products-list), [Create](#products-create), [Get](#products-get), [Update](#products-update), [Delete](#products-delete), [API Search](#products-api-search) |
| Balance | [Get](#balance-get) |
| Balance Transactions | [List](#balance-transactions-list), [Get](#balance-transactions-get) |
| Payment Intents | [List](#payment-intents-list), [Get](#payment-intents-get), [API Search](#payment-intents-api-search) |
| Disputes | [List](#disputes-list), [Get](#disputes-get) |
| Payouts | [List](#payouts-list), [Get](#payouts-get) |

## Customers

### Customers List

Returns a list of your customers. The customers are returned sorted by creation date, with the most recent customers appearing first.

#### Python SDK

```python
await stripe.customers.list()
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
| `limit` | `integer` | No | A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10. |
| `starting_after` | `string` | No | A cursor for use in pagination. starting_after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include starting_after=obj_foo in order to fetch the next page of the list. |
| `ending_before` | `string` | No | A cursor for use in pagination. ending_before is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj_bar, your subsequent call can include ending_before=obj_bar in order to fetch the previous page of the list. |
| `email` | `string` | No | A case-sensitive filter on the list based on the customer's email field. The value must be a string. |
| `created` | `object` | No | Only return customers that were created during the given date interval. |
| `created.gt` | `integer` | No | Minimum value to filter by (exclusive) |
| `created.gte` | `integer` | No | Minimum value to filter by (inclusive) |
| `created.lt` | `integer` | No | Maximum value to filter by (exclusive) |
| `created.lte` | `integer` | No | Maximum value to filter by (inclusive) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"customer"` |  |
| `address` | `object \| null` |  |
| `balance` | `integer` |  |
| `business_name` | `string \| null` |  |
| `cash_balance` | `object \| null` |  |
| `created` | `integer` |  |
| `currency` | `string \| null` |  |
| `customer_account` | `string \| null` |  |
| `default_currency` | `string \| null` |  |
| `default_source` | `string \| null` |  |
| `delinquent` | `boolean \| null` |  |
| `description` | `string \| null` |  |
| `discount` | `object \| null` |  |
| `email` | `string \| null` |  |
| `individual_name` | `string \| null` |  |
| `invoice_credit_balance` | `object` |  |
| `invoice_prefix` | `string \| null` |  |
| `invoice_settings` | `object` |  |
| `livemode` | `boolean` |  |
| `metadata` | `object` |  |
| `name` | `string \| null` |  |
| `next_invoice_sequence` | `integer \| null` |  |
| `phone` | `string \| null` |  |
| `preferred_locales` | `array \| null` |  |
| `shipping` | `object \| null` |  |
| `sources` | `object \| null` |  |
| `subscriptions` | `object \| null` |  |
| `tax_exempt` | `string \| null` |  |
| `test_clock` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

### Customers Create

Creates a new customer object.

#### Python SDK

```python
await stripe.customers.create()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "customers",
    "action": "create"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"customer"` |  |
| `address` | `object \| null` |  |
| `balance` | `integer` |  |
| `business_name` | `string \| null` |  |
| `cash_balance` | `object \| null` |  |
| `created` | `integer` |  |
| `currency` | `string \| null` |  |
| `customer_account` | `string \| null` |  |
| `default_currency` | `string \| null` |  |
| `default_source` | `string \| null` |  |
| `delinquent` | `boolean \| null` |  |
| `description` | `string \| null` |  |
| `discount` | `object \| null` |  |
| `email` | `string \| null` |  |
| `individual_name` | `string \| null` |  |
| `invoice_credit_balance` | `object` |  |
| `invoice_prefix` | `string \| null` |  |
| `invoice_settings` | `object` |  |
| `livemode` | `boolean` |  |
| `metadata` | `object` |  |
| `name` | `string \| null` |  |
| `next_invoice_sequence` | `integer \| null` |  |
| `phone` | `string \| null` |  |
| `preferred_locales` | `array \| null` |  |
| `shipping` | `object \| null` |  |
| `sources` | `object \| null` |  |
| `subscriptions` | `object \| null` |  |
| `tax_exempt` | `string \| null` |  |
| `test_clock` | `string \| null` |  |


</details>

### Customers Get

Retrieves a Customer object.

#### Python SDK

```python
await stripe.customers.get(
    id="<str>"
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
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The customer ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"customer"` |  |
| `address` | `object \| null` |  |
| `balance` | `integer` |  |
| `business_name` | `string \| null` |  |
| `cash_balance` | `object \| null` |  |
| `created` | `integer` |  |
| `currency` | `string \| null` |  |
| `customer_account` | `string \| null` |  |
| `default_currency` | `string \| null` |  |
| `default_source` | `string \| null` |  |
| `delinquent` | `boolean \| null` |  |
| `description` | `string \| null` |  |
| `discount` | `object \| null` |  |
| `email` | `string \| null` |  |
| `individual_name` | `string \| null` |  |
| `invoice_credit_balance` | `object` |  |
| `invoice_prefix` | `string \| null` |  |
| `invoice_settings` | `object` |  |
| `livemode` | `boolean` |  |
| `metadata` | `object` |  |
| `name` | `string \| null` |  |
| `next_invoice_sequence` | `integer \| null` |  |
| `phone` | `string \| null` |  |
| `preferred_locales` | `array \| null` |  |
| `shipping` | `object \| null` |  |
| `sources` | `object \| null` |  |
| `subscriptions` | `object \| null` |  |
| `tax_exempt` | `string \| null` |  |
| `test_clock` | `string \| null` |  |


</details>

### Customers Update

Updates the specified customer by setting the values of the parameters passed.

#### Python SDK

```python
await stripe.customers.update(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "customers",
    "action": "update",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The customer ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"customer"` |  |
| `address` | `object \| null` |  |
| `balance` | `integer` |  |
| `business_name` | `string \| null` |  |
| `cash_balance` | `object \| null` |  |
| `created` | `integer` |  |
| `currency` | `string \| null` |  |
| `customer_account` | `string \| null` |  |
| `default_currency` | `string \| null` |  |
| `default_source` | `string \| null` |  |
| `delinquent` | `boolean \| null` |  |
| `description` | `string \| null` |  |
| `discount` | `object \| null` |  |
| `email` | `string \| null` |  |
| `individual_name` | `string \| null` |  |
| `invoice_credit_balance` | `object` |  |
| `invoice_prefix` | `string \| null` |  |
| `invoice_settings` | `object` |  |
| `livemode` | `boolean` |  |
| `metadata` | `object` |  |
| `name` | `string \| null` |  |
| `next_invoice_sequence` | `integer \| null` |  |
| `phone` | `string \| null` |  |
| `preferred_locales` | `array \| null` |  |
| `shipping` | `object \| null` |  |
| `sources` | `object \| null` |  |
| `subscriptions` | `object \| null` |  |
| `tax_exempt` | `string \| null` |  |
| `test_clock` | `string \| null` |  |


</details>

### Customers Delete

Permanently deletes a customer. It cannot be undone.

#### Python SDK

```python
await stripe.customers.delete(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "customers",
    "action": "delete",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The customer ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"customer"` |  |
| `deleted` | `boolean` |  |


</details>

### Customers API Search

Search for customers using Stripe's Search Query Language.

#### Python SDK

```python
await stripe.customers.api_search(
    query="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "customers",
    "action": "api_search",
    "params": {
        "query": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | Yes | The search query string using Stripe's Search Query Language |
| `limit` | `integer` | No | A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10. |
| `page` | `string` | No | A cursor for pagination across multiple pages of results. Don’t include this parameter on the first call. Use the next_page value returned in a previous response to request subsequent results. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"customer"` |  |
| `address` | `object \| null` |  |
| `balance` | `integer` |  |
| `business_name` | `string \| null` |  |
| `cash_balance` | `object \| null` |  |
| `created` | `integer` |  |
| `currency` | `string \| null` |  |
| `customer_account` | `string \| null` |  |
| `default_currency` | `string \| null` |  |
| `default_source` | `string \| null` |  |
| `delinquent` | `boolean \| null` |  |
| `description` | `string \| null` |  |
| `discount` | `object \| null` |  |
| `email` | `string \| null` |  |
| `individual_name` | `string \| null` |  |
| `invoice_credit_balance` | `object` |  |
| `invoice_prefix` | `string \| null` |  |
| `invoice_settings` | `object` |  |
| `livemode` | `boolean` |  |
| `metadata` | `object` |  |
| `name` | `string \| null` |  |
| `next_invoice_sequence` | `integer \| null` |  |
| `phone` | `string \| null` |  |
| `preferred_locales` | `array \| null` |  |
| `shipping` | `object \| null` |  |
| `sources` | `object \| null` |  |
| `subscriptions` | `object \| null` |  |
| `tax_exempt` | `string \| null` |  |
| `test_clock` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

### Customers Search

Search and filter customers records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await stripe.customers.search(
    query={"filter": {"eq": {"account_balance": 0}}}
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
        "query": {"filter": {"eq": {"account_balance": 0}}}
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
| `account_balance` | `integer` | Current balance value representing funds owed by or to the customer. |
| `address` | `object` | The customer's address information including line1, line2, city, state, postal code, and country. |
| `balance` | `integer` | Current balance (positive or negative) that is automatically applied to the customer's next invoice. |
| `cards` | `array` | Card payment methods associated with the customer account. |
| `created` | `integer` | Timestamp indicating when the customer object was created. |
| `currency` | `string` | Three-letter ISO currency code representing the customer's default currency. |
| `default_card` | `string` | The default card to be used for charges when no specific payment method is provided. |
| `default_source` | `string` | The default payment source (card or bank account) for the customer. |
| `delinquent` | `boolean` | Boolean indicating whether the customer is currently delinquent on payments. |
| `description` | `string` | An arbitrary string attached to the customer, often useful for displaying to users. |
| `discount` | `object` | Discount object describing any active discount applied to the customer. |
| `email` | `string` | The customer's email address for communication and tracking purposes. |
| `id` | `string` | Unique identifier for the customer object. |
| `invoice_prefix` | `string` | The prefix for invoice numbers generated for this customer. |
| `invoice_settings` | `object` | Customer's invoice-related settings including default payment method and custom fields. |
| `is_deleted` | `boolean` | Boolean indicating whether the customer has been deleted. |
| `livemode` | `boolean` | Boolean indicating whether the object exists in live mode or test mode. |
| `metadata` | `object` | Set of key-value pairs for storing additional structured information about the customer. |
| `name` | `string` | The customer's full name or business name. |
| `next_invoice_sequence` | `integer` | The sequence number for the next invoice generated for this customer. |
| `object` | `string` | String representing the object type, always 'customer'. |
| `phone` | `string` | The customer's phone number. |
| `preferred_locales` | `array` | Array of preferred locales for the customer, used for invoice and receipt localization. |
| `shipping` | `object` | Mailing and shipping address for the customer, appears on invoices emailed to the customer. |
| `sources` | `string` | Payment sources (cards, bank accounts) attached to the customer for making payments. |
| `subscriptions` | `object` | List of active subscriptions associated with the customer. |
| `tax_exempt` | `string` | Describes the customer's tax exemption status (none, exempt, or reverse). |
| `tax_info` | `string` | Tax identification information for the customer. |
| `tax_info_verification` | `string` | Verification status of the customer's tax information. |
| `test_clock` | `string` | ID of the test clock associated with this customer for testing time-dependent scenarios. |
| `updated` | `integer` | Timestamp indicating when the customer object was last updated. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.account_balance` | `integer` | Current balance value representing funds owed by or to the customer. |
| `hits[].data.address` | `object` | The customer's address information including line1, line2, city, state, postal code, and country. |
| `hits[].data.balance` | `integer` | Current balance (positive or negative) that is automatically applied to the customer's next invoice. |
| `hits[].data.cards` | `array` | Card payment methods associated with the customer account. |
| `hits[].data.created` | `integer` | Timestamp indicating when the customer object was created. |
| `hits[].data.currency` | `string` | Three-letter ISO currency code representing the customer's default currency. |
| `hits[].data.default_card` | `string` | The default card to be used for charges when no specific payment method is provided. |
| `hits[].data.default_source` | `string` | The default payment source (card or bank account) for the customer. |
| `hits[].data.delinquent` | `boolean` | Boolean indicating whether the customer is currently delinquent on payments. |
| `hits[].data.description` | `string` | An arbitrary string attached to the customer, often useful for displaying to users. |
| `hits[].data.discount` | `object` | Discount object describing any active discount applied to the customer. |
| `hits[].data.email` | `string` | The customer's email address for communication and tracking purposes. |
| `hits[].data.id` | `string` | Unique identifier for the customer object. |
| `hits[].data.invoice_prefix` | `string` | The prefix for invoice numbers generated for this customer. |
| `hits[].data.invoice_settings` | `object` | Customer's invoice-related settings including default payment method and custom fields. |
| `hits[].data.is_deleted` | `boolean` | Boolean indicating whether the customer has been deleted. |
| `hits[].data.livemode` | `boolean` | Boolean indicating whether the object exists in live mode or test mode. |
| `hits[].data.metadata` | `object` | Set of key-value pairs for storing additional structured information about the customer. |
| `hits[].data.name` | `string` | The customer's full name or business name. |
| `hits[].data.next_invoice_sequence` | `integer` | The sequence number for the next invoice generated for this customer. |
| `hits[].data.object` | `string` | String representing the object type, always 'customer'. |
| `hits[].data.phone` | `string` | The customer's phone number. |
| `hits[].data.preferred_locales` | `array` | Array of preferred locales for the customer, used for invoice and receipt localization. |
| `hits[].data.shipping` | `object` | Mailing and shipping address for the customer, appears on invoices emailed to the customer. |
| `hits[].data.sources` | `string` | Payment sources (cards, bank accounts) attached to the customer for making payments. |
| `hits[].data.subscriptions` | `object` | List of active subscriptions associated with the customer. |
| `hits[].data.tax_exempt` | `string` | Describes the customer's tax exemption status (none, exempt, or reverse). |
| `hits[].data.tax_info` | `string` | Tax identification information for the customer. |
| `hits[].data.tax_info_verification` | `string` | Verification status of the customer's tax information. |
| `hits[].data.test_clock` | `string` | ID of the test clock associated with this customer for testing time-dependent scenarios. |
| `hits[].data.updated` | `integer` | Timestamp indicating when the customer object was last updated. |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Invoices

### Invoices List

Returns a list of invoices

#### Python SDK

```python
await stripe.invoices.list()
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
| `collection_method` | `"charge_automatically" \| "send_invoice"` | No | The collection method of the invoices to retrieve |
| `created` | `object` | No | Only return customers that were created during the given date interval. |
| `created.gt` | `integer` | No | Minimum value to filter by (exclusive) |
| `created.gte` | `integer` | No | Minimum value to filter by (inclusive) |
| `created.lt` | `integer` | No | Maximum value to filter by (exclusive) |
| `created.lte` | `integer` | No | Maximum value to filter by (inclusive) |
| `customer` | `string` | No | Only return invoices for the customer specified by this customer ID. |
| `customer_account` | `string` | No | Only return invoices for the account specified by this account ID |
| `ending_before` | `string` | No | A cursor for use in pagination. ending_before is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj_bar, your subsequent call can include ending_before=obj_bar in order to fetch the previous page of the list. |
| `limit` | `integer` | No | A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10. |
| `starting_after` | `string` | No | A cursor for use in pagination. starting_after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include starting_after=obj_foo in order to fetch the next page of the list. |
| `status` | `"draft" \| "open" \| "paid" \| "uncollectible" \| "void"` | No | The status of the invoices to retrieve |
| `subscription` | `string` | No | Only return invoices for the subscription specified by this subscription ID. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"invoice"` |  |
| `account_country` | `string \| null` |  |
| `account_name` | `string \| null` |  |
| `account_tax_ids` | `array \| null` |  |
| `amount_due` | `integer` |  |
| `amount_overpaid` | `integer` |  |
| `amount_paid` | `integer` |  |
| `amount_remaining` | `integer` |  |
| `amount_shipping` | `integer` |  |
| `application` | `string \| null` |  |
| `application_fee_amount` | `integer \| null` |  |
| `attempt_count` | `integer` |  |
| `attempted` | `boolean` |  |
| `auto_advance` | `boolean` |  |
| `automatic_tax` | `object` |  |
| `automatically_finalizes_at` | `integer \| null` |  |
| `billing_reason` | `string \| null` |  |
| `charge` | `string \| null` |  |
| `collection_method` | `"charge_automatically" \| "send_invoice"` |  |
| `confirmation_secret` | `object \| null` |  |
| `created` | `integer` |  |
| `currency` | `string` |  |
| `custom_fields` | `array \| null` |  |
| `customer` | `string` |  |
| `customer_account` | `string \| null` |  |
| `customer_address` | `object \| null` |  |
| `customer_email` | `string \| null` |  |
| `customer_name` | `string \| null` |  |
| `customer_phone` | `string \| null` |  |
| `customer_shipping` | `object \| null` |  |
| `customer_tax_exempt` | `string \| null` |  |
| `customer_tax_ids` | `array \| null` |  |
| `default_payment_method` | `string \| null` |  |
| `default_source` | `string \| null` |  |
| `default_tax_rates` | `array<object>` |  |
| `description` | `string \| null` |  |
| `discount` | `object \| null` |  |
| `discounts` | `array<string>` |  |
| `due_date` | `integer \| null` |  |
| `effective_at` | `integer \| null` |  |
| `ending_balance` | `integer \| null` |  |
| `footer` | `string \| null` |  |
| `from_invoice` | `object \| null` |  |
| `hosted_invoice_url` | `string \| null` |  |
| `invoice_pdf` | `string \| null` |  |
| `issuer` | `object` |  |
| `last_finalization_error` | `object \| null` |  |
| `latest_revision` | `string \| null` |  |
| `lines` | `object` |  |
| `livemode` | `boolean` |  |
| `metadata` | `object` |  |
| `next_payment_attempt` | `integer \| null` |  |
| `number` | `string \| null` |  |
| `on_behalf_of` | `string \| null` |  |
| `paid` | `boolean \| null` |  |
| `paid_out_of_band` | `boolean \| null` |  |
| `parent` | `object \| null` |  |
| `payment_intent` | `string \| null` |  |
| `payment_settings` | `object` |  |
| `payments` | `object` |  |
| `period_end` | `integer` |  |
| `period_start` | `integer` |  |
| `post_payment_credit_notes_amount` | `integer` |  |
| `pre_payment_credit_notes_amount` | `integer` |  |
| `quote` | `string \| null` |  |
| `receipt_number` | `string \| null` |  |
| `rendering` | `object \| null` |  |
| `rendering_options` | `object \| null` |  |
| `shipping_cost` | `object \| null` |  |
| `shipping_details` | `object \| null` |  |
| `starting_balance` | `integer` |  |
| `statement_descriptor` | `string \| null` |  |
| `status` | `string \| null` |  |
| `status_transitions` | `object` |  |
| `subscription` | `string \| null` |  |
| `subscription_details` | `object \| null` |  |
| `subtotal` | `integer` |  |
| `subtotal_excluding_tax` | `integer \| null` |  |
| `tax` | `integer \| null` |  |
| `test_clock` | `string \| null` |  |
| `threshold_reason` | `object \| null` |  |
| `total` | `integer` |  |
| `total_discount_amounts` | `array \| null` |  |
| `total_excluding_tax` | `integer \| null` |  |
| `total_pretax_credit_amounts` | `array \| null` |  |
| `total_tax_amounts` | `array \| null` |  |
| `total_taxes` | `array \| null` |  |
| `transfer_data` | `object \| null` |  |
| `webhooks_delivered_at` | `integer \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

### Invoices Get

Retrieves the invoice with the given ID

#### Python SDK

```python
await stripe.invoices.get(
    id="<str>"
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
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The invoice ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"invoice"` |  |
| `account_country` | `string \| null` |  |
| `account_name` | `string \| null` |  |
| `account_tax_ids` | `array \| null` |  |
| `amount_due` | `integer` |  |
| `amount_overpaid` | `integer` |  |
| `amount_paid` | `integer` |  |
| `amount_remaining` | `integer` |  |
| `amount_shipping` | `integer` |  |
| `application` | `string \| null` |  |
| `application_fee_amount` | `integer \| null` |  |
| `attempt_count` | `integer` |  |
| `attempted` | `boolean` |  |
| `auto_advance` | `boolean` |  |
| `automatic_tax` | `object` |  |
| `automatically_finalizes_at` | `integer \| null` |  |
| `billing_reason` | `string \| null` |  |
| `charge` | `string \| null` |  |
| `collection_method` | `"charge_automatically" \| "send_invoice"` |  |
| `confirmation_secret` | `object \| null` |  |
| `created` | `integer` |  |
| `currency` | `string` |  |
| `custom_fields` | `array \| null` |  |
| `customer` | `string` |  |
| `customer_account` | `string \| null` |  |
| `customer_address` | `object \| null` |  |
| `customer_email` | `string \| null` |  |
| `customer_name` | `string \| null` |  |
| `customer_phone` | `string \| null` |  |
| `customer_shipping` | `object \| null` |  |
| `customer_tax_exempt` | `string \| null` |  |
| `customer_tax_ids` | `array \| null` |  |
| `default_payment_method` | `string \| null` |  |
| `default_source` | `string \| null` |  |
| `default_tax_rates` | `array<object>` |  |
| `description` | `string \| null` |  |
| `discount` | `object \| null` |  |
| `discounts` | `array<string>` |  |
| `due_date` | `integer \| null` |  |
| `effective_at` | `integer \| null` |  |
| `ending_balance` | `integer \| null` |  |
| `footer` | `string \| null` |  |
| `from_invoice` | `object \| null` |  |
| `hosted_invoice_url` | `string \| null` |  |
| `invoice_pdf` | `string \| null` |  |
| `issuer` | `object` |  |
| `last_finalization_error` | `object \| null` |  |
| `latest_revision` | `string \| null` |  |
| `lines` | `object` |  |
| `livemode` | `boolean` |  |
| `metadata` | `object` |  |
| `next_payment_attempt` | `integer \| null` |  |
| `number` | `string \| null` |  |
| `on_behalf_of` | `string \| null` |  |
| `paid` | `boolean \| null` |  |
| `paid_out_of_band` | `boolean \| null` |  |
| `parent` | `object \| null` |  |
| `payment_intent` | `string \| null` |  |
| `payment_settings` | `object` |  |
| `payments` | `object` |  |
| `period_end` | `integer` |  |
| `period_start` | `integer` |  |
| `post_payment_credit_notes_amount` | `integer` |  |
| `pre_payment_credit_notes_amount` | `integer` |  |
| `quote` | `string \| null` |  |
| `receipt_number` | `string \| null` |  |
| `rendering` | `object \| null` |  |
| `rendering_options` | `object \| null` |  |
| `shipping_cost` | `object \| null` |  |
| `shipping_details` | `object \| null` |  |
| `starting_balance` | `integer` |  |
| `statement_descriptor` | `string \| null` |  |
| `status` | `string \| null` |  |
| `status_transitions` | `object` |  |
| `subscription` | `string \| null` |  |
| `subscription_details` | `object \| null` |  |
| `subtotal` | `integer` |  |
| `subtotal_excluding_tax` | `integer \| null` |  |
| `tax` | `integer \| null` |  |
| `test_clock` | `string \| null` |  |
| `threshold_reason` | `object \| null` |  |
| `total` | `integer` |  |
| `total_discount_amounts` | `array \| null` |  |
| `total_excluding_tax` | `integer \| null` |  |
| `total_pretax_credit_amounts` | `array \| null` |  |
| `total_tax_amounts` | `array \| null` |  |
| `total_taxes` | `array \| null` |  |
| `transfer_data` | `object \| null` |  |
| `webhooks_delivered_at` | `integer \| null` |  |


</details>

### Invoices API Search

Search for invoices using Stripe's Search Query Language

#### Python SDK

```python
await stripe.invoices.api_search(
    query="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "invoices",
    "action": "api_search",
    "params": {
        "query": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | Yes | The search query string using Stripe's Search Query Language |
| `limit` | `integer` | No | A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10. |
| `page` | `string` | No | A cursor for pagination across multiple pages of results. Don’t include this parameter on the first call. Use the next_page value returned in a previous response to request subsequent results. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `object` | `"search_result"` |  |
| `data` | `array<object>` |  |
| `data[].id` | `string` |  |
| `data[].object` | `"invoice"` |  |
| `data[].account_country` | `string \| null` |  |
| `data[].account_name` | `string \| null` |  |
| `data[].account_tax_ids` | `array \| null` |  |
| `data[].amount_due` | `integer` |  |
| `data[].amount_overpaid` | `integer` |  |
| `data[].amount_paid` | `integer` |  |
| `data[].amount_remaining` | `integer` |  |
| `data[].amount_shipping` | `integer` |  |
| `data[].application` | `string \| null` |  |
| `data[].application_fee_amount` | `integer \| null` |  |
| `data[].attempt_count` | `integer` |  |
| `data[].attempted` | `boolean` |  |
| `data[].auto_advance` | `boolean` |  |
| `data[].automatic_tax` | `object` |  |
| `data[].automatically_finalizes_at` | `integer \| null` |  |
| `data[].billing_reason` | `string \| null` |  |
| `data[].charge` | `string \| null` |  |
| `data[].collection_method` | `"charge_automatically" \| "send_invoice"` |  |
| `data[].confirmation_secret` | `object \| null` |  |
| `data[].created` | `integer` |  |
| `data[].currency` | `string` |  |
| `data[].custom_fields` | `array \| null` |  |
| `data[].customer` | `string` |  |
| `data[].customer_account` | `string \| null` |  |
| `data[].customer_address` | `object \| null` |  |
| `data[].customer_email` | `string \| null` |  |
| `data[].customer_name` | `string \| null` |  |
| `data[].customer_phone` | `string \| null` |  |
| `data[].customer_shipping` | `object \| null` |  |
| `data[].customer_tax_exempt` | `string \| null` |  |
| `data[].customer_tax_ids` | `array \| null` |  |
| `data[].default_payment_method` | `string \| null` |  |
| `data[].default_source` | `string \| null` |  |
| `data[].default_tax_rates` | `array<object>` |  |
| `data[].description` | `string \| null` |  |
| `data[].discount` | `object \| null` |  |
| `data[].discounts` | `array<string>` |  |
| `data[].due_date` | `integer \| null` |  |
| `data[].effective_at` | `integer \| null` |  |
| `data[].ending_balance` | `integer \| null` |  |
| `data[].footer` | `string \| null` |  |
| `data[].from_invoice` | `object \| null` |  |
| `data[].hosted_invoice_url` | `string \| null` |  |
| `data[].invoice_pdf` | `string \| null` |  |
| `data[].issuer` | `object` |  |
| `data[].last_finalization_error` | `object \| null` |  |
| `data[].latest_revision` | `string \| null` |  |
| `data[].lines` | `object` |  |
| `data[].livemode` | `boolean` |  |
| `data[].metadata` | `object` |  |
| `data[].next_payment_attempt` | `integer \| null` |  |
| `data[].number` | `string \| null` |  |
| `data[].on_behalf_of` | `string \| null` |  |
| `data[].paid` | `boolean \| null` |  |
| `data[].paid_out_of_band` | `boolean \| null` |  |
| `data[].parent` | `object \| null` |  |
| `data[].payment_intent` | `string \| null` |  |
| `data[].payment_settings` | `object` |  |
| `data[].payments` | `object` |  |
| `data[].period_end` | `integer` |  |
| `data[].period_start` | `integer` |  |
| `data[].post_payment_credit_notes_amount` | `integer` |  |
| `data[].pre_payment_credit_notes_amount` | `integer` |  |
| `data[].quote` | `string \| null` |  |
| `data[].receipt_number` | `string \| null` |  |
| `data[].rendering` | `object \| null` |  |
| `data[].rendering_options` | `object \| null` |  |
| `data[].shipping_cost` | `object \| null` |  |
| `data[].shipping_details` | `object \| null` |  |
| `data[].starting_balance` | `integer` |  |
| `data[].statement_descriptor` | `string \| null` |  |
| `data[].status` | `string \| null` |  |
| `data[].status_transitions` | `object` |  |
| `data[].subscription` | `string \| null` |  |
| `data[].subscription_details` | `object \| null` |  |
| `data[].subtotal` | `integer` |  |
| `data[].subtotal_excluding_tax` | `integer \| null` |  |
| `data[].tax` | `integer \| null` |  |
| `data[].test_clock` | `string \| null` |  |
| `data[].threshold_reason` | `object \| null` |  |
| `data[].total` | `integer` |  |
| `data[].total_discount_amounts` | `array \| null` |  |
| `data[].total_excluding_tax` | `integer \| null` |  |
| `data[].total_pretax_credit_amounts` | `array \| null` |  |
| `data[].total_tax_amounts` | `array \| null` |  |
| `data[].total_taxes` | `array \| null` |  |
| `data[].transfer_data` | `object \| null` |  |
| `data[].webhooks_delivered_at` | `integer \| null` |  |
| `has_more` | `boolean` |  |
| `next_page` | `string \| null` |  |
| `url` | `string` |  |


</details>

### Invoices Search

Search and filter invoices records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await stripe.invoices.search(
    query={"filter": {"eq": {"account_country": "<str>"}}}
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
        "query": {"filter": {"eq": {"account_country": "<str>"}}}
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
| `account_country` | `string` | The country of the business associated with this invoice, commonly used to display localized content. |
| `account_name` | `string` | The public name of the business associated with this invoice. |
| `account_tax_ids` | `array` | Tax IDs of the account associated with this invoice. |
| `amount_due` | `integer` | Total amount, in smallest currency unit, that is due and owed by the customer. |
| `amount_paid` | `integer` | Total amount, in smallest currency unit, that has been paid by the customer. |
| `amount_remaining` | `integer` | The difference between amount_due and amount_paid, representing the outstanding balance. |
| `amount_shipping` | `integer` | Total amount of shipping costs on the invoice. |
| `application` | `string` | ID of the Connect application that created this invoice. |
| `application_fee` | `integer` | Amount of application fee charged for this invoice in a Connect scenario. |
| `application_fee_amount` | `integer` | The fee in smallest currency unit that is collected by the application in a Connect scenario. |
| `attempt_count` | `integer` | Number of payment attempts made for this invoice. |
| `attempted` | `boolean` | Whether an attempt has been made to pay the invoice. |
| `auto_advance` | `boolean` | Controls whether Stripe performs automatic collection of the invoice. |
| `automatic_tax` | `object` | Settings and status for automatic tax calculation on this invoice. |
| `billing` | `string` | Billing method used for the invoice (charge_automatically or send_invoice). |
| `billing_reason` | `string` | Indicates the reason why the invoice was created (subscription_cycle, manual, etc.). |
| `charge` | `string` | ID of the latest charge generated for this invoice, if any. |
| `closed` | `boolean` | Whether the invoice has been marked as closed and no longer open for collection. |
| `collection_method` | `string` | Method by which the invoice is collected: charge_automatically or send_invoice. |
| `created` | `integer` | Timestamp indicating when the invoice was created. |
| `currency` | `string` | Three-letter ISO currency code in which the invoice is denominated. |
| `custom_fields` | `array` | Custom fields displayed on the invoice as specified by the account. |
| `customer` | `string` | The customer object or ID associated with this invoice. |
| `customer_address` | `object` | The customer's address at the time the invoice was finalized. |
| `customer_email` | `string` | The customer's email address at the time the invoice was finalized. |
| `customer_name` | `string` | The customer's name at the time the invoice was finalized. |
| `customer_phone` | `string` | The customer's phone number at the time the invoice was finalized. |
| `customer_shipping` | `object` | The customer's shipping information at the time the invoice was finalized. |
| `customer_tax_exempt` | `string` | The customer's tax exempt status at the time the invoice was finalized. |
| `customer_tax_ids` | `array` | The customer's tax IDs at the time the invoice was finalized. |
| `default_payment_method` | `string` | Default payment method for the invoice, used if no other method is specified. |
| `default_source` | `string` | Default payment source for the invoice if no payment method is set. |
| `default_tax_rates` | `array` | The tax rates applied to the invoice by default. |
| `description` | `string` | An arbitrary string attached to the invoice, often displayed to customers. |
| `discount` | `object` | The discount object applied to the invoice, if any. |
| `discounts` | `array` | Array of discount IDs or objects currently applied to this invoice. |
| `due_date` | `number` | The date by which payment on this invoice is due, if the invoice is not auto-collected. |
| `effective_at` | `integer` | Timestamp when the invoice becomes effective and finalized for payment. |
| `ending_balance` | `integer` | The customer's ending account balance after this invoice is finalized. |
| `footer` | `string` | Footer text displayed on the invoice. |
| `forgiven` | `boolean` | Whether the invoice has been forgiven and is considered paid without actual payment. |
| `from_invoice` | `object` | Details about the invoice this invoice was created from, if applicable. |
| `hosted_invoice_url` | `string` | URL for the hosted invoice page where customers can view and pay the invoice. |
| `id` | `string` | Unique identifier for the invoice object. |
| `invoice_pdf` | `string` | URL for the PDF version of the invoice. |
| `is_deleted` | `boolean` | Indicates whether this invoice has been deleted. |
| `issuer` | `object` | Details about the entity issuing the invoice. |
| `last_finalization_error` | `object` | The error encountered during the last finalization attempt, if any. |
| `latest_revision` | `string` | The latest revision of the invoice, if revisions are enabled. |
| `lines` | `object` | The individual line items that make up the invoice, representing products, services, or fees. |
| `livemode` | `boolean` | Indicates whether the invoice exists in live mode (true) or test mode (false). |
| `metadata` | `object` | Key-value pairs for storing additional structured information about the invoice. |
| `next_payment_attempt` | `number` | Timestamp of the next automatic payment attempt for this invoice, if applicable. |
| `number` | `string` | A unique, human-readable identifier for this invoice, often shown to customers. |
| `object` | `string` | String representing the object type, always 'invoice'. |
| `on_behalf_of` | `string` | The account on behalf of which the invoice is being created, used in Connect scenarios. |
| `paid` | `boolean` | Whether the invoice has been paid in full. |
| `paid_out_of_band` | `boolean` | Whether payment was made outside of Stripe and manually marked as paid. |
| `payment` | `string` | ID of the payment associated with this invoice, if any. |
| `payment_intent` | `string` | The PaymentIntent associated with this invoice for processing payment. |
| `payment_settings` | `object` | Configuration settings for how payment should be collected on this invoice. |
| `period_end` | `number` | End date of the billing period covered by this invoice. |
| `period_start` | `number` | Start date of the billing period covered by this invoice. |
| `post_payment_credit_notes_amount` | `integer` | Total amount of credit notes issued after the invoice was paid. |
| `pre_payment_credit_notes_amount` | `integer` | Total amount of credit notes applied before payment was attempted. |
| `quote` | `string` | The quote from which this invoice was generated, if applicable. |
| `receipt_number` | `string` | The receipt number displayed on the invoice, if available. |
| `rendering` | `object` | Settings that control how the invoice is rendered for display. |
| `rendering_options` | `object` | Options for customizing the visual rendering of the invoice. |
| `shipping_cost` | `object` | Total cost of shipping charges included in the invoice. |
| `shipping_details` | `object` | Detailed shipping information for the invoice, including address and carrier. |
| `starting_balance` | `integer` | The customer's starting account balance at the beginning of the billing period. |
| `statement_description` | `string` | Extra information about the invoice that appears on the customer's credit card statement. |
| `statement_descriptor` | `string` | A dynamic descriptor that appears on the customer's credit card statement for this invoice. |
| `status` | `string` | The status of the invoice: draft, open, paid, void, or uncollectible. |
| `status_transitions` | `object` | Timestamps tracking when the invoice transitioned between different statuses. |
| `subscription` | `string` | The subscription this invoice was generated for, if applicable. |
| `subscription_details` | `object` | Additional details about the subscription associated with this invoice. |
| `subtotal` | `integer` | Total of all line items before discounts or tax are applied. |
| `subtotal_excluding_tax` | `integer` | The subtotal amount excluding any tax calculations. |
| `tax` | `integer` | Total tax amount applied to the invoice. |
| `tax_percent` | `number` | The percentage of tax applied to the invoice (deprecated, use total_tax_amounts instead). |
| `test_clock` | `string` | ID of the test clock this invoice belongs to, used for testing time-dependent billing. |
| `total` | `integer` | Total amount of the invoice after all line items, discounts, and taxes are calculated. |
| `total_discount_amounts` | `array` | Array of the total discount amounts applied, broken down by discount. |
| `total_excluding_tax` | `integer` | Total amount of the invoice excluding all tax calculations. |
| `total_tax_amounts` | `array` | Array of tax amounts applied to the invoice, broken down by tax rate. |
| `transfer_data` | `object` | Information about the transfer of funds associated with this invoice in Connect scenarios. |
| `updated` | `integer` | Timestamp indicating when the invoice was last updated. |
| `webhooks_delivered_at` | `number` | Timestamp indicating when webhooks for this invoice were successfully delivered. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.account_country` | `string` | The country of the business associated with this invoice, commonly used to display localized content. |
| `hits[].data.account_name` | `string` | The public name of the business associated with this invoice. |
| `hits[].data.account_tax_ids` | `array` | Tax IDs of the account associated with this invoice. |
| `hits[].data.amount_due` | `integer` | Total amount, in smallest currency unit, that is due and owed by the customer. |
| `hits[].data.amount_paid` | `integer` | Total amount, in smallest currency unit, that has been paid by the customer. |
| `hits[].data.amount_remaining` | `integer` | The difference between amount_due and amount_paid, representing the outstanding balance. |
| `hits[].data.amount_shipping` | `integer` | Total amount of shipping costs on the invoice. |
| `hits[].data.application` | `string` | ID of the Connect application that created this invoice. |
| `hits[].data.application_fee` | `integer` | Amount of application fee charged for this invoice in a Connect scenario. |
| `hits[].data.application_fee_amount` | `integer` | The fee in smallest currency unit that is collected by the application in a Connect scenario. |
| `hits[].data.attempt_count` | `integer` | Number of payment attempts made for this invoice. |
| `hits[].data.attempted` | `boolean` | Whether an attempt has been made to pay the invoice. |
| `hits[].data.auto_advance` | `boolean` | Controls whether Stripe performs automatic collection of the invoice. |
| `hits[].data.automatic_tax` | `object` | Settings and status for automatic tax calculation on this invoice. |
| `hits[].data.billing` | `string` | Billing method used for the invoice (charge_automatically or send_invoice). |
| `hits[].data.billing_reason` | `string` | Indicates the reason why the invoice was created (subscription_cycle, manual, etc.). |
| `hits[].data.charge` | `string` | ID of the latest charge generated for this invoice, if any. |
| `hits[].data.closed` | `boolean` | Whether the invoice has been marked as closed and no longer open for collection. |
| `hits[].data.collection_method` | `string` | Method by which the invoice is collected: charge_automatically or send_invoice. |
| `hits[].data.created` | `integer` | Timestamp indicating when the invoice was created. |
| `hits[].data.currency` | `string` | Three-letter ISO currency code in which the invoice is denominated. |
| `hits[].data.custom_fields` | `array` | Custom fields displayed on the invoice as specified by the account. |
| `hits[].data.customer` | `string` | The customer object or ID associated with this invoice. |
| `hits[].data.customer_address` | `object` | The customer's address at the time the invoice was finalized. |
| `hits[].data.customer_email` | `string` | The customer's email address at the time the invoice was finalized. |
| `hits[].data.customer_name` | `string` | The customer's name at the time the invoice was finalized. |
| `hits[].data.customer_phone` | `string` | The customer's phone number at the time the invoice was finalized. |
| `hits[].data.customer_shipping` | `object` | The customer's shipping information at the time the invoice was finalized. |
| `hits[].data.customer_tax_exempt` | `string` | The customer's tax exempt status at the time the invoice was finalized. |
| `hits[].data.customer_tax_ids` | `array` | The customer's tax IDs at the time the invoice was finalized. |
| `hits[].data.default_payment_method` | `string` | Default payment method for the invoice, used if no other method is specified. |
| `hits[].data.default_source` | `string` | Default payment source for the invoice if no payment method is set. |
| `hits[].data.default_tax_rates` | `array` | The tax rates applied to the invoice by default. |
| `hits[].data.description` | `string` | An arbitrary string attached to the invoice, often displayed to customers. |
| `hits[].data.discount` | `object` | The discount object applied to the invoice, if any. |
| `hits[].data.discounts` | `array` | Array of discount IDs or objects currently applied to this invoice. |
| `hits[].data.due_date` | `number` | The date by which payment on this invoice is due, if the invoice is not auto-collected. |
| `hits[].data.effective_at` | `integer` | Timestamp when the invoice becomes effective and finalized for payment. |
| `hits[].data.ending_balance` | `integer` | The customer's ending account balance after this invoice is finalized. |
| `hits[].data.footer` | `string` | Footer text displayed on the invoice. |
| `hits[].data.forgiven` | `boolean` | Whether the invoice has been forgiven and is considered paid without actual payment. |
| `hits[].data.from_invoice` | `object` | Details about the invoice this invoice was created from, if applicable. |
| `hits[].data.hosted_invoice_url` | `string` | URL for the hosted invoice page where customers can view and pay the invoice. |
| `hits[].data.id` | `string` | Unique identifier for the invoice object. |
| `hits[].data.invoice_pdf` | `string` | URL for the PDF version of the invoice. |
| `hits[].data.is_deleted` | `boolean` | Indicates whether this invoice has been deleted. |
| `hits[].data.issuer` | `object` | Details about the entity issuing the invoice. |
| `hits[].data.last_finalization_error` | `object` | The error encountered during the last finalization attempt, if any. |
| `hits[].data.latest_revision` | `string` | The latest revision of the invoice, if revisions are enabled. |
| `hits[].data.lines` | `object` | The individual line items that make up the invoice, representing products, services, or fees. |
| `hits[].data.livemode` | `boolean` | Indicates whether the invoice exists in live mode (true) or test mode (false). |
| `hits[].data.metadata` | `object` | Key-value pairs for storing additional structured information about the invoice. |
| `hits[].data.next_payment_attempt` | `number` | Timestamp of the next automatic payment attempt for this invoice, if applicable. |
| `hits[].data.number` | `string` | A unique, human-readable identifier for this invoice, often shown to customers. |
| `hits[].data.object` | `string` | String representing the object type, always 'invoice'. |
| `hits[].data.on_behalf_of` | `string` | The account on behalf of which the invoice is being created, used in Connect scenarios. |
| `hits[].data.paid` | `boolean` | Whether the invoice has been paid in full. |
| `hits[].data.paid_out_of_band` | `boolean` | Whether payment was made outside of Stripe and manually marked as paid. |
| `hits[].data.payment` | `string` | ID of the payment associated with this invoice, if any. |
| `hits[].data.payment_intent` | `string` | The PaymentIntent associated with this invoice for processing payment. |
| `hits[].data.payment_settings` | `object` | Configuration settings for how payment should be collected on this invoice. |
| `hits[].data.period_end` | `number` | End date of the billing period covered by this invoice. |
| `hits[].data.period_start` | `number` | Start date of the billing period covered by this invoice. |
| `hits[].data.post_payment_credit_notes_amount` | `integer` | Total amount of credit notes issued after the invoice was paid. |
| `hits[].data.pre_payment_credit_notes_amount` | `integer` | Total amount of credit notes applied before payment was attempted. |
| `hits[].data.quote` | `string` | The quote from which this invoice was generated, if applicable. |
| `hits[].data.receipt_number` | `string` | The receipt number displayed on the invoice, if available. |
| `hits[].data.rendering` | `object` | Settings that control how the invoice is rendered for display. |
| `hits[].data.rendering_options` | `object` | Options for customizing the visual rendering of the invoice. |
| `hits[].data.shipping_cost` | `object` | Total cost of shipping charges included in the invoice. |
| `hits[].data.shipping_details` | `object` | Detailed shipping information for the invoice, including address and carrier. |
| `hits[].data.starting_balance` | `integer` | The customer's starting account balance at the beginning of the billing period. |
| `hits[].data.statement_description` | `string` | Extra information about the invoice that appears on the customer's credit card statement. |
| `hits[].data.statement_descriptor` | `string` | A dynamic descriptor that appears on the customer's credit card statement for this invoice. |
| `hits[].data.status` | `string` | The status of the invoice: draft, open, paid, void, or uncollectible. |
| `hits[].data.status_transitions` | `object` | Timestamps tracking when the invoice transitioned between different statuses. |
| `hits[].data.subscription` | `string` | The subscription this invoice was generated for, if applicable. |
| `hits[].data.subscription_details` | `object` | Additional details about the subscription associated with this invoice. |
| `hits[].data.subtotal` | `integer` | Total of all line items before discounts or tax are applied. |
| `hits[].data.subtotal_excluding_tax` | `integer` | The subtotal amount excluding any tax calculations. |
| `hits[].data.tax` | `integer` | Total tax amount applied to the invoice. |
| `hits[].data.tax_percent` | `number` | The percentage of tax applied to the invoice (deprecated, use total_tax_amounts instead). |
| `hits[].data.test_clock` | `string` | ID of the test clock this invoice belongs to, used for testing time-dependent billing. |
| `hits[].data.total` | `integer` | Total amount of the invoice after all line items, discounts, and taxes are calculated. |
| `hits[].data.total_discount_amounts` | `array` | Array of the total discount amounts applied, broken down by discount. |
| `hits[].data.total_excluding_tax` | `integer` | Total amount of the invoice excluding all tax calculations. |
| `hits[].data.total_tax_amounts` | `array` | Array of tax amounts applied to the invoice, broken down by tax rate. |
| `hits[].data.transfer_data` | `object` | Information about the transfer of funds associated with this invoice in Connect scenarios. |
| `hits[].data.updated` | `integer` | Timestamp indicating when the invoice was last updated. |
| `hits[].data.webhooks_delivered_at` | `number` | Timestamp indicating when webhooks for this invoice were successfully delivered. |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Charges

### Charges List

Returns a list of charges you've previously created. The charges are returned in sorted order, with the most recent charges appearing first.

#### Python SDK

```python
await stripe.charges.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "charges",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `created` | `object` | No | Only return customers that were created during the given date interval. |
| `created.gt` | `integer` | No | Minimum value to filter by (exclusive) |
| `created.gte` | `integer` | No | Minimum value to filter by (inclusive) |
| `created.lt` | `integer` | No | Maximum value to filter by (exclusive) |
| `created.lte` | `integer` | No | Maximum value to filter by (inclusive) |
| `customer` | `string` | No | Only return charges for the customer specified by this customer ID |
| `ending_before` | `string` | No | A cursor for use in pagination. ending_before is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj_bar, your subsequent call can include ending_before=obj_bar in order to fetch the previous page of the list. |
| `limit` | `integer` | No | A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10. |
| `payment_intent` | `string` | No | Only return charges that were created by the PaymentIntent specified by this ID |
| `starting_after` | `string` | No | A cursor for use in pagination. starting_after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include starting_after=obj_foo in order to fetch the next page of the list. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"charge"` |  |
| `created` | `integer` |  |
| `livemode` | `boolean` |  |
| `amount` | `integer` |  |
| `amount_captured` | `integer` |  |
| `amount_refunded` | `integer` |  |
| `amount_updates` | `array \| null` |  |
| `application` | `string \| null` |  |
| `application_fee` | `string \| null` |  |
| `application_fee_amount` | `integer \| null` |  |
| `calculated_statement_descriptor` | `string \| null` |  |
| `currency` | `string` |  |
| `customer` | `string \| null` |  |
| `description` | `string \| null` |  |
| `destination` | `string \| null` |  |
| `dispute` | `string \| null` |  |
| `disputed` | `boolean` |  |
| `failure_balance_transaction` | `string \| null` |  |
| `failure_code` | `string \| null` |  |
| `failure_message` | `string \| null` |  |
| `fraud_details` | `object \| null` |  |
| `invoice` | `string \| null` |  |
| `on_behalf_of` | `string \| null` |  |
| `order` | `string \| null` |  |
| `outcome` | `object \| null` |  |
| `paid` | `boolean` |  |
| `payment_intent` | `string \| null` |  |
| `payment_method` | `string \| null` |  |
| `payment_method_details` | `object \| null` |  |
| `presentment_details` | `object \| null` |  |
| `receipt_email` | `string \| null` |  |
| `receipt_number` | `string \| null` |  |
| `receipt_url` | `string \| null` |  |
| `refunded` | `boolean` |  |
| `refunds` | `object \| null` |  |
| `review` | `string \| null` |  |
| `shipping` | `object \| null` |  |
| `source` | `object \| null` |  |
| `source_transfer` | `string \| null` |  |
| `statement_descriptor` | `string \| null` |  |
| `statement_descriptor_suffix` | `string \| null` |  |
| `status` | `"succeeded" \| "pending" \| "failed"` |  |
| `transfer_data` | `object \| null` |  |
| `transfer_group` | `string \| null` |  |
| `captured` | `boolean` |  |
| `balance_transaction` | `string \| null` |  |
| `billing_details` | `object` |  |
| `metadata` | `object` |  |
| `radar_options` | `object \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

### Charges Get

Retrieves the details of a charge that has previously been created

#### Python SDK

```python
await stripe.charges.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "charges",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The charge ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"charge"` |  |
| `created` | `integer` |  |
| `livemode` | `boolean` |  |
| `amount` | `integer` |  |
| `amount_captured` | `integer` |  |
| `amount_refunded` | `integer` |  |
| `amount_updates` | `array \| null` |  |
| `application` | `string \| null` |  |
| `application_fee` | `string \| null` |  |
| `application_fee_amount` | `integer \| null` |  |
| `calculated_statement_descriptor` | `string \| null` |  |
| `currency` | `string` |  |
| `customer` | `string \| null` |  |
| `description` | `string \| null` |  |
| `destination` | `string \| null` |  |
| `dispute` | `string \| null` |  |
| `disputed` | `boolean` |  |
| `failure_balance_transaction` | `string \| null` |  |
| `failure_code` | `string \| null` |  |
| `failure_message` | `string \| null` |  |
| `fraud_details` | `object \| null` |  |
| `invoice` | `string \| null` |  |
| `on_behalf_of` | `string \| null` |  |
| `order` | `string \| null` |  |
| `outcome` | `object \| null` |  |
| `paid` | `boolean` |  |
| `payment_intent` | `string \| null` |  |
| `payment_method` | `string \| null` |  |
| `payment_method_details` | `object \| null` |  |
| `presentment_details` | `object \| null` |  |
| `receipt_email` | `string \| null` |  |
| `receipt_number` | `string \| null` |  |
| `receipt_url` | `string \| null` |  |
| `refunded` | `boolean` |  |
| `refunds` | `object \| null` |  |
| `review` | `string \| null` |  |
| `shipping` | `object \| null` |  |
| `source` | `object \| null` |  |
| `source_transfer` | `string \| null` |  |
| `statement_descriptor` | `string \| null` |  |
| `statement_descriptor_suffix` | `string \| null` |  |
| `status` | `"succeeded" \| "pending" \| "failed"` |  |
| `transfer_data` | `object \| null` |  |
| `transfer_group` | `string \| null` |  |
| `captured` | `boolean` |  |
| `balance_transaction` | `string \| null` |  |
| `billing_details` | `object` |  |
| `metadata` | `object` |  |
| `radar_options` | `object \| null` |  |


</details>

### Charges API Search

Search for charges using Stripe's Search Query Language

#### Python SDK

```python
await stripe.charges.api_search(
    query="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "charges",
    "action": "api_search",
    "params": {
        "query": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | Yes | The search query string using Stripe's Search Query Language |
| `limit` | `integer` | No | A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10. |
| `page` | `string` | No | A cursor for pagination across multiple pages of results. Don’t include this parameter on the first call. Use the next_page value returned in a previous response to request subsequent results. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `object` | `"search_result"` |  |
| `data` | `array<object>` |  |
| `data[].id` | `string` |  |
| `data[].object` | `"charge"` |  |
| `data[].created` | `integer` |  |
| `data[].livemode` | `boolean` |  |
| `data[].amount` | `integer` |  |
| `data[].amount_captured` | `integer` |  |
| `data[].amount_refunded` | `integer` |  |
| `data[].amount_updates` | `array \| null` |  |
| `data[].application` | `string \| null` |  |
| `data[].application_fee` | `string \| null` |  |
| `data[].application_fee_amount` | `integer \| null` |  |
| `data[].calculated_statement_descriptor` | `string \| null` |  |
| `data[].currency` | `string` |  |
| `data[].customer` | `string \| null` |  |
| `data[].description` | `string \| null` |  |
| `data[].destination` | `string \| null` |  |
| `data[].dispute` | `string \| null` |  |
| `data[].disputed` | `boolean` |  |
| `data[].failure_balance_transaction` | `string \| null` |  |
| `data[].failure_code` | `string \| null` |  |
| `data[].failure_message` | `string \| null` |  |
| `data[].fraud_details` | `object \| null` |  |
| `data[].invoice` | `string \| null` |  |
| `data[].on_behalf_of` | `string \| null` |  |
| `data[].order` | `string \| null` |  |
| `data[].outcome` | `object \| null` |  |
| `data[].paid` | `boolean` |  |
| `data[].payment_intent` | `string \| null` |  |
| `data[].payment_method` | `string \| null` |  |
| `data[].payment_method_details` | `object \| null` |  |
| `data[].presentment_details` | `object \| null` |  |
| `data[].receipt_email` | `string \| null` |  |
| `data[].receipt_number` | `string \| null` |  |
| `data[].receipt_url` | `string \| null` |  |
| `data[].refunded` | `boolean` |  |
| `data[].refunds` | `object \| null` |  |
| `data[].review` | `string \| null` |  |
| `data[].shipping` | `object \| null` |  |
| `data[].source` | `object \| null` |  |
| `data[].source_transfer` | `string \| null` |  |
| `data[].statement_descriptor` | `string \| null` |  |
| `data[].statement_descriptor_suffix` | `string \| null` |  |
| `data[].status` | `"succeeded" \| "pending" \| "failed"` |  |
| `data[].transfer_data` | `object \| null` |  |
| `data[].transfer_group` | `string \| null` |  |
| `data[].captured` | `boolean` |  |
| `data[].balance_transaction` | `string \| null` |  |
| `data[].billing_details` | `object` |  |
| `data[].metadata` | `object` |  |
| `data[].radar_options` | `object \| null` |  |
| `has_more` | `boolean` |  |
| `next_page` | `string \| null` |  |
| `url` | `string` |  |


</details>

### Charges Search

Search and filter charges records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await stripe.charges.search(
    query={"filter": {"eq": {"amount": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "charges",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"amount": 0}}}
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
| `amount` | `integer` | Amount intended to be collected by this payment in the smallest currency unit (e.g., 100 cents for $1.00), supporting up to eight digits. |
| `amount_captured` | `integer` | Amount that was actually captured from this charge. |
| `amount_refunded` | `integer` | Amount that has been refunded back to the customer. |
| `amount_updates` | `array` | Updates to the amount that have been made during the charge lifecycle. |
| `application` | `string` | ID of the application that created this charge (Connect only). |
| `application_fee` | `string` | ID of the application fee associated with this charge (Connect only). |
| `application_fee_amount` | `integer` | The amount of the application fee deducted from this charge (Connect only). |
| `balance_transaction` | `string` | ID of the balance transaction that describes the impact of this charge on your account balance (excluding refunds or disputes). |
| `billing_details` | `object` | Billing information associated with the payment method at the time of the transaction, including name, email, phone, and address. |
| `calculated_statement_descriptor` | `string` | The full statement descriptor that appears on the customer's credit card statement, combining prefix and suffix. |
| `captured` | `boolean` | Whether the charge has been captured and funds transferred to your account. |
| `card` | `object` | Deprecated card object containing payment card details if a card was used. |
| `created` | `integer` | Timestamp indicating when the charge was created. |
| `currency` | `string` | Three-letter ISO currency code in lowercase (e.g., 'usd', 'eur') for the charge amount. |
| `customer` | `string` | ID of the customer this charge is for, if one exists. |
| `description` | `string` | An arbitrary string attached to the charge, often useful for displaying to users or internal reference. |
| `destination` | `string` | ID of the destination account where funds are transferred (Connect only). |
| `dispute` | `string` | ID of the dispute object if the charge has been disputed. |
| `disputed` | `boolean` | Whether the charge has been disputed by the customer with their card issuer. |
| `failure_balance_transaction` | `string` | ID of the balance transaction that describes the reversal of funds if the charge failed. |
| `failure_code` | `string` | Error code explaining the reason for charge failure, if applicable. |
| `failure_message` | `string` | Human-readable message providing more details about why the charge failed. |
| `fraud_details` | `object` | Information about fraud assessments and user reports related to this charge. |
| `id` | `string` | Unique identifier for the charge, used to link transactions across other records. |
| `invoice` | `string` | ID of the invoice this charge is for, if the charge was created by invoicing. |
| `livemode` | `boolean` | Whether the charge occurred in live mode (true) or test mode (false). |
| `metadata` | `object` | Key-value pairs for storing additional structured information about the charge, useful for internal tracking. |
| `object` | `string` | String representing the object type, always 'charge' for charge objects. |
| `on_behalf_of` | `string` | ID of the account on whose behalf the charge was made (Connect only). |
| `order` | `string` | Deprecated field for order information associated with this charge. |
| `outcome` | `object` | Details about the outcome of the charge, including network status, risk assessment, and reason codes. |
| `paid` | `boolean` | Whether the charge succeeded and funds were successfully collected. |
| `payment_intent` | `string` | ID of the PaymentIntent associated with this charge, if one exists. |
| `payment_method` | `string` | ID of the payment method used for this charge. |
| `payment_method_details` | `object` | Details about the payment method at the time of the transaction, including card brand, network, and authentication results. |
| `receipt_email` | `string` | Email address to which the receipt for this charge was sent. |
| `receipt_number` | `string` | Receipt number that appears on email receipts sent for this charge. |
| `receipt_url` | `string` | URL to a hosted receipt page for this charge, viewable by the customer. |
| `refunded` | `boolean` | Whether the charge has been fully refunded (partial refunds will still show as false). |
| `refunds` | `object` | List of refunds that have been applied to this charge. |
| `review` | `string` | ID of the review object associated with this charge, if it was flagged for manual review. |
| `shipping` | `object` | Shipping information for the charge, including recipient name, address, and tracking details. |
| `source` | `object` | Deprecated payment source object used to create this charge. |
| `source_transfer` | `string` | ID of the transfer from a source account if funds came from another Stripe account (Connect only). |
| `statement_description` | `string` | Deprecated alias for statement_descriptor. |
| `statement_descriptor` | `string` | Statement descriptor that overrides the account default for card charges, appearing on the customer's statement. |
| `statement_descriptor_suffix` | `string` | Suffix concatenated to the account's statement descriptor prefix to form the complete descriptor on customer statements. |
| `status` | `string` | Current status of the payment: 'succeeded' (completed), 'pending' (processing), or 'failed' (unsuccessful). |
| `transfer_data` | `object` | Object containing destination and amount for transfers to connected accounts (Connect only). |
| `transfer_group` | `string` | String identifier for grouping related charges and transfers together (Connect only). |
| `updated` | `integer` | Timestamp of the last update to this charge object. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.amount` | `integer` | Amount intended to be collected by this payment in the smallest currency unit (e.g., 100 cents for $1.00), supporting up to eight digits. |
| `hits[].data.amount_captured` | `integer` | Amount that was actually captured from this charge. |
| `hits[].data.amount_refunded` | `integer` | Amount that has been refunded back to the customer. |
| `hits[].data.amount_updates` | `array` | Updates to the amount that have been made during the charge lifecycle. |
| `hits[].data.application` | `string` | ID of the application that created this charge (Connect only). |
| `hits[].data.application_fee` | `string` | ID of the application fee associated with this charge (Connect only). |
| `hits[].data.application_fee_amount` | `integer` | The amount of the application fee deducted from this charge (Connect only). |
| `hits[].data.balance_transaction` | `string` | ID of the balance transaction that describes the impact of this charge on your account balance (excluding refunds or disputes). |
| `hits[].data.billing_details` | `object` | Billing information associated with the payment method at the time of the transaction, including name, email, phone, and address. |
| `hits[].data.calculated_statement_descriptor` | `string` | The full statement descriptor that appears on the customer's credit card statement, combining prefix and suffix. |
| `hits[].data.captured` | `boolean` | Whether the charge has been captured and funds transferred to your account. |
| `hits[].data.card` | `object` | Deprecated card object containing payment card details if a card was used. |
| `hits[].data.created` | `integer` | Timestamp indicating when the charge was created. |
| `hits[].data.currency` | `string` | Three-letter ISO currency code in lowercase (e.g., 'usd', 'eur') for the charge amount. |
| `hits[].data.customer` | `string` | ID of the customer this charge is for, if one exists. |
| `hits[].data.description` | `string` | An arbitrary string attached to the charge, often useful for displaying to users or internal reference. |
| `hits[].data.destination` | `string` | ID of the destination account where funds are transferred (Connect only). |
| `hits[].data.dispute` | `string` | ID of the dispute object if the charge has been disputed. |
| `hits[].data.disputed` | `boolean` | Whether the charge has been disputed by the customer with their card issuer. |
| `hits[].data.failure_balance_transaction` | `string` | ID of the balance transaction that describes the reversal of funds if the charge failed. |
| `hits[].data.failure_code` | `string` | Error code explaining the reason for charge failure, if applicable. |
| `hits[].data.failure_message` | `string` | Human-readable message providing more details about why the charge failed. |
| `hits[].data.fraud_details` | `object` | Information about fraud assessments and user reports related to this charge. |
| `hits[].data.id` | `string` | Unique identifier for the charge, used to link transactions across other records. |
| `hits[].data.invoice` | `string` | ID of the invoice this charge is for, if the charge was created by invoicing. |
| `hits[].data.livemode` | `boolean` | Whether the charge occurred in live mode (true) or test mode (false). |
| `hits[].data.metadata` | `object` | Key-value pairs for storing additional structured information about the charge, useful for internal tracking. |
| `hits[].data.object` | `string` | String representing the object type, always 'charge' for charge objects. |
| `hits[].data.on_behalf_of` | `string` | ID of the account on whose behalf the charge was made (Connect only). |
| `hits[].data.order` | `string` | Deprecated field for order information associated with this charge. |
| `hits[].data.outcome` | `object` | Details about the outcome of the charge, including network status, risk assessment, and reason codes. |
| `hits[].data.paid` | `boolean` | Whether the charge succeeded and funds were successfully collected. |
| `hits[].data.payment_intent` | `string` | ID of the PaymentIntent associated with this charge, if one exists. |
| `hits[].data.payment_method` | `string` | ID of the payment method used for this charge. |
| `hits[].data.payment_method_details` | `object` | Details about the payment method at the time of the transaction, including card brand, network, and authentication results. |
| `hits[].data.receipt_email` | `string` | Email address to which the receipt for this charge was sent. |
| `hits[].data.receipt_number` | `string` | Receipt number that appears on email receipts sent for this charge. |
| `hits[].data.receipt_url` | `string` | URL to a hosted receipt page for this charge, viewable by the customer. |
| `hits[].data.refunded` | `boolean` | Whether the charge has been fully refunded (partial refunds will still show as false). |
| `hits[].data.refunds` | `object` | List of refunds that have been applied to this charge. |
| `hits[].data.review` | `string` | ID of the review object associated with this charge, if it was flagged for manual review. |
| `hits[].data.shipping` | `object` | Shipping information for the charge, including recipient name, address, and tracking details. |
| `hits[].data.source` | `object` | Deprecated payment source object used to create this charge. |
| `hits[].data.source_transfer` | `string` | ID of the transfer from a source account if funds came from another Stripe account (Connect only). |
| `hits[].data.statement_description` | `string` | Deprecated alias for statement_descriptor. |
| `hits[].data.statement_descriptor` | `string` | Statement descriptor that overrides the account default for card charges, appearing on the customer's statement. |
| `hits[].data.statement_descriptor_suffix` | `string` | Suffix concatenated to the account's statement descriptor prefix to form the complete descriptor on customer statements. |
| `hits[].data.status` | `string` | Current status of the payment: 'succeeded' (completed), 'pending' (processing), or 'failed' (unsuccessful). |
| `hits[].data.transfer_data` | `object` | Object containing destination and amount for transfers to connected accounts (Connect only). |
| `hits[].data.transfer_group` | `string` | String identifier for grouping related charges and transfers together (Connect only). |
| `hits[].data.updated` | `integer` | Timestamp of the last update to this charge object. |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Subscriptions

### Subscriptions List

By default, returns a list of subscriptions that have not been canceled

#### Python SDK

```python
await stripe.subscriptions.list()
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
| `automatic_tax` | `object` | No | Filter subscriptions by their automatic tax settings. |
| `automatic_tax.enabled` | `boolean` | No | Enabled automatic tax calculation which will automatically compute tax rates on all invoices generated by the subscription. |
| `collection_method` | `"charge_automatically" \| "send_invoice"` | No | The collection method of the subscriptions to retrieve |
| `created` | `object` | No | Only return customers that were created during the given date interval. |
| `created.gt` | `integer` | No | Minimum value to filter by (exclusive) |
| `created.gte` | `integer` | No | Minimum value to filter by (inclusive) |
| `created.lt` | `integer` | No | Maximum value to filter by (exclusive) |
| `created.lte` | `integer` | No | Maximum value to filter by (inclusive) |
| `current_period_end` | `object` | No | Only return subscriptions whose minimum item current_period_end falls within the given date interval. |
| `current_period_end.gt` | `integer` | No | Minimum value to filter by (exclusive) |
| `current_period_end.gte` | `integer` | No | Minimum value to filter by (inclusive) |
| `current_period_end.lt` | `integer` | No | Maximum value to filter by (exclusive) |
| `current_period_end.lte` | `integer` | No | Maximum value to filter by (inclusive) |
| `current_period_start` | `object` | No | Only return subscriptions whose maximum item current_period_start falls within the given date interval. |
| `current_period_start.gt` | `integer` | No | Minimum value to filter by (exclusive) |
| `current_period_start.gte` | `integer` | No | Minimum value to filter by (inclusive) |
| `current_period_start.lt` | `integer` | No | Maximum value to filter by (exclusive) |
| `current_period_start.lte` | `integer` | No | Maximum value to filter by (inclusive) |
| `customer` | `string` | No | Only return subscriptions for the customer specified by this customer ID |
| `customer_account` | `string` | No | The ID of the account whose subscriptions will be retrieved. |
| `ending_before` | `string` | No | A cursor for use in pagination. ending_before is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj_bar, your subsequent call can include ending_before=obj_bar in order to fetch the previous page of the list. |
| `limit` | `integer` | No | A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10. |
| `price` | `string` | No | Filter for subscriptions that contain this recurring price ID. |
| `starting_after` | `string` | No | A cursor for use in pagination. starting_after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include starting_after=obj_foo in order to fetch the next page of the list. |
| `status` | `"canceled" \| "ended" \| "all"` | No | The status of the subscriptions to retrieve. Passing in a value of canceled will return all canceled subscriptions, including those belonging to deleted customers. Pass ended to find subscriptions that are canceled and subscriptions that are expired due to incomplete payment. Passing in a value of all will return subscriptions of all statuses. If no value is supplied, all subscriptions that have not been canceled are returned. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"subscription"` |  |
| `application` | `string \| null` |  |
| `application_fee_percent` | `number \| null` |  |
| `automatic_tax` | `object` |  |
| `billing_cycle_anchor` | `integer` |  |
| `billing_cycle_anchor_config` | `object \| null` |  |
| `billing_mode` | `object` |  |
| `billing_thresholds` | `object \| null` |  |
| `cancel_at` | `integer \| null` |  |
| `cancel_at_period_end` | `boolean` |  |
| `canceled_at` | `integer \| null` |  |
| `cancellation_details` | `object \| null` |  |
| `collection_method` | `"charge_automatically" \| "send_invoice"` |  |
| `created` | `integer` |  |
| `currency` | `string` |  |
| `customer` | `string` |  |
| `customer_account` | `string \| null` |  |
| `days_until_due` | `integer \| null` |  |
| `default_payment_method` | `string \| null` |  |
| `default_source` | `string \| null` |  |
| `default_tax_rates` | `array \| null` |  |
| `description` | `string \| null` |  |
| `discounts` | `array<string>` |  |
| `ended_at` | `integer \| null` |  |
| `invoice_settings` | `object` |  |
| `items` | `object` |  |
| `latest_invoice` | `string \| null` |  |
| `livemode` | `boolean` |  |
| `metadata` | `object` |  |
| `next_pending_invoice_item_invoice` | `integer \| null` |  |
| `on_behalf_of` | `string \| null` |  |
| `pause_collection` | `object \| null` |  |
| `payment_settings` | `object \| null` |  |
| `status` | `"incomplete" \| "incomplete_expired" \| "trialing" \| "active" \| "past_due" \| "canceled" \| "unpaid" \| "paused"` |  |
| `current_period_start` | `integer` |  |
| `current_period_end` | `integer` |  |
| `start_date` | `integer` |  |
| `trial_start` | `integer \| null` |  |
| `trial_end` | `integer \| null` |  |
| `discount` | `object \| null` |  |
| `plan` | `object \| null` |  |
| `quantity` | `integer \| null` |  |
| `schedule` | `string \| null` |  |
| `test_clock` | `string \| null` |  |
| `transfer_data` | `object \| null` |  |
| `trial_settings` | `object \| null` |  |
| `pending_invoice_item_interval` | `object \| null` |  |
| `pending_setup_intent` | `string \| null` |  |
| `pending_update` | `object \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

### Subscriptions Get

Retrieves the subscription with the given ID

#### Python SDK

```python
await stripe.subscriptions.get(
    id="<str>"
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
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The subscription ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"subscription"` |  |
| `application` | `string \| null` |  |
| `application_fee_percent` | `number \| null` |  |
| `automatic_tax` | `object` |  |
| `billing_cycle_anchor` | `integer` |  |
| `billing_cycle_anchor_config` | `object \| null` |  |
| `billing_mode` | `object` |  |
| `billing_thresholds` | `object \| null` |  |
| `cancel_at` | `integer \| null` |  |
| `cancel_at_period_end` | `boolean` |  |
| `canceled_at` | `integer \| null` |  |
| `cancellation_details` | `object \| null` |  |
| `collection_method` | `"charge_automatically" \| "send_invoice"` |  |
| `created` | `integer` |  |
| `currency` | `string` |  |
| `customer` | `string` |  |
| `customer_account` | `string \| null` |  |
| `days_until_due` | `integer \| null` |  |
| `default_payment_method` | `string \| null` |  |
| `default_source` | `string \| null` |  |
| `default_tax_rates` | `array \| null` |  |
| `description` | `string \| null` |  |
| `discounts` | `array<string>` |  |
| `ended_at` | `integer \| null` |  |
| `invoice_settings` | `object` |  |
| `items` | `object` |  |
| `latest_invoice` | `string \| null` |  |
| `livemode` | `boolean` |  |
| `metadata` | `object` |  |
| `next_pending_invoice_item_invoice` | `integer \| null` |  |
| `on_behalf_of` | `string \| null` |  |
| `pause_collection` | `object \| null` |  |
| `payment_settings` | `object \| null` |  |
| `status` | `"incomplete" \| "incomplete_expired" \| "trialing" \| "active" \| "past_due" \| "canceled" \| "unpaid" \| "paused"` |  |
| `current_period_start` | `integer` |  |
| `current_period_end` | `integer` |  |
| `start_date` | `integer` |  |
| `trial_start` | `integer \| null` |  |
| `trial_end` | `integer \| null` |  |
| `discount` | `object \| null` |  |
| `plan` | `object \| null` |  |
| `quantity` | `integer \| null` |  |
| `schedule` | `string \| null` |  |
| `test_clock` | `string \| null` |  |
| `transfer_data` | `object \| null` |  |
| `trial_settings` | `object \| null` |  |
| `pending_invoice_item_interval` | `object \| null` |  |
| `pending_setup_intent` | `string \| null` |  |
| `pending_update` | `object \| null` |  |


</details>

### Subscriptions API Search

Search for subscriptions using Stripe's Search Query Language

#### Python SDK

```python
await stripe.subscriptions.api_search(
    query="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "subscriptions",
    "action": "api_search",
    "params": {
        "query": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | Yes | The search query string using Stripe's Search Query Language |
| `limit` | `integer` | No | A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10. |
| `page` | `string` | No | A cursor for pagination across multiple pages of results. Don't include this parameter on the first call. Use the next_page value returned in a previous response to request subsequent results. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `object` | `"search_result"` |  |
| `data` | `array<object>` |  |
| `data[].id` | `string` |  |
| `data[].object` | `"subscription"` |  |
| `data[].application` | `string \| null` |  |
| `data[].application_fee_percent` | `number \| null` |  |
| `data[].automatic_tax` | `object` |  |
| `data[].billing_cycle_anchor` | `integer` |  |
| `data[].billing_cycle_anchor_config` | `object \| null` |  |
| `data[].billing_mode` | `object` |  |
| `data[].billing_thresholds` | `object \| null` |  |
| `data[].cancel_at` | `integer \| null` |  |
| `data[].cancel_at_period_end` | `boolean` |  |
| `data[].canceled_at` | `integer \| null` |  |
| `data[].cancellation_details` | `object \| null` |  |
| `data[].collection_method` | `"charge_automatically" \| "send_invoice"` |  |
| `data[].created` | `integer` |  |
| `data[].currency` | `string` |  |
| `data[].customer` | `string` |  |
| `data[].customer_account` | `string \| null` |  |
| `data[].days_until_due` | `integer \| null` |  |
| `data[].default_payment_method` | `string \| null` |  |
| `data[].default_source` | `string \| null` |  |
| `data[].default_tax_rates` | `array \| null` |  |
| `data[].description` | `string \| null` |  |
| `data[].discounts` | `array<string>` |  |
| `data[].ended_at` | `integer \| null` |  |
| `data[].invoice_settings` | `object` |  |
| `data[].items` | `object` |  |
| `data[].latest_invoice` | `string \| null` |  |
| `data[].livemode` | `boolean` |  |
| `data[].metadata` | `object` |  |
| `data[].next_pending_invoice_item_invoice` | `integer \| null` |  |
| `data[].on_behalf_of` | `string \| null` |  |
| `data[].pause_collection` | `object \| null` |  |
| `data[].payment_settings` | `object \| null` |  |
| `data[].status` | `"incomplete" \| "incomplete_expired" \| "trialing" \| "active" \| "past_due" \| "canceled" \| "unpaid" \| "paused"` |  |
| `data[].current_period_start` | `integer` |  |
| `data[].current_period_end` | `integer` |  |
| `data[].start_date` | `integer` |  |
| `data[].trial_start` | `integer \| null` |  |
| `data[].trial_end` | `integer \| null` |  |
| `data[].discount` | `object \| null` |  |
| `data[].plan` | `object \| null` |  |
| `data[].quantity` | `integer \| null` |  |
| `data[].schedule` | `string \| null` |  |
| `data[].test_clock` | `string \| null` |  |
| `data[].transfer_data` | `object \| null` |  |
| `data[].trial_settings` | `object \| null` |  |
| `data[].pending_invoice_item_interval` | `object \| null` |  |
| `data[].pending_setup_intent` | `string \| null` |  |
| `data[].pending_update` | `object \| null` |  |
| `has_more` | `boolean` |  |
| `next_page` | `string \| null` |  |
| `url` | `string` |  |


</details>

### Subscriptions Search

Search and filter subscriptions records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await stripe.subscriptions.search(
    query={"filter": {"eq": {"application": "<str>"}}}
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
        "query": {"filter": {"eq": {"application": "<str>"}}}
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
| `application` | `string` | For Connect platforms, the application associated with the subscription. |
| `application_fee_percent` | `number` | For Connect platforms, the percentage of the subscription amount taken as an application fee. |
| `automatic_tax` | `object` | Automatic tax calculation settings for the subscription. |
| `billing` | `string` | Billing mode configuration for the subscription. |
| `billing_cycle_anchor` | `number` | Timestamp determining when the billing cycle for the subscription starts. |
| `billing_cycle_anchor_config` | `object` | Configuration for the subscription's billing cycle anchor behavior. |
| `billing_thresholds` | `object` | Defines thresholds at which an invoice will be sent, controlling billing timing based on usage. |
| `cancel_at` | `number` | Timestamp indicating when the subscription is scheduled to be canceled. |
| `cancel_at_period_end` | `boolean` | Boolean indicating whether the subscription will be canceled at the end of the current billing period. |
| `canceled_at` | `number` | Timestamp indicating when the subscription was canceled, if applicable. |
| `cancellation_details` | `object` | Details about why and how the subscription was canceled. |
| `collection_method` | `string` | How invoices are collected (charge_automatically or send_invoice). |
| `created` | `integer` | Timestamp indicating when the subscription was created. |
| `currency` | `string` | Three-letter ISO currency code in lowercase indicating the currency for the subscription. |
| `current_period_end` | `number` | Timestamp marking the end of the current billing period. |
| `current_period_start` | `integer` | Timestamp marking the start of the current billing period. |
| `customer` | `string` | ID of the customer who owns the subscription, expandable to full customer object. |
| `days_until_due` | `integer` | Number of days until the invoice is due for subscriptions using send_invoice collection method. |
| `default_payment_method` | `string` | ID of the default payment method for the subscription, taking precedence over default_source. |
| `default_source` | `string` | ID of the default payment source for the subscription. |
| `default_tax_rates` | `array` | Tax rates that apply to the subscription by default. |
| `description` | `string` | Human-readable description of the subscription, displayable to the customer. |
| `discount` | `object` | Describes any discount currently applied to the subscription. |
| `ended_at` | `number` | Timestamp indicating when the subscription ended, if applicable. |
| `id` | `string` | Unique identifier for the subscription object. |
| `invoice_settings` | `object` | Settings for invoices generated by this subscription, such as custom fields and footer. |
| `is_deleted` | `boolean` | Indicates whether the subscription has been deleted. |
| `items` | `object` | List of subscription items, each with an attached price defining what the customer is subscribed to. |
| `latest_invoice` | `string` | The most recent invoice this subscription has generated, expandable to full invoice object. |
| `livemode` | `boolean` | Indicates whether the subscription exists in live mode (true) or test mode (false). |
| `metadata` | `object` | Set of key-value pairs that you can attach to the subscription for storing additional structured information. |
| `next_pending_invoice_item_invoice` | `integer` | Timestamp when the next invoice for pending invoice items will be created. |
| `object` | `string` | String representing the object type, always 'subscription'. |
| `on_behalf_of` | `string` | For Connect platforms, the account for which the subscription is being created or managed. |
| `pause_collection` | `object` | Configuration for pausing collection on the subscription while retaining the subscription structure. |
| `payment_settings` | `object` | Payment settings for invoices generated by this subscription. |
| `pending_invoice_item_interval` | `object` | Specifies an interval for aggregating usage records into pending invoice items. |
| `pending_setup_intent` | `string` | SetupIntent used for collecting user authentication when updating payment methods without immediate payment. |
| `pending_update` | `object` | If specified, pending updates that will be applied to the subscription once the latest_invoice has been paid. |
| `plan` | `object` | The plan associated with the subscription (deprecated, use items instead). |
| `quantity` | `integer` | Quantity of the plan subscribed to (deprecated, use items instead). |
| `schedule` | `string` | ID of the subscription schedule managing this subscription's lifecycle, if applicable. |
| `start_date` | `integer` | Timestamp indicating when the subscription started. |
| `status` | `string` | Current status of the subscription (incomplete, incomplete_expired, trialing, active, past_due, canceled, unpaid, or paused). |
| `tax_percent` | `number` | The percentage of tax applied to the subscription (deprecated, use default_tax_rates instead). |
| `test_clock` | `string` | ID of the test clock associated with this subscription for simulating time-based scenarios. |
| `transfer_data` | `object` | For Connect platforms, the account receiving funds from the subscription and optional percentage transferred. |
| `trial_end` | `number` | Timestamp indicating when the trial period ends, if applicable. |
| `trial_settings` | `object` | Settings related to trial periods, including conditions for ending trials. |
| `trial_start` | `integer` | Timestamp indicating when the trial period began, if applicable. |
| `updated` | `integer` | Timestamp indicating when the subscription was last updated. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.application` | `string` | For Connect platforms, the application associated with the subscription. |
| `hits[].data.application_fee_percent` | `number` | For Connect platforms, the percentage of the subscription amount taken as an application fee. |
| `hits[].data.automatic_tax` | `object` | Automatic tax calculation settings for the subscription. |
| `hits[].data.billing` | `string` | Billing mode configuration for the subscription. |
| `hits[].data.billing_cycle_anchor` | `number` | Timestamp determining when the billing cycle for the subscription starts. |
| `hits[].data.billing_cycle_anchor_config` | `object` | Configuration for the subscription's billing cycle anchor behavior. |
| `hits[].data.billing_thresholds` | `object` | Defines thresholds at which an invoice will be sent, controlling billing timing based on usage. |
| `hits[].data.cancel_at` | `number` | Timestamp indicating when the subscription is scheduled to be canceled. |
| `hits[].data.cancel_at_period_end` | `boolean` | Boolean indicating whether the subscription will be canceled at the end of the current billing period. |
| `hits[].data.canceled_at` | `number` | Timestamp indicating when the subscription was canceled, if applicable. |
| `hits[].data.cancellation_details` | `object` | Details about why and how the subscription was canceled. |
| `hits[].data.collection_method` | `string` | How invoices are collected (charge_automatically or send_invoice). |
| `hits[].data.created` | `integer` | Timestamp indicating when the subscription was created. |
| `hits[].data.currency` | `string` | Three-letter ISO currency code in lowercase indicating the currency for the subscription. |
| `hits[].data.current_period_end` | `number` | Timestamp marking the end of the current billing period. |
| `hits[].data.current_period_start` | `integer` | Timestamp marking the start of the current billing period. |
| `hits[].data.customer` | `string` | ID of the customer who owns the subscription, expandable to full customer object. |
| `hits[].data.days_until_due` | `integer` | Number of days until the invoice is due for subscriptions using send_invoice collection method. |
| `hits[].data.default_payment_method` | `string` | ID of the default payment method for the subscription, taking precedence over default_source. |
| `hits[].data.default_source` | `string` | ID of the default payment source for the subscription. |
| `hits[].data.default_tax_rates` | `array` | Tax rates that apply to the subscription by default. |
| `hits[].data.description` | `string` | Human-readable description of the subscription, displayable to the customer. |
| `hits[].data.discount` | `object` | Describes any discount currently applied to the subscription. |
| `hits[].data.ended_at` | `number` | Timestamp indicating when the subscription ended, if applicable. |
| `hits[].data.id` | `string` | Unique identifier for the subscription object. |
| `hits[].data.invoice_settings` | `object` | Settings for invoices generated by this subscription, such as custom fields and footer. |
| `hits[].data.is_deleted` | `boolean` | Indicates whether the subscription has been deleted. |
| `hits[].data.items` | `object` | List of subscription items, each with an attached price defining what the customer is subscribed to. |
| `hits[].data.latest_invoice` | `string` | The most recent invoice this subscription has generated, expandable to full invoice object. |
| `hits[].data.livemode` | `boolean` | Indicates whether the subscription exists in live mode (true) or test mode (false). |
| `hits[].data.metadata` | `object` | Set of key-value pairs that you can attach to the subscription for storing additional structured information. |
| `hits[].data.next_pending_invoice_item_invoice` | `integer` | Timestamp when the next invoice for pending invoice items will be created. |
| `hits[].data.object` | `string` | String representing the object type, always 'subscription'. |
| `hits[].data.on_behalf_of` | `string` | For Connect platforms, the account for which the subscription is being created or managed. |
| `hits[].data.pause_collection` | `object` | Configuration for pausing collection on the subscription while retaining the subscription structure. |
| `hits[].data.payment_settings` | `object` | Payment settings for invoices generated by this subscription. |
| `hits[].data.pending_invoice_item_interval` | `object` | Specifies an interval for aggregating usage records into pending invoice items. |
| `hits[].data.pending_setup_intent` | `string` | SetupIntent used for collecting user authentication when updating payment methods without immediate payment. |
| `hits[].data.pending_update` | `object` | If specified, pending updates that will be applied to the subscription once the latest_invoice has been paid. |
| `hits[].data.plan` | `object` | The plan associated with the subscription (deprecated, use items instead). |
| `hits[].data.quantity` | `integer` | Quantity of the plan subscribed to (deprecated, use items instead). |
| `hits[].data.schedule` | `string` | ID of the subscription schedule managing this subscription's lifecycle, if applicable. |
| `hits[].data.start_date` | `integer` | Timestamp indicating when the subscription started. |
| `hits[].data.status` | `string` | Current status of the subscription (incomplete, incomplete_expired, trialing, active, past_due, canceled, unpaid, or paused). |
| `hits[].data.tax_percent` | `number` | The percentage of tax applied to the subscription (deprecated, use default_tax_rates instead). |
| `hits[].data.test_clock` | `string` | ID of the test clock associated with this subscription for simulating time-based scenarios. |
| `hits[].data.transfer_data` | `object` | For Connect platforms, the account receiving funds from the subscription and optional percentage transferred. |
| `hits[].data.trial_end` | `number` | Timestamp indicating when the trial period ends, if applicable. |
| `hits[].data.trial_settings` | `object` | Settings related to trial periods, including conditions for ending trials. |
| `hits[].data.trial_start` | `integer` | Timestamp indicating when the trial period began, if applicable. |
| `hits[].data.updated` | `integer` | Timestamp indicating when the subscription was last updated. |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Refunds

### Refunds List

Returns a list of all refunds you've previously created. The refunds are returned in sorted order, with the most recent refunds appearing first.

#### Python SDK

```python
await stripe.refunds.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "refunds",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `charge` | `string` | No | Only return refunds for the charge specified by this charge ID |
| `created` | `object` | No | Only return customers that were created during the given date interval. |
| `created.gt` | `integer` | No | Minimum value to filter by (exclusive) |
| `created.gte` | `integer` | No | Minimum value to filter by (inclusive) |
| `created.lt` | `integer` | No | Maximum value to filter by (exclusive) |
| `created.lte` | `integer` | No | Maximum value to filter by (inclusive) |
| `ending_before` | `string` | No | A cursor for use in pagination. ending_before is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj_bar, your subsequent call can include ending_before=obj_bar in order to fetch the previous page of the list. |
| `limit` | `integer` | No | A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10. |
| `payment_intent` | `string` | No | Only return refunds for the PaymentIntent specified by this ID |
| `starting_after` | `string` | No | A cursor for use in pagination. starting_after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include starting_after=obj_foo in order to fetch the next page of the list. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"refund"` |  |
| `amount` | `integer` |  |
| `balance_transaction` | `string \| null` |  |
| `charge` | `string \| null` |  |
| `created` | `integer` |  |
| `currency` | `string` |  |
| `description` | `string \| null` |  |
| `destination_details` | `object \| null` |  |
| `failure_balance_transaction` | `string \| null` |  |
| `failure_reason` | `string \| null` |  |
| `instructions_email` | `string \| null` |  |
| `metadata` | `object \| null` |  |
| `next_action` | `object \| null` |  |
| `payment_intent` | `string \| null` |  |
| `pending_reason` | `string \| null` |  |
| `reason` | `string \| null` |  |
| `receipt_number` | `string \| null` |  |
| `source_transfer_reversal` | `string \| null` |  |
| `status` | `string \| null` |  |
| `transfer_reversal` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

### Refunds Create

When you create a new refund, you must specify a Charge or a PaymentIntent object on which to create it. Creating a new refund will refund a charge that has previously been created but not yet refunded.

#### Python SDK

```python
await stripe.refunds.create()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "refunds",
    "action": "create"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"refund"` |  |
| `amount` | `integer` |  |
| `balance_transaction` | `string \| null` |  |
| `charge` | `string \| null` |  |
| `created` | `integer` |  |
| `currency` | `string` |  |
| `description` | `string \| null` |  |
| `destination_details` | `object \| null` |  |
| `failure_balance_transaction` | `string \| null` |  |
| `failure_reason` | `string \| null` |  |
| `instructions_email` | `string \| null` |  |
| `metadata` | `object \| null` |  |
| `next_action` | `object \| null` |  |
| `payment_intent` | `string \| null` |  |
| `pending_reason` | `string \| null` |  |
| `reason` | `string \| null` |  |
| `receipt_number` | `string \| null` |  |
| `source_transfer_reversal` | `string \| null` |  |
| `status` | `string \| null` |  |
| `transfer_reversal` | `string \| null` |  |


</details>

### Refunds Get

Retrieves the details of an existing refund

#### Python SDK

```python
await stripe.refunds.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "refunds",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The refund ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"refund"` |  |
| `amount` | `integer` |  |
| `balance_transaction` | `string \| null` |  |
| `charge` | `string \| null` |  |
| `created` | `integer` |  |
| `currency` | `string` |  |
| `description` | `string \| null` |  |
| `destination_details` | `object \| null` |  |
| `failure_balance_transaction` | `string \| null` |  |
| `failure_reason` | `string \| null` |  |
| `instructions_email` | `string \| null` |  |
| `metadata` | `object \| null` |  |
| `next_action` | `object \| null` |  |
| `payment_intent` | `string \| null` |  |
| `pending_reason` | `string \| null` |  |
| `reason` | `string \| null` |  |
| `receipt_number` | `string \| null` |  |
| `source_transfer_reversal` | `string \| null` |  |
| `status` | `string \| null` |  |
| `transfer_reversal` | `string \| null` |  |


</details>

### Refunds Search

Search and filter refunds records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await stripe.refunds.search(
    query={"filter": {"eq": {"amount": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "refunds",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"amount": 0}}}
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
| `amount` | `integer` | Amount refunded, in cents (the smallest currency unit). |
| `balance_transaction` | `string` | ID of the balance transaction that describes the impact of this refund on your account balance. |
| `charge` | `string` | ID of the charge that was refunded. |
| `created` | `integer` | Timestamp indicating when the refund was created. |
| `currency` | `string` | Three-letter ISO currency code in lowercase representing the currency of the refund. |
| `destination_details` | `object` | Details about the destination where the refunded funds should be sent. |
| `id` | `string` | Unique identifier for the refund object. |
| `metadata` | `object` | Set of key-value pairs that you can attach to an object for storing additional structured information. |
| `object` | `string` | String representing the object type, always 'refund'. |
| `payment_intent` | `string` | ID of the PaymentIntent that was refunded. |
| `reason` | `string` | Reason for the refund, either user-provided (duplicate, fraudulent, or requested_by_customer) or generated by Stripe internally (expired_uncaptured_charge). |
| `receipt_number` | `string` | The transaction number that appears on email receipts sent for this refund. |
| `source_transfer_reversal` | `string` | ID of the transfer reversal that was created as a result of refunding a transfer (Connect only). |
| `status` | `string` | Status of the refund (pending, requires_action, succeeded, failed, or canceled). |
| `transfer_reversal` | `string` | ID of the reversal of the transfer that funded the charge being refunded (Connect only). |
| `updated` | `integer` | Timestamp indicating when the refund was last updated. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.amount` | `integer` | Amount refunded, in cents (the smallest currency unit). |
| `hits[].data.balance_transaction` | `string` | ID of the balance transaction that describes the impact of this refund on your account balance. |
| `hits[].data.charge` | `string` | ID of the charge that was refunded. |
| `hits[].data.created` | `integer` | Timestamp indicating when the refund was created. |
| `hits[].data.currency` | `string` | Three-letter ISO currency code in lowercase representing the currency of the refund. |
| `hits[].data.destination_details` | `object` | Details about the destination where the refunded funds should be sent. |
| `hits[].data.id` | `string` | Unique identifier for the refund object. |
| `hits[].data.metadata` | `object` | Set of key-value pairs that you can attach to an object for storing additional structured information. |
| `hits[].data.object` | `string` | String representing the object type, always 'refund'. |
| `hits[].data.payment_intent` | `string` | ID of the PaymentIntent that was refunded. |
| `hits[].data.reason` | `string` | Reason for the refund, either user-provided (duplicate, fraudulent, or requested_by_customer) or generated by Stripe internally (expired_uncaptured_charge). |
| `hits[].data.receipt_number` | `string` | The transaction number that appears on email receipts sent for this refund. |
| `hits[].data.source_transfer_reversal` | `string` | ID of the transfer reversal that was created as a result of refunding a transfer (Connect only). |
| `hits[].data.status` | `string` | Status of the refund (pending, requires_action, succeeded, failed, or canceled). |
| `hits[].data.transfer_reversal` | `string` | ID of the reversal of the transfer that funded the charge being refunded (Connect only). |
| `hits[].data.updated` | `integer` | Timestamp indicating when the refund was last updated. |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Products

### Products List

Returns a list of your products. The products are returned sorted by creation date, with the most recent products appearing first.

#### Python SDK

```python
await stripe.products.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "products",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `active` | `boolean` | No | Only return products that are active or inactive |
| `created` | `object` | No | Only return products that were created during the given date interval. |
| `created.gt` | `integer` | No | Minimum value to filter by (exclusive) |
| `created.gte` | `integer` | No | Minimum value to filter by (inclusive) |
| `created.lt` | `integer` | No | Maximum value to filter by (exclusive) |
| `created.lte` | `integer` | No | Maximum value to filter by (inclusive) |
| `ending_before` | `string` | No | A cursor for use in pagination. ending_before is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj_bar, your subsequent call can include ending_before=obj_bar in order to fetch the previous page of the list. |
| `ids` | `array<string>` | No | Only return products with the given IDs |
| `limit` | `integer` | No | A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10. |
| `shippable` | `boolean` | No | Only return products that can be shipped |
| `starting_after` | `string` | No | A cursor for use in pagination. starting_after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include starting_after=obj_foo in order to fetch the next page of the list. |
| `url` | `string` | No | Only return products with the given url |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"product"` |  |
| `active` | `boolean` |  |
| `attributes` | `array<string>` |  |
| `created` | `integer` |  |
| `default_price` | `string \| null` |  |
| `description` | `string \| null` |  |
| `features` | `array<object>` |  |
| `images` | `array<string>` |  |
| `livemode` | `boolean` |  |
| `marketing_features` | `array<object>` |  |
| `metadata` | `object` |  |
| `name` | `string` |  |
| `package_dimensions` | `object \| null` |  |
| `shippable` | `boolean \| null` |  |
| `statement_descriptor` | `string \| null` |  |
| `tax_code` | `string \| null` |  |
| `type` | `"good" \| "service"` |  |
| `unit_label` | `string \| null` |  |
| `updated` | `integer` |  |
| `url` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

### Products Create

Creates a new product object. Your product's name, description, and other information will be displayed in all product and invoice displays.

#### Python SDK

```python
await stripe.products.create()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "products",
    "action": "create"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"product"` |  |
| `active` | `boolean` |  |
| `attributes` | `array<string>` |  |
| `created` | `integer` |  |
| `default_price` | `string \| null` |  |
| `description` | `string \| null` |  |
| `features` | `array<object>` |  |
| `images` | `array<string>` |  |
| `livemode` | `boolean` |  |
| `marketing_features` | `array<object>` |  |
| `metadata` | `object` |  |
| `name` | `string` |  |
| `package_dimensions` | `object \| null` |  |
| `shippable` | `boolean \| null` |  |
| `statement_descriptor` | `string \| null` |  |
| `tax_code` | `string \| null` |  |
| `type` | `"good" \| "service"` |  |
| `unit_label` | `string \| null` |  |
| `updated` | `integer` |  |
| `url` | `string \| null` |  |


</details>

### Products Get

Retrieves the details of an existing product. Supply the unique product ID and Stripe will return the corresponding product information.

#### Python SDK

```python
await stripe.products.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "products",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The product ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"product"` |  |
| `active` | `boolean` |  |
| `attributes` | `array<string>` |  |
| `created` | `integer` |  |
| `default_price` | `string \| null` |  |
| `description` | `string \| null` |  |
| `features` | `array<object>` |  |
| `images` | `array<string>` |  |
| `livemode` | `boolean` |  |
| `marketing_features` | `array<object>` |  |
| `metadata` | `object` |  |
| `name` | `string` |  |
| `package_dimensions` | `object \| null` |  |
| `shippable` | `boolean \| null` |  |
| `statement_descriptor` | `string \| null` |  |
| `tax_code` | `string \| null` |  |
| `type` | `"good" \| "service"` |  |
| `unit_label` | `string \| null` |  |
| `updated` | `integer` |  |
| `url` | `string \| null` |  |


</details>

### Products Update

Updates the specific product by setting the values of the parameters passed. Any parameters not provided will be left unchanged.

#### Python SDK

```python
await stripe.products.update(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "products",
    "action": "update",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The product ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"product"` |  |
| `active` | `boolean` |  |
| `attributes` | `array<string>` |  |
| `created` | `integer` |  |
| `default_price` | `string \| null` |  |
| `description` | `string \| null` |  |
| `features` | `array<object>` |  |
| `images` | `array<string>` |  |
| `livemode` | `boolean` |  |
| `marketing_features` | `array<object>` |  |
| `metadata` | `object` |  |
| `name` | `string` |  |
| `package_dimensions` | `object \| null` |  |
| `shippable` | `boolean \| null` |  |
| `statement_descriptor` | `string \| null` |  |
| `tax_code` | `string \| null` |  |
| `type` | `"good" \| "service"` |  |
| `unit_label` | `string \| null` |  |
| `updated` | `integer` |  |
| `url` | `string \| null` |  |


</details>

### Products Delete

Deletes a product. Deleting a product is only possible if it has no prices associated with it.

#### Python SDK

```python
await stripe.products.delete(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "products",
    "action": "delete",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The product ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"product"` |  |
| `deleted` | `boolean` |  |


</details>

### Products API Search

Search for products using Stripe's Search Query Language.

#### Python SDK

```python
await stripe.products.api_search(
    query="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "products",
    "action": "api_search",
    "params": {
        "query": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | Yes | The search query string using Stripe's Search Query Language |
| `limit` | `integer` | No | A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10. |
| `page` | `string` | No | A cursor for pagination across multiple pages of results. Don't include this parameter on the first call. Use the next_page value returned in a previous response to request subsequent results. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"product"` |  |
| `active` | `boolean` |  |
| `attributes` | `array<string>` |  |
| `created` | `integer` |  |
| `default_price` | `string \| null` |  |
| `description` | `string \| null` |  |
| `features` | `array<object>` |  |
| `images` | `array<string>` |  |
| `livemode` | `boolean` |  |
| `marketing_features` | `array<object>` |  |
| `metadata` | `object` |  |
| `name` | `string` |  |
| `package_dimensions` | `object \| null` |  |
| `shippable` | `boolean \| null` |  |
| `statement_descriptor` | `string \| null` |  |
| `tax_code` | `string \| null` |  |
| `type` | `"good" \| "service"` |  |
| `unit_label` | `string \| null` |  |
| `updated` | `integer` |  |
| `url` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

## Balance

### Balance Get

Retrieves the current account balance, based on the authentication that was used to make the request.

#### Python SDK

```python
await stripe.balance.get()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "balance",
    "action": "get"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `object` | `"balance"` |  |
| `livemode` | `boolean` |  |
| `available` | `array<object>` |  |
| `connect_reserved` | `array \| null` |  |
| `instant_available` | `array \| null` |  |
| `issuing` | `object \| null` |  |
| `pending` | `array<object>` |  |
| `refund_and_dispute_prefunding` | `object \| null` |  |


</details>

## Balance Transactions

### Balance Transactions List

Returns a list of transactions that have contributed to the Stripe account balance (e.g., charges, transfers, and so forth). The transactions are returned in sorted order, with the most recent transactions appearing first.

#### Python SDK

```python
await stripe.balance_transactions.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "balance_transactions",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `created` | `object` | No | Only return transactions that were created during the given date interval. |
| `created.gt` | `integer` | No | Minimum value to filter by (exclusive) |
| `created.gte` | `integer` | No | Minimum value to filter by (inclusive) |
| `created.lt` | `integer` | No | Maximum value to filter by (exclusive) |
| `created.lte` | `integer` | No | Maximum value to filter by (inclusive) |
| `currency` | `string` | No | Only return transactions in a certain currency. Three-letter ISO currency code, in lowercase. |
| `ending_before` | `string` | No | A cursor for use in pagination. ending_before is an object ID that defines your place in the list. |
| `limit` | `integer` | No | A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10. |
| `payout` | `string` | No | For automatic Stripe payouts only, only returns transactions that were paid out on the specified payout ID. |
| `source` | `string` | No | Only returns the original transaction. |
| `starting_after` | `string` | No | A cursor for use in pagination. starting_after is an object ID that defines your place in the list. |
| `type` | `string` | No | Only returns transactions of the given type. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"balance_transaction"` |  |
| `amount` | `integer` |  |
| `available_on` | `integer` |  |
| `balance_type` | `"issuing" \| "payments" \| "refund_and_dispute_prefunding"` |  |
| `created` | `integer` |  |
| `currency` | `string` |  |
| `description` | `string \| null` |  |
| `exchange_rate` | `number \| null` |  |
| `fee` | `integer` |  |
| `fee_details` | `array<object>` |  |
| `net` | `integer` |  |
| `reporting_category` | `string` |  |
| `source` | `string \| null` |  |
| `status` | `"available" \| "pending"` |  |
| `type` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

### Balance Transactions Get

Retrieves the balance transaction with the given ID.

#### Python SDK

```python
await stripe.balance_transactions.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "balance_transactions",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the desired balance transaction |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"balance_transaction"` |  |
| `amount` | `integer` |  |
| `available_on` | `integer` |  |
| `balance_type` | `"issuing" \| "payments" \| "refund_and_dispute_prefunding"` |  |
| `created` | `integer` |  |
| `currency` | `string` |  |
| `description` | `string \| null` |  |
| `exchange_rate` | `number \| null` |  |
| `fee` | `integer` |  |
| `fee_details` | `array<object>` |  |
| `net` | `integer` |  |
| `reporting_category` | `string` |  |
| `source` | `string \| null` |  |
| `status` | `"available" \| "pending"` |  |
| `type` | `string` |  |


</details>

## Payment Intents

### Payment Intents List

Returns a list of PaymentIntents. The payment intents are returned sorted by creation date, with the most recent payment intents appearing first.

#### Python SDK

```python
await stripe.payment_intents.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "payment_intents",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `created` | `object` | No | Only return payment intents that were created during the given date interval. |
| `created.gt` | `integer` | No | Minimum value to filter by (exclusive) |
| `created.gte` | `integer` | No | Minimum value to filter by (inclusive) |
| `created.lt` | `integer` | No | Maximum value to filter by (exclusive) |
| `created.lte` | `integer` | No | Maximum value to filter by (inclusive) |
| `customer` | `string` | No | Only return payment intents for the customer specified by this customer ID |
| `customer_account` | `string` | No | Only return payment intents for the account specified by this account ID |
| `ending_before` | `string` | No | A cursor for use in pagination. ending_before is an object ID that defines your place in the list. |
| `limit` | `integer` | No | A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10. |
| `starting_after` | `string` | No | A cursor for use in pagination. starting_after is an object ID that defines your place in the list. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"payment_intent"` |  |
| `amount` | `integer` |  |
| `amount_capturable` | `integer` |  |
| `amount_received` | `integer` |  |
| `application` | `string \| null` |  |
| `application_fee_amount` | `integer \| null` |  |
| `capture_method` | `"automatic" \| "automatic_async" \| "manual"` |  |
| `client_secret` | `string \| null` |  |
| `confirmation_method` | `"automatic" \| "manual"` |  |
| `created` | `integer` |  |
| `currency` | `string` |  |
| `customer` | `string \| null` |  |
| `description` | `string \| null` |  |
| `livemode` | `boolean` |  |
| `metadata` | `object` |  |
| `payment_method` | `string \| null` |  |
| `payment_method_types` | `array<string>` |  |
| `status` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

### Payment Intents Get

Retrieves the details of a PaymentIntent that has previously been created.

#### Python SDK

```python
await stripe.payment_intents.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "payment_intents",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the payment intent |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"payment_intent"` |  |
| `amount` | `integer` |  |
| `amount_capturable` | `integer` |  |
| `amount_received` | `integer` |  |
| `application` | `string \| null` |  |
| `application_fee_amount` | `integer \| null` |  |
| `capture_method` | `"automatic" \| "automatic_async" \| "manual"` |  |
| `client_secret` | `string \| null` |  |
| `confirmation_method` | `"automatic" \| "manual"` |  |
| `created` | `integer` |  |
| `currency` | `string` |  |
| `customer` | `string \| null` |  |
| `description` | `string \| null` |  |
| `livemode` | `boolean` |  |
| `metadata` | `object` |  |
| `payment_method` | `string \| null` |  |
| `payment_method_types` | `array<string>` |  |
| `status` | `string` |  |


</details>

### Payment Intents API Search

Search for payment intents using Stripe's Search Query Language.

#### Python SDK

```python
await stripe.payment_intents.api_search(
    query="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "payment_intents",
    "action": "api_search",
    "params": {
        "query": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | Yes | The search query string using Stripe's Search Query Language |
| `limit` | `integer` | No | A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10. |
| `page` | `string` | No | A cursor for pagination across multiple pages of results. Don't include this parameter on the first call. Use the next_page value returned in a previous response to request subsequent results. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"payment_intent"` |  |
| `amount` | `integer` |  |
| `amount_capturable` | `integer` |  |
| `amount_received` | `integer` |  |
| `application` | `string \| null` |  |
| `application_fee_amount` | `integer \| null` |  |
| `capture_method` | `"automatic" \| "automatic_async" \| "manual"` |  |
| `client_secret` | `string \| null` |  |
| `confirmation_method` | `"automatic" \| "manual"` |  |
| `created` | `integer` |  |
| `currency` | `string` |  |
| `customer` | `string \| null` |  |
| `description` | `string \| null` |  |
| `livemode` | `boolean` |  |
| `metadata` | `object` |  |
| `payment_method` | `string \| null` |  |
| `payment_method_types` | `array<string>` |  |
| `status` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

## Disputes

### Disputes List

Returns a list of your disputes. The disputes are returned sorted by creation date, with the most recent disputes appearing first.

#### Python SDK

```python
await stripe.disputes.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "disputes",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `charge` | `string` | No | Only return disputes associated to the charge specified by this charge ID |
| `created` | `object` | No | Only return disputes that were created during the given date interval. |
| `created.gt` | `integer` | No | Minimum value to filter by (exclusive) |
| `created.gte` | `integer` | No | Minimum value to filter by (inclusive) |
| `created.lt` | `integer` | No | Maximum value to filter by (exclusive) |
| `created.lte` | `integer` | No | Maximum value to filter by (inclusive) |
| `ending_before` | `string` | No | A cursor for use in pagination. ending_before is an object ID that defines your place in the list. |
| `limit` | `integer` | No | A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10. |
| `payment_intent` | `string` | No | Only return disputes associated to the PaymentIntent specified by this PaymentIntent ID |
| `starting_after` | `string` | No | A cursor for use in pagination. starting_after is an object ID that defines your place in the list. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"dispute"` |  |
| `amount` | `integer` |  |
| `balance_transactions` | `array<object>` |  |
| `charge` | `string` |  |
| `created` | `integer` |  |
| `currency` | `string` |  |
| `enhanced_eligibility_types` | `array<string>` |  |
| `evidence` | `object` |  |
| `evidence_details` | `object` |  |
| `is_charge_refundable` | `boolean` |  |
| `livemode` | `boolean` |  |
| `metadata` | `object` |  |
| `payment_intent` | `string \| null` |  |
| `payment_method_details` | `object \| null` |  |
| `reason` | `string` |  |
| `status` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

### Disputes Get

Retrieves the dispute with the given ID.

#### Python SDK

```python
await stripe.disputes.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "disputes",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the dispute |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"dispute"` |  |
| `amount` | `integer` |  |
| `balance_transactions` | `array<object>` |  |
| `charge` | `string` |  |
| `created` | `integer` |  |
| `currency` | `string` |  |
| `enhanced_eligibility_types` | `array<string>` |  |
| `evidence` | `object` |  |
| `evidence_details` | `object` |  |
| `is_charge_refundable` | `boolean` |  |
| `livemode` | `boolean` |  |
| `metadata` | `object` |  |
| `payment_intent` | `string \| null` |  |
| `payment_method_details` | `object \| null` |  |
| `reason` | `string` |  |
| `status` | `string` |  |


</details>

## Payouts

### Payouts List

Returns a list of existing payouts sent to third-party bank accounts or payouts that Stripe sent to you. The payouts return in sorted order, with the most recently created payouts appearing first.

#### Python SDK

```python
await stripe.payouts.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "payouts",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `arrival_date` | `object` | No | Filter payouts by expected arrival date range. |
| `arrival_date.gt` | `integer` | No | Minimum value to filter by (exclusive) |
| `arrival_date.gte` | `integer` | No | Minimum value to filter by (inclusive) |
| `arrival_date.lt` | `integer` | No | Maximum value to filter by (exclusive) |
| `arrival_date.lte` | `integer` | No | Maximum value to filter by (inclusive) |
| `created` | `object` | No | Only return payouts that were created during the given date interval. |
| `created.gt` | `integer` | No | Minimum value to filter by (exclusive) |
| `created.gte` | `integer` | No | Minimum value to filter by (inclusive) |
| `created.lt` | `integer` | No | Maximum value to filter by (exclusive) |
| `created.lte` | `integer` | No | Maximum value to filter by (inclusive) |
| `destination` | `string` | No | The ID of the external account the payout was sent to. |
| `ending_before` | `string` | No | A cursor for use in pagination. ending_before is an object ID that defines your place in the list. |
| `limit` | `integer` | No | A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10. |
| `starting_after` | `string` | No | A cursor for use in pagination. starting_after is an object ID that defines your place in the list. |
| `status` | `"pending" \| "paid" \| "failed" \| "canceled"` | No | Only return payouts that have the given status |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"payout"` |  |
| `amount` | `integer` |  |
| `application_fee` | `string \| null` |  |
| `application_fee_amount` | `integer \| null` |  |
| `arrival_date` | `integer` |  |
| `automatic` | `boolean` |  |
| `balance_transaction` | `string \| null` |  |
| `created` | `integer` |  |
| `currency` | `string` |  |
| `description` | `string \| null` |  |
| `destination` | `string \| null` |  |
| `failure_balance_transaction` | `string \| null` |  |
| `failure_code` | `string \| null` |  |
| `failure_message` | `string \| null` |  |
| `livemode` | `boolean` |  |
| `metadata` | `object` |  |
| `method` | `"standard" \| "instant"` |  |
| `original_payout` | `string \| null` |  |
| `payout_method` | `string \| null` |  |
| `reconciliation_status` | `string` |  |
| `reversed_by` | `string \| null` |  |
| `source_balance` | `string \| null` |  |
| `source_type` | `string` |  |
| `statement_descriptor` | `string \| null` |  |
| `status` | `string` |  |
| `trace_id` | `object \| null` |  |
| `type` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

### Payouts Get

Retrieves the details of an existing payout. Supply the unique payout ID from either a payout creation request or the payout list, and Stripe will return the corresponding payout information.

#### Python SDK

```python
await stripe.payouts.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "payouts",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the payout |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `"payout"` |  |
| `amount` | `integer` |  |
| `application_fee` | `string \| null` |  |
| `application_fee_amount` | `integer \| null` |  |
| `arrival_date` | `integer` |  |
| `automatic` | `boolean` |  |
| `balance_transaction` | `string \| null` |  |
| `created` | `integer` |  |
| `currency` | `string` |  |
| `description` | `string \| null` |  |
| `destination` | `string \| null` |  |
| `failure_balance_transaction` | `string \| null` |  |
| `failure_code` | `string \| null` |  |
| `failure_message` | `string \| null` |  |
| `livemode` | `boolean` |  |
| `metadata` | `object` |  |
| `method` | `"standard" \| "instant"` |  |
| `original_payout` | `string \| null` |  |
| `payout_method` | `string \| null` |  |
| `reconciliation_status` | `string` |  |
| `reversed_by` | `string \| null` |  |
| `source_balance` | `string \| null` |  |
| `source_type` | `string` |  |
| `statement_descriptor` | `string \| null` |  |
| `status` | `string` |  |
| `trace_id` | `object \| null` |  |
| `type` | `string` |  |


</details>

