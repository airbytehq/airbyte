# Stripe

## Supported Entities and Actions

| Entity | Actions |
|--------|---------|
| Customers | [List](#customers-list), [Get](#customers-get), [Search](#customers-search) |
| Invoices | [List](#invoices-list), [Get](#invoices-get), [Search](#invoices-search) |
| Charges | [List](#charges-list), [Get](#charges-get), [Search](#charges-search) |
| Subscriptions | [List](#subscriptions-list), [Get](#subscriptions-get), [Search](#subscriptions-search) |
| Refunds | [List](#refunds-list), [Get](#refunds-get) |
| Products | [List](#products-list), [Get](#products-get), [Search](#products-search) |
| Balance | [Get](#balance-get) |
| Balance Transactions | [List](#balance-transactions-list), [Get](#balance-transactions-get) |
| Payment Intents | [List](#payment-intents-list), [Get](#payment-intents-get), [Search](#payment-intents-search) |
| Disputes | [List](#disputes-list), [Get](#disputes-get) |
| Payouts | [List](#payouts-list), [Get](#payouts-get) |

### Customers

#### Customers List

Returns a list of your customers. The customers are returned sorted by creation date, with the most recent customers appearing first.

**Python SDK**

```python
stripe.customers.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "customers",
    "action": "list"
}'
```


**Params**

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

**Records**

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


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

#### Customers Get

Retrieves a Customer object.

**Python SDK**

```python
stripe.customers.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The customer ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

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

#### Customers Search

Search for customers using Stripe's Search Query Language.

**Python SDK**

```python
stripe.customers.search(
    query="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "customers",
    "action": "search",
    "params": {
        "query": "<str>"
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | Yes | The search query string using Stripe's Search Query Language |
| `limit` | `integer` | No | A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10. |
| `page` | `string` | No | A cursor for pagination across multiple pages of results. Don’t include this parameter on the first call. Use the next_page value returned in a previous response to request subsequent results. |


<details>
<summary><b>Response Schema</b></summary>

**Records**

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


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

### Invoices

#### Invoices List

Returns a list of invoices

**Python SDK**

```python
stripe.invoices.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "invoices",
    "action": "list"
}'
```


**Params**

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

**Records**

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


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

#### Invoices Get

Retrieves the invoice with the given ID

**Python SDK**

```python
stripe.invoices.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The invoice ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

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

#### Invoices Search

Search for invoices using Stripe's Search Query Language

**Python SDK**

```python
stripe.invoices.search(
    query="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "invoices",
    "action": "search",
    "params": {
        "query": "<str>"
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | Yes | The search query string using Stripe's Search Query Language |
| `limit` | `integer` | No | A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10. |
| `page` | `string` | No | A cursor for pagination across multiple pages of results. Don’t include this parameter on the first call. Use the next_page value returned in a previous response to request subsequent results. |


<details>
<summary><b>Response Schema</b></summary>

**Records**

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

### Charges

#### Charges List

Returns a list of charges you've previously created. The charges are returned in sorted order, with the most recent charges appearing first.

**Python SDK**

```python
stripe.charges.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "charges",
    "action": "list"
}'
```


**Params**

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

**Records**

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


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

#### Charges Get

Retrieves the details of a charge that has previously been created

**Python SDK**

```python
stripe.charges.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The charge ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

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

#### Charges Search

Search for charges using Stripe's Search Query Language

**Python SDK**

```python
stripe.charges.search(
    query="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "charges",
    "action": "search",
    "params": {
        "query": "<str>"
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | Yes | The search query string using Stripe's Search Query Language |
| `limit` | `integer` | No | A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10. |
| `page` | `string` | No | A cursor for pagination across multiple pages of results. Don’t include this parameter on the first call. Use the next_page value returned in a previous response to request subsequent results. |


<details>
<summary><b>Response Schema</b></summary>

**Records**

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

### Subscriptions

#### Subscriptions List

By default, returns a list of subscriptions that have not been canceled

**Python SDK**

```python
stripe.subscriptions.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "subscriptions",
    "action": "list"
}'
```


**Params**

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

**Records**

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


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

#### Subscriptions Get

Retrieves the subscription with the given ID

**Python SDK**

```python
stripe.subscriptions.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The subscription ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

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

#### Subscriptions Search

Search for subscriptions using Stripe's Search Query Language

**Python SDK**

```python
stripe.subscriptions.search(
    query="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "subscriptions",
    "action": "search",
    "params": {
        "query": "<str>"
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | Yes | The search query string using Stripe's Search Query Language |
| `limit` | `integer` | No | A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10. |
| `page` | `string` | No | A cursor for pagination across multiple pages of results. Don't include this parameter on the first call. Use the next_page value returned in a previous response to request subsequent results. |


<details>
<summary><b>Response Schema</b></summary>

**Records**

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

### Refunds

#### Refunds List

Returns a list of all refunds you've previously created. The refunds are returned in sorted order, with the most recent refunds appearing first.

**Python SDK**

```python
stripe.refunds.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "refunds",
    "action": "list"
}'
```


**Params**

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

**Records**

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


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

#### Refunds Get

Retrieves the details of an existing refund

**Python SDK**

```python
stripe.refunds.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The refund ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

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

### Products

#### Products List

Returns a list of your products. The products are returned sorted by creation date, with the most recent products appearing first.

**Python SDK**

```python
stripe.products.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "products",
    "action": "list"
}'
```


**Params**

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

**Records**

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


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

#### Products Get

Retrieves the details of an existing product. Supply the unique product ID and Stripe will return the corresponding product information.

**Python SDK**

```python
stripe.products.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The product ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

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

#### Products Search

Search for products using Stripe's Search Query Language.

**Python SDK**

```python
stripe.products.search(
    query="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "products",
    "action": "search",
    "params": {
        "query": "<str>"
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | Yes | The search query string using Stripe's Search Query Language |
| `limit` | `integer` | No | A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10. |
| `page` | `string` | No | A cursor for pagination across multiple pages of results. Don't include this parameter on the first call. Use the next_page value returned in a previous response to request subsequent results. |


<details>
<summary><b>Response Schema</b></summary>

**Records**

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


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

### Balance

#### Balance Get

Retrieves the current account balance, based on the authentication that was used to make the request.

**Python SDK**

```python
stripe.balance.get()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "balance",
    "action": "get"
}'
```



<details>
<summary><b>Response Schema</b></summary>

**Records**

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

### Balance Transactions

#### Balance Transactions List

Returns a list of transactions that have contributed to the Stripe account balance (e.g., charges, transfers, and so forth). The transactions are returned in sorted order, with the most recent transactions appearing first.

**Python SDK**

```python
stripe.balance_transactions.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "balance_transactions",
    "action": "list"
}'
```


**Params**

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

**Records**

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


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

#### Balance Transactions Get

Retrieves the balance transaction with the given ID.

**Python SDK**

```python
stripe.balance_transactions.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the desired balance transaction |


<details>
<summary><b>Response Schema</b></summary>

**Records**

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

### Payment Intents

#### Payment Intents List

Returns a list of PaymentIntents. The payment intents are returned sorted by creation date, with the most recent payment intents appearing first.

**Python SDK**

```python
stripe.payment_intents.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "payment_intents",
    "action": "list"
}'
```


**Params**

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

**Records**

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


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

#### Payment Intents Get

Retrieves the details of a PaymentIntent that has previously been created.

**Python SDK**

```python
stripe.payment_intents.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the payment intent |


<details>
<summary><b>Response Schema</b></summary>

**Records**

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

#### Payment Intents Search

Search for payment intents using Stripe's Search Query Language.

**Python SDK**

```python
stripe.payment_intents.search(
    query="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "payment_intents",
    "action": "search",
    "params": {
        "query": "<str>"
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | Yes | The search query string using Stripe's Search Query Language |
| `limit` | `integer` | No | A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10. |
| `page` | `string` | No | A cursor for pagination across multiple pages of results. Don't include this parameter on the first call. Use the next_page value returned in a previous response to request subsequent results. |


<details>
<summary><b>Response Schema</b></summary>

**Records**

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


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

### Disputes

#### Disputes List

Returns a list of your disputes. The disputes are returned sorted by creation date, with the most recent disputes appearing first.

**Python SDK**

```python
stripe.disputes.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "disputes",
    "action": "list"
}'
```


**Params**

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

**Records**

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


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

#### Disputes Get

Retrieves the dispute with the given ID.

**Python SDK**

```python
stripe.disputes.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the dispute |


<details>
<summary><b>Response Schema</b></summary>

**Records**

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

### Payouts

#### Payouts List

Returns a list of existing payouts sent to third-party bank accounts or payouts that Stripe sent to you. The payouts return in sorted order, with the most recently created payouts appearing first.

**Python SDK**

```python
stripe.payouts.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "payouts",
    "action": "list"
}'
```


**Params**

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

**Records**

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


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `has_more` | `boolean` |  |

</details>

#### Payouts Get

Retrieves the details of an existing payout. Supply the unique payout ID from either a payout creation request or the payout list, and Stripe will return the corresponding payout information.

**Python SDK**

```python
stripe.payouts.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the payout |


<details>
<summary><b>Response Schema</b></summary>

**Records**

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



## Authentication

The Stripe connector supports the following authentication methods:


### API Key Authentication

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `api_key` | `str` | Yes | Your Stripe API Key (starts with sk_test_ or sk_live_) |

#### Example

**Python SDK**

```python
StripeConnector(
  auth_config=StripeAuthConfig(
    api_key="<Your Stripe API Key (starts with sk_test_ or sk_live_)>"
  )
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
  "connector_definition_id": "e094cb9a-26de-4645-8761-65c0c425d1de",
  "auth_config": {
    "api_key": "<Your Stripe API Key (starts with sk_test_ or sk_live_)>"
  },
  "name": "My Stripe Connector"
}'
```

