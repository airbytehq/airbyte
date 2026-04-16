# Chargebee full reference

This is the full reference documentation for the Chargebee agent connector.

## Supported entities and actions

The Chargebee connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Customer | [List](#customer-list), [Get](#customer-get), [Search](#customer-search) |
| Subscription | [List](#subscription-list), [Get](#subscription-get), [Search](#subscription-search) |
| Invoice | [List](#invoice-list), [Get](#invoice-get), [Search](#invoice-search) |
| Credit Note | [List](#credit-note-list), [Get](#credit-note-get), [Search](#credit-note-search) |
| Coupon | [List](#coupon-list), [Get](#coupon-get), [Search](#coupon-search) |
| Transaction | [List](#transaction-list), [Get](#transaction-get), [Search](#transaction-search) |
| Event | [List](#event-list), [Get](#event-get), [Search](#event-search) |
| Order | [List](#order-list), [Get](#order-get), [Search](#order-search) |
| Item | [List](#item-list), [Get](#item-get), [Search](#item-search) |
| Item Price | [List](#item-price-list), [Get](#item-price-get), [Search](#item-price-search) |
| Payment Source | [List](#payment-source-list), [Get](#payment-source-get), [Search](#payment-source-search) |

## Customer

### Customer List

List customers

#### Python SDK

```python
await chargebee.customer.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "customer",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Number of items to return (max 100) |
| `offset` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `first_name` | `string` |  |
| `last_name` | `string` |  |
| `email` | `string` |  |
| `phone` | `string` |  |
| `company` | `string` |  |
| `vat_number` | `string` |  |
| `auto_collection` | `string` |  |
| `offline_payment_method` | `string` |  |
| `net_term_days` | `integer` |  |
| `vat_number_validated_time` | `integer` |  |
| `vat_number_status` | `string` |  |
| `allow_direct_debit` | `boolean` |  |
| `is_location_valid` | `boolean` |  |
| `created_at` | `integer` |  |
| `created_from_ip` | `string` |  |
| `taxability` | `string` |  |
| `entity_code` | `string` |  |
| `exempt_number` | `string` |  |
| `resource_version` | `integer` |  |
| `updated_at` | `integer` |  |
| `locale` | `string` |  |
| `billing_date` | `integer` |  |
| `billing_date_mode` | `string` |  |
| `billing_day_of_week` | `string` |  |
| `billing_day_of_week_mode` | `string` |  |
| `billing_month` | `integer` |  |
| `pii_cleared` | `string` |  |
| `auto_close_invoices` | `boolean` |  |
| `channel` | `string` |  |
| `fraud_flag` | `string` |  |
| `primary_payment_source_id` | `string` |  |
| `backup_payment_source_id` | `string` |  |
| `invoice_notes` | `string` |  |
| `business_entity_id` | `string` |  |
| `preferred_currency_code` | `string` |  |
| `promotional_credits` | `integer` |  |
| `unbilled_charges` | `integer` |  |
| `refundable_credits` | `integer` |  |
| `excess_payments` | `integer` |  |
| `deleted` | `boolean` |  |
| `registered_for_gst` | `boolean` |  |
| `consolidated_invoicing` | `boolean` |  |
| `customer_type` | `string` |  |
| `business_customer_without_vat_number` | `boolean` |  |
| `client_profile_id` | `string` |  |
| `use_default_hierarchy_settings` | `boolean` |  |
| `vat_number_prefix` | `string` |  |
| `billing_address` | `object` |  |
| `referral_urls` | `array<object>` |  |
| `contacts` | `array<object>` |  |
| `payment_method` | `object` |  |
| `balances` | `array<object>` |  |
| `relationship` | `object` |  |
| `parent_account_access` | `object` |  |
| `child_account_access` | `object` |  |
| `meta_data` | `object` |  |
| `mrr` | `integer` |  |
| `exemption_details` | `array<object>` |  |
| `tax_providers_fields` | `array<object>` |  |
| `object` | `string` |  |
| `card_status` | `string` |  |
| `custom_fields` | `array<object>` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_offset` | `string` |  |

</details>

### Customer Get

Retrieve a customer

#### Python SDK

```python
await chargebee.customer.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "customer",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Customer ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `first_name` | `string` |  |
| `last_name` | `string` |  |
| `email` | `string` |  |
| `phone` | `string` |  |
| `company` | `string` |  |
| `vat_number` | `string` |  |
| `auto_collection` | `string` |  |
| `offline_payment_method` | `string` |  |
| `net_term_days` | `integer` |  |
| `vat_number_validated_time` | `integer` |  |
| `vat_number_status` | `string` |  |
| `allow_direct_debit` | `boolean` |  |
| `is_location_valid` | `boolean` |  |
| `created_at` | `integer` |  |
| `created_from_ip` | `string` |  |
| `taxability` | `string` |  |
| `entity_code` | `string` |  |
| `exempt_number` | `string` |  |
| `resource_version` | `integer` |  |
| `updated_at` | `integer` |  |
| `locale` | `string` |  |
| `billing_date` | `integer` |  |
| `billing_date_mode` | `string` |  |
| `billing_day_of_week` | `string` |  |
| `billing_day_of_week_mode` | `string` |  |
| `billing_month` | `integer` |  |
| `pii_cleared` | `string` |  |
| `auto_close_invoices` | `boolean` |  |
| `channel` | `string` |  |
| `fraud_flag` | `string` |  |
| `primary_payment_source_id` | `string` |  |
| `backup_payment_source_id` | `string` |  |
| `invoice_notes` | `string` |  |
| `business_entity_id` | `string` |  |
| `preferred_currency_code` | `string` |  |
| `promotional_credits` | `integer` |  |
| `unbilled_charges` | `integer` |  |
| `refundable_credits` | `integer` |  |
| `excess_payments` | `integer` |  |
| `deleted` | `boolean` |  |
| `registered_for_gst` | `boolean` |  |
| `consolidated_invoicing` | `boolean` |  |
| `customer_type` | `string` |  |
| `business_customer_without_vat_number` | `boolean` |  |
| `client_profile_id` | `string` |  |
| `use_default_hierarchy_settings` | `boolean` |  |
| `vat_number_prefix` | `string` |  |
| `billing_address` | `object` |  |
| `referral_urls` | `array<object>` |  |
| `contacts` | `array<object>` |  |
| `payment_method` | `object` |  |
| `balances` | `array<object>` |  |
| `relationship` | `object` |  |
| `parent_account_access` | `object` |  |
| `child_account_access` | `object` |  |
| `meta_data` | `object` |  |
| `mrr` | `integer` |  |
| `exemption_details` | `array<object>` |  |
| `tax_providers_fields` | `array<object>` |  |
| `object` | `string` |  |
| `card_status` | `string` |  |
| `custom_fields` | `array<object>` |  |


</details>

### Customer Search

Search and filter customer records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await chargebee.customer.search(
    query={"filter": {"eq": {"allow_direct_debit": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "customer",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"allow_direct_debit": True}}}
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
| `allow_direct_debit` | `boolean` | Indicates if direct debit is allowed for the customer. |
| `auto_close_invoices` | `boolean` | Flag to automatically close invoices for the customer. |
| `auto_collection` | `string` | Configures the automatic collection settings for the customer. |
| `backup_payment_source_id` | `string` | ID of the backup payment source for the customer. |
| `balances` | `array` | Customer's balance information related to their account. |
| `billing_address` | `object` | Customer's billing address details. |
| `billing_date` | `integer` | Date for billing cycle. |
| `billing_date_mode` | `string` | Mode for billing date calculation. |
| `billing_day_of_week` | `string` | Day of the week for billing cycle. |
| `billing_day_of_week_mode` | `string` | Mode for billing day of the week calculation. |
| `billing_month` | `integer` | Month for billing cycle. |
| `business_customer_without_vat_number` | `boolean` | Flag indicating business customer without a VAT number. |
| `business_entity_id` | `string` | ID of the business entity. |
| `card_status` | `string` | Status of payment card associated with the customer. |
| `channel` | `string` | Channel through which the customer was acquired. |
| `child_account_access` | `object` | Information regarding the access rights of child accounts linked to the customer's account. |
| `client_profile_id` | `string` | Client profile ID of the customer. |
| `company` | `string` | Company or organization name. |
| `consolidated_invoicing` | `boolean` | Flag for consolidated invoicing setting. |
| `contacts` | `array` | List of contact details associated with the customer. |
| `created_at` | `integer` | Date and time when the customer was created. |
| `created_from_ip` | `string` | IP address from which the customer was created. |
| `custom_fields` | `array` |  |
| `customer_type` | `string` | Type of customer (e.g., individual, business). |
| `deleted` | `boolean` | Flag indicating if the customer is deleted. |
| `email` | `string` | Email address of the customer. |
| `entity_code` | `string` | Code for the customer entity. |
| `excess_payments` | `integer` | Total amount of excess payments by the customer. |
| `exempt_number` | `string` | Exemption number for tax purposes. |
| `exemption_details` | `array` | Details about any exemptions applicable to the customer's account. |
| `first_name` | `string` | First name of the customer. |
| `fraud_flag` | `string` | Flag indicating if fraud is associated with the customer. |
| `id` | `string` | Unique ID of the customer. |
| `invoice_notes` | `string` | Notes added to the customer's invoices. |
| `is_location_valid` | `boolean` | Flag indicating if the customer location is valid. |
| `last_name` | `string` | Last name of the customer. |
| `locale` | `string` | Locale setting for the customer. |
| `meta_data` | `object` | Additional metadata associated with the customer. |
| `mrr` | `integer` | Monthly recurring revenue generated from the customer. |
| `net_term_days` | `integer` | Number of days for net terms. |
| `object` | `string` | Object type for the customer. |
| `offline_payment_method` | `string` | Offline payment method used by the customer. |
| `parent_account_access` | `object` | Information regarding the access rights of the parent account, if applicable. |
| `payment_method` | `object` | Customer's preferred payment method details. |
| `phone` | `string` | Phone number of the customer. |
| `pii_cleared` | `string` | Flag indicating if PII (Personally Identifiable Information) is cleared. |
| `preferred_currency_code` | `string` | Preferred currency code for transactions. |
| `primary_payment_source_id` | `string` | ID of the primary payment source for the customer. |
| `promotional_credits` | `integer` | Total amount of promotional credits used. |
| `referral_urls` | `array` | List of referral URLs associated with the customer. |
| `refundable_credits` | `integer` | Total amount of refundable credits. |
| `registered_for_gst` | `boolean` | Flag indicating if the customer is registered for GST. |
| `relationship` | `object` | Details about the relationship of the customer to other entities, if any. |
| `resource_version` | `integer` | Version of the customer's resource. |
| `tax_providers_fields` | `array` | Fields related to tax providers. |
| `taxability` | `string` | Taxability status of the customer. |
| `unbilled_charges` | `integer` | Total amount of unbilled charges. |
| `updated_at` | `integer` | Date and time when the customer record was last updated. |
| `use_default_hierarchy_settings` | `boolean` | Flag indicating if default hierarchy settings are used. |
| `vat_number` | `string` | VAT number associated with the customer. |
| `vat_number_prefix` | `string` | Prefix for the VAT number. |
| `vat_number_status` | `string` | Status of the VAT number validation. |
| `vat_number_validated_time` | `integer` | Date and time when the VAT number was validated. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].allow_direct_debit` | `boolean` | Indicates if direct debit is allowed for the customer. |
| `data[].auto_close_invoices` | `boolean` | Flag to automatically close invoices for the customer. |
| `data[].auto_collection` | `string` | Configures the automatic collection settings for the customer. |
| `data[].backup_payment_source_id` | `string` | ID of the backup payment source for the customer. |
| `data[].balances` | `array` | Customer's balance information related to their account. |
| `data[].billing_address` | `object` | Customer's billing address details. |
| `data[].billing_date` | `integer` | Date for billing cycle. |
| `data[].billing_date_mode` | `string` | Mode for billing date calculation. |
| `data[].billing_day_of_week` | `string` | Day of the week for billing cycle. |
| `data[].billing_day_of_week_mode` | `string` | Mode for billing day of the week calculation. |
| `data[].billing_month` | `integer` | Month for billing cycle. |
| `data[].business_customer_without_vat_number` | `boolean` | Flag indicating business customer without a VAT number. |
| `data[].business_entity_id` | `string` | ID of the business entity. |
| `data[].card_status` | `string` | Status of payment card associated with the customer. |
| `data[].channel` | `string` | Channel through which the customer was acquired. |
| `data[].child_account_access` | `object` | Information regarding the access rights of child accounts linked to the customer's account. |
| `data[].client_profile_id` | `string` | Client profile ID of the customer. |
| `data[].company` | `string` | Company or organization name. |
| `data[].consolidated_invoicing` | `boolean` | Flag for consolidated invoicing setting. |
| `data[].contacts` | `array` | List of contact details associated with the customer. |
| `data[].created_at` | `integer` | Date and time when the customer was created. |
| `data[].created_from_ip` | `string` | IP address from which the customer was created. |
| `data[].custom_fields` | `array` |  |
| `data[].customer_type` | `string` | Type of customer (e.g., individual, business). |
| `data[].deleted` | `boolean` | Flag indicating if the customer is deleted. |
| `data[].email` | `string` | Email address of the customer. |
| `data[].entity_code` | `string` | Code for the customer entity. |
| `data[].excess_payments` | `integer` | Total amount of excess payments by the customer. |
| `data[].exempt_number` | `string` | Exemption number for tax purposes. |
| `data[].exemption_details` | `array` | Details about any exemptions applicable to the customer's account. |
| `data[].first_name` | `string` | First name of the customer. |
| `data[].fraud_flag` | `string` | Flag indicating if fraud is associated with the customer. |
| `data[].id` | `string` | Unique ID of the customer. |
| `data[].invoice_notes` | `string` | Notes added to the customer's invoices. |
| `data[].is_location_valid` | `boolean` | Flag indicating if the customer location is valid. |
| `data[].last_name` | `string` | Last name of the customer. |
| `data[].locale` | `string` | Locale setting for the customer. |
| `data[].meta_data` | `object` | Additional metadata associated with the customer. |
| `data[].mrr` | `integer` | Monthly recurring revenue generated from the customer. |
| `data[].net_term_days` | `integer` | Number of days for net terms. |
| `data[].object` | `string` | Object type for the customer. |
| `data[].offline_payment_method` | `string` | Offline payment method used by the customer. |
| `data[].parent_account_access` | `object` | Information regarding the access rights of the parent account, if applicable. |
| `data[].payment_method` | `object` | Customer's preferred payment method details. |
| `data[].phone` | `string` | Phone number of the customer. |
| `data[].pii_cleared` | `string` | Flag indicating if PII (Personally Identifiable Information) is cleared. |
| `data[].preferred_currency_code` | `string` | Preferred currency code for transactions. |
| `data[].primary_payment_source_id` | `string` | ID of the primary payment source for the customer. |
| `data[].promotional_credits` | `integer` | Total amount of promotional credits used. |
| `data[].referral_urls` | `array` | List of referral URLs associated with the customer. |
| `data[].refundable_credits` | `integer` | Total amount of refundable credits. |
| `data[].registered_for_gst` | `boolean` | Flag indicating if the customer is registered for GST. |
| `data[].relationship` | `object` | Details about the relationship of the customer to other entities, if any. |
| `data[].resource_version` | `integer` | Version of the customer's resource. |
| `data[].tax_providers_fields` | `array` | Fields related to tax providers. |
| `data[].taxability` | `string` | Taxability status of the customer. |
| `data[].unbilled_charges` | `integer` | Total amount of unbilled charges. |
| `data[].updated_at` | `integer` | Date and time when the customer record was last updated. |
| `data[].use_default_hierarchy_settings` | `boolean` | Flag indicating if default hierarchy settings are used. |
| `data[].vat_number` | `string` | VAT number associated with the customer. |
| `data[].vat_number_prefix` | `string` | Prefix for the VAT number. |
| `data[].vat_number_status` | `string` | Status of the VAT number validation. |
| `data[].vat_number_validated_time` | `integer` | Date and time when the VAT number was validated. |

</details>

## Subscription

### Subscription List

List subscriptions

#### Python SDK

```python
await chargebee.subscription.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "subscription",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No |  |
| `offset` | `string` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `customer_id` | `string` |  |
| `plan_id` | `string` |  |
| `plan_quantity` | `integer` |  |
| `plan_unit_price` | `integer` |  |
| `plan_amount` | `integer` |  |
| `plan_free_quantity` | `integer` |  |
| `status` | `string` |  |
| `trial_start` | `integer` |  |
| `trial_end` | `integer` |  |
| `current_term_start` | `integer` |  |
| `current_term_end` | `integer` |  |
| `next_billing_at` | `integer` |  |
| `created_at` | `integer` |  |
| `started_at` | `integer` |  |
| `activated_at` | `integer` |  |
| `cancelled_at` | `integer` |  |
| `cancel_reason` | `string` |  |
| `channel` | `string` |  |
| `billing_period` | `integer` |  |
| `billing_period_unit` | `string` |  |
| `auto_collection` | `string` |  |
| `currency_code` | `string` |  |
| `remaining_billing_cycles` | `integer` |  |
| `po_number` | `string` |  |
| `created_from_ip` | `string` |  |
| `resource_version` | `integer` |  |
| `updated_at` | `integer` |  |
| `has_scheduled_changes` | `boolean` |  |
| `payment_source_id` | `string` |  |
| `plan_free_quantity_in_decimal` | `string` |  |
| `plan_quantity_in_decimal` | `string` |  |
| `plan_unit_price_in_decimal` | `string` |  |
| `plan_amount_in_decimal` | `string` |  |
| `due_invoices_count` | `integer` |  |
| `due_since` | `integer` |  |
| `total_dues` | `integer` |  |
| `mrr` | `integer` |  |
| `exchange_rate` | `number` |  |
| `base_currency_code` | `string` |  |
| `override_relationship` | `boolean` |  |
| `trial_end_action` | `string` |  |
| `pause_date` | `integer` |  |
| `resume_date` | `integer` |  |
| `cancelled_at_term_end` | `boolean` |  |
| `has_scheduled_advance_invoices` | `boolean` |  |
| `object` | `string` |  |
| `addons` | `array<object>` |  |
| `coupons` | `array<object>` |  |
| `discounts` | `array<object>` |  |
| `subscription_items` | `array<object>` |  |
| `item_tiers` | `array<object>` |  |
| `charged_items` | `array<object>` |  |
| `shipping_address` | `object` |  |
| `contract_term` | `object` |  |
| `meta_data` | `object` |  |
| `deleted` | `boolean` |  |
| `business_entity_id` | `string` |  |
| `free_period` | `integer` |  |
| `free_period_unit` | `string` |  |
| `cf_mandate_id` | `string` |  |
| `custom_fields` | `array<object>` |  |
| `changes_scheduled_at` | `integer` |  |
| `invoice_notes` | `string` |  |
| `auto_close_invoices` | `boolean` |  |
| `offline_payment_method` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_offset` | `string` |  |

</details>

### Subscription Get

Retrieve a subscription

#### Python SDK

```python
await chargebee.subscription.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "subscription",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Subscription ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `customer_id` | `string` |  |
| `plan_id` | `string` |  |
| `plan_quantity` | `integer` |  |
| `plan_unit_price` | `integer` |  |
| `plan_amount` | `integer` |  |
| `plan_free_quantity` | `integer` |  |
| `status` | `string` |  |
| `trial_start` | `integer` |  |
| `trial_end` | `integer` |  |
| `current_term_start` | `integer` |  |
| `current_term_end` | `integer` |  |
| `next_billing_at` | `integer` |  |
| `created_at` | `integer` |  |
| `started_at` | `integer` |  |
| `activated_at` | `integer` |  |
| `cancelled_at` | `integer` |  |
| `cancel_reason` | `string` |  |
| `channel` | `string` |  |
| `billing_period` | `integer` |  |
| `billing_period_unit` | `string` |  |
| `auto_collection` | `string` |  |
| `currency_code` | `string` |  |
| `remaining_billing_cycles` | `integer` |  |
| `po_number` | `string` |  |
| `created_from_ip` | `string` |  |
| `resource_version` | `integer` |  |
| `updated_at` | `integer` |  |
| `has_scheduled_changes` | `boolean` |  |
| `payment_source_id` | `string` |  |
| `plan_free_quantity_in_decimal` | `string` |  |
| `plan_quantity_in_decimal` | `string` |  |
| `plan_unit_price_in_decimal` | `string` |  |
| `plan_amount_in_decimal` | `string` |  |
| `due_invoices_count` | `integer` |  |
| `due_since` | `integer` |  |
| `total_dues` | `integer` |  |
| `mrr` | `integer` |  |
| `exchange_rate` | `number` |  |
| `base_currency_code` | `string` |  |
| `override_relationship` | `boolean` |  |
| `trial_end_action` | `string` |  |
| `pause_date` | `integer` |  |
| `resume_date` | `integer` |  |
| `cancelled_at_term_end` | `boolean` |  |
| `has_scheduled_advance_invoices` | `boolean` |  |
| `object` | `string` |  |
| `addons` | `array<object>` |  |
| `coupons` | `array<object>` |  |
| `discounts` | `array<object>` |  |
| `subscription_items` | `array<object>` |  |
| `item_tiers` | `array<object>` |  |
| `charged_items` | `array<object>` |  |
| `shipping_address` | `object` |  |
| `contract_term` | `object` |  |
| `meta_data` | `object` |  |
| `deleted` | `boolean` |  |
| `business_entity_id` | `string` |  |
| `free_period` | `integer` |  |
| `free_period_unit` | `string` |  |
| `cf_mandate_id` | `string` |  |
| `custom_fields` | `array<object>` |  |
| `changes_scheduled_at` | `integer` |  |
| `invoice_notes` | `string` |  |
| `auto_close_invoices` | `boolean` |  |
| `offline_payment_method` | `string` |  |


</details>

### Subscription Search

Search and filter subscription records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await chargebee.subscription.search(
    query={"filter": {"eq": {"activated_at": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "subscription",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"activated_at": 0}}}
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
| `activated_at` | `integer` | The date and time when the subscription was activated. |
| `addons` | `array` | Represents any additional features or services added to the subscription |
| `affiliate_token` | `string` | The affiliate token associated with the subscription. |
| `auto_close_invoices` | `boolean` | Defines if the invoices are automatically closed or not. |
| `auto_collection` | `string` | Indicates if auto-collection is enabled for the subscription. |
| `base_currency_code` | `string` | The base currency code used for the subscription. |
| `billing_period` | `integer` | The billing period duration for the subscription. |
| `billing_period_unit` | `string` | The unit of the billing period. |
| `business_entity_id` | `string` | The ID of the business entity to which the subscription belongs. |
| `cancel_reason` | `string` | The reason for the cancellation of the subscription. |
| `cancel_reason_code` | `string` | The code associated with the cancellation reason. |
| `cancel_schedule_created_at` | `integer` | The date and time when the cancellation schedule was created. |
| `cancelled_at` | `integer` | The date and time when the subscription was cancelled. |
| `channel` | `string` | The channel through which the subscription was acquired. |
| `charged_event_based_addons` | `array` | Details of addons charged based on events |
| `charged_items` | `array` | Lists the items that have been charged as part of the subscription |
| `contract_term` | `object` | Contains details about the contract term of the subscription |
| `contract_term_billing_cycle_on_renewal` | `integer` | Indicates if the contract term billing cycle is applied on renewal. |
| `coupon` | `string` | The coupon applied to the subscription. |
| `coupons` | `array` | Details of applied coupons |
| `create_pending_invoices` | `boolean` | Indicates if pending invoices are created. |
| `created_at` | `integer` | The date and time of the creation of the subscription. |
| `created_from_ip` | `string` | The IP address from which the subscription was created. |
| `currency_code` | `string` | The currency code used for the subscription. |
| `current_term_end` | `integer` | The end date of the current term for the subscription. |
| `current_term_start` | `integer` | The start date of the current term for the subscription. |
| `custom_fields` | `array` |  |
| `customer_id` | `string` | The ID of the customer associated with the subscription. |
| `deleted` | `boolean` | Indicates if the subscription has been deleted. |
| `discounts` | `array` | Includes any discounts applied to the subscription |
| `due_invoices_count` | `integer` | The count of due invoices for the subscription. |
| `due_since` | `integer` | The date since which the invoices are due. |
| `event_based_addons` | `array` | Specifies any event-based addons associated with the subscription |
| `exchange_rate` | `number` | The exchange rate used for currency conversion. |
| `free_period` | `integer` | The duration of the free period for the subscription. |
| `free_period_unit` | `string` | The unit of the free period duration. |
| `gift_id` | `string` | The ID of the gift associated with the subscription. |
| `has_scheduled_advance_invoices` | `boolean` | Indicates if there are scheduled advance invoices for the subscription. |
| `has_scheduled_changes` | `boolean` | Indicates if there are scheduled changes for the subscription. |
| `id` | `string` | The unique ID of the subscription. |
| `invoice_notes` | `string` | Any notes added to the invoices of the subscription. |
| `item_tiers` | `array` | Provides information about tiers or levels for specific subscription items |
| `meta_data` | `object` | Additional metadata associated with subscription |
| `metadata` | `object` | Additional metadata associated with subscription |
| `mrr` | `integer` | The monthly recurring revenue generated by the subscription. |
| `next_billing_at` | `integer` | The date and time of the next billing event for the subscription. |
| `object` | `string` | The type of object (subscription). |
| `offline_payment_method` | `string` | The offline payment method used for the subscription. |
| `override_relationship` | `boolean` | Indicates if the existing relationship is overridden by this subscription. |
| `pause_date` | `integer` | The date on which the subscription was paused. |
| `payment_source_id` | `string` | The ID of the payment source used for the subscription. |
| `plan_amount` | `integer` | The total amount charged for the plan of the subscription. |
| `plan_amount_in_decimal` | `string` | The total amount charged for the plan in decimal format. |
| `plan_free_quantity` | `integer` | The free quantity included in the plan of the subscription. |
| `plan_free_quantity_in_decimal` | `string` | The free quantity included in the plan in decimal format. |
| `plan_id` | `string` | The ID of the plan associated with the subscription. |
| `plan_quantity` | `integer` | The quantity of the plan included in the subscription. |
| `plan_quantity_in_decimal` | `string` | The quantity of the plan in decimal format. |
| `plan_unit_price` | `integer` | The unit price of the plan for the subscription. |
| `plan_unit_price_in_decimal` | `string` | The unit price of the plan in decimal format. |
| `po_number` | `string` | The purchase order number associated with the subscription. |
| `referral_info` | `object` | Contains details related to any referral information associated with the subscription |
| `remaining_billing_cycles` | `integer` | The count of remaining billing cycles for the subscription. |
| `resource_version` | `integer` | The version of the resource (subscription). |
| `resume_date` | `integer` | The date on which the subscription was resumed. |
| `setup_fee` | `integer` | The setup fee charged for the subscription. |
| `shipping_address` | `object` | Stores the shipping address related to the subscription |
| `start_date` | `integer` | The start date of the subscription. |
| `started_at` | `integer` | The date and time when the subscription started. |
| `status` | `string` | The current status of the subscription. |
| `subscription_items` | `array` | Lists individual items included in the subscription |
| `total_dues` | `integer` | The total amount of dues for the subscription. |
| `trial_end` | `integer` | The end date of the trial period for the subscription. |
| `trial_end_action` | `string` | The action to be taken at the end of the trial period. |
| `trial_start` | `integer` | The start date of the trial period for the subscription. |
| `updated_at` | `integer` | The date and time when the subscription was last updated. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].activated_at` | `integer` | The date and time when the subscription was activated. |
| `data[].addons` | `array` | Represents any additional features or services added to the subscription |
| `data[].affiliate_token` | `string` | The affiliate token associated with the subscription. |
| `data[].auto_close_invoices` | `boolean` | Defines if the invoices are automatically closed or not. |
| `data[].auto_collection` | `string` | Indicates if auto-collection is enabled for the subscription. |
| `data[].base_currency_code` | `string` | The base currency code used for the subscription. |
| `data[].billing_period` | `integer` | The billing period duration for the subscription. |
| `data[].billing_period_unit` | `string` | The unit of the billing period. |
| `data[].business_entity_id` | `string` | The ID of the business entity to which the subscription belongs. |
| `data[].cancel_reason` | `string` | The reason for the cancellation of the subscription. |
| `data[].cancel_reason_code` | `string` | The code associated with the cancellation reason. |
| `data[].cancel_schedule_created_at` | `integer` | The date and time when the cancellation schedule was created. |
| `data[].cancelled_at` | `integer` | The date and time when the subscription was cancelled. |
| `data[].channel` | `string` | The channel through which the subscription was acquired. |
| `data[].charged_event_based_addons` | `array` | Details of addons charged based on events |
| `data[].charged_items` | `array` | Lists the items that have been charged as part of the subscription |
| `data[].contract_term` | `object` | Contains details about the contract term of the subscription |
| `data[].contract_term_billing_cycle_on_renewal` | `integer` | Indicates if the contract term billing cycle is applied on renewal. |
| `data[].coupon` | `string` | The coupon applied to the subscription. |
| `data[].coupons` | `array` | Details of applied coupons |
| `data[].create_pending_invoices` | `boolean` | Indicates if pending invoices are created. |
| `data[].created_at` | `integer` | The date and time of the creation of the subscription. |
| `data[].created_from_ip` | `string` | The IP address from which the subscription was created. |
| `data[].currency_code` | `string` | The currency code used for the subscription. |
| `data[].current_term_end` | `integer` | The end date of the current term for the subscription. |
| `data[].current_term_start` | `integer` | The start date of the current term for the subscription. |
| `data[].custom_fields` | `array` |  |
| `data[].customer_id` | `string` | The ID of the customer associated with the subscription. |
| `data[].deleted` | `boolean` | Indicates if the subscription has been deleted. |
| `data[].discounts` | `array` | Includes any discounts applied to the subscription |
| `data[].due_invoices_count` | `integer` | The count of due invoices for the subscription. |
| `data[].due_since` | `integer` | The date since which the invoices are due. |
| `data[].event_based_addons` | `array` | Specifies any event-based addons associated with the subscription |
| `data[].exchange_rate` | `number` | The exchange rate used for currency conversion. |
| `data[].free_period` | `integer` | The duration of the free period for the subscription. |
| `data[].free_period_unit` | `string` | The unit of the free period duration. |
| `data[].gift_id` | `string` | The ID of the gift associated with the subscription. |
| `data[].has_scheduled_advance_invoices` | `boolean` | Indicates if there are scheduled advance invoices for the subscription. |
| `data[].has_scheduled_changes` | `boolean` | Indicates if there are scheduled changes for the subscription. |
| `data[].id` | `string` | The unique ID of the subscription. |
| `data[].invoice_notes` | `string` | Any notes added to the invoices of the subscription. |
| `data[].item_tiers` | `array` | Provides information about tiers or levels for specific subscription items |
| `data[].meta_data` | `object` | Additional metadata associated with subscription |
| `data[].metadata` | `object` | Additional metadata associated with subscription |
| `data[].mrr` | `integer` | The monthly recurring revenue generated by the subscription. |
| `data[].next_billing_at` | `integer` | The date and time of the next billing event for the subscription. |
| `data[].object` | `string` | The type of object (subscription). |
| `data[].offline_payment_method` | `string` | The offline payment method used for the subscription. |
| `data[].override_relationship` | `boolean` | Indicates if the existing relationship is overridden by this subscription. |
| `data[].pause_date` | `integer` | The date on which the subscription was paused. |
| `data[].payment_source_id` | `string` | The ID of the payment source used for the subscription. |
| `data[].plan_amount` | `integer` | The total amount charged for the plan of the subscription. |
| `data[].plan_amount_in_decimal` | `string` | The total amount charged for the plan in decimal format. |
| `data[].plan_free_quantity` | `integer` | The free quantity included in the plan of the subscription. |
| `data[].plan_free_quantity_in_decimal` | `string` | The free quantity included in the plan in decimal format. |
| `data[].plan_id` | `string` | The ID of the plan associated with the subscription. |
| `data[].plan_quantity` | `integer` | The quantity of the plan included in the subscription. |
| `data[].plan_quantity_in_decimal` | `string` | The quantity of the plan in decimal format. |
| `data[].plan_unit_price` | `integer` | The unit price of the plan for the subscription. |
| `data[].plan_unit_price_in_decimal` | `string` | The unit price of the plan in decimal format. |
| `data[].po_number` | `string` | The purchase order number associated with the subscription. |
| `data[].referral_info` | `object` | Contains details related to any referral information associated with the subscription |
| `data[].remaining_billing_cycles` | `integer` | The count of remaining billing cycles for the subscription. |
| `data[].resource_version` | `integer` | The version of the resource (subscription). |
| `data[].resume_date` | `integer` | The date on which the subscription was resumed. |
| `data[].setup_fee` | `integer` | The setup fee charged for the subscription. |
| `data[].shipping_address` | `object` | Stores the shipping address related to the subscription |
| `data[].start_date` | `integer` | The start date of the subscription. |
| `data[].started_at` | `integer` | The date and time when the subscription started. |
| `data[].status` | `string` | The current status of the subscription. |
| `data[].subscription_items` | `array` | Lists individual items included in the subscription |
| `data[].total_dues` | `integer` | The total amount of dues for the subscription. |
| `data[].trial_end` | `integer` | The end date of the trial period for the subscription. |
| `data[].trial_end_action` | `string` | The action to be taken at the end of the trial period. |
| `data[].trial_start` | `integer` | The start date of the trial period for the subscription. |
| `data[].updated_at` | `integer` | The date and time when the subscription was last updated. |

</details>

## Invoice

### Invoice List

List invoices

#### Python SDK

```python
await chargebee.invoice.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "invoice",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No |  |
| `offset` | `string` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `customer_id` | `string` |  |
| `subscription_id` | `string` |  |
| `recurring` | `boolean` |  |
| `status` | `string` |  |
| `price_type` | `string` |  |
| `date` | `integer` |  |
| `due_date` | `integer` |  |
| `net_term_days` | `integer` |  |
| `currency_code` | `string` |  |
| `total` | `integer` |  |
| `amount_paid` | `integer` |  |
| `amount_adjusted` | `integer` |  |
| `write_off_amount` | `integer` |  |
| `credits_applied` | `integer` |  |
| `amount_due` | `integer` |  |
| `paid_at` | `integer` |  |
| `dunning_status` | `string` |  |
| `updated_at` | `integer` |  |
| `resource_version` | `integer` |  |
| `deleted` | `boolean` |  |
| `object` | `string` |  |
| `first_invoice` | `boolean` |  |
| `amount_to_collect` | `integer` |  |
| `round_off_amount` | `integer` |  |
| `new_sales_amount` | `integer` |  |
| `has_advance_charges` | `boolean` |  |
| `tax` | `integer` |  |
| `sub_total` | `integer` |  |
| `sub_total_in_local_currency` | `integer` |  |
| `total_in_local_currency` | `integer` |  |
| `exchange_rate` | `number` |  |
| `base_currency_code` | `string` |  |
| `is_gifted` | `boolean` |  |
| `generated_at` | `integer` |  |
| `expected_payment_date` | `integer` |  |
| `channel` | `string` |  |
| `business_entity_id` | `string` |  |
| `line_items` | `array<object>` |  |
| `discounts` | `array<object>` |  |
| `line_item_discounts` | `array<object>` |  |
| `taxes` | `array<object>` |  |
| `line_item_taxes` | `array<object>` |  |
| `line_item_tiers` | `array<object>` |  |
| `linked_payments` | `array<object>` |  |
| `dunning_attempts` | `array<object>` |  |
| `applied_credits` | `array<object>` |  |
| `adjustment_credit_notes` | `array<object>` |  |
| `issued_credit_notes` | `array<object>` |  |
| `linked_orders` | `array<object>` |  |
| `notes` | `array<object>` |  |
| `billing_address` | `object` |  |
| `shipping_address` | `object` |  |
| `linked_taxes_withheld` | `array<object>` |  |
| `custom_fields` | `array<object>` |  |
| `void_reason_code` | `string` |  |
| `voided_at` | `integer` |  |
| `created_at` | `integer` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_offset` | `string` |  |

</details>

### Invoice Get

Retrieve an invoice

#### Python SDK

```python
await chargebee.invoice.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "invoice",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Invoice ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `customer_id` | `string` |  |
| `subscription_id` | `string` |  |
| `recurring` | `boolean` |  |
| `status` | `string` |  |
| `price_type` | `string` |  |
| `date` | `integer` |  |
| `due_date` | `integer` |  |
| `net_term_days` | `integer` |  |
| `currency_code` | `string` |  |
| `total` | `integer` |  |
| `amount_paid` | `integer` |  |
| `amount_adjusted` | `integer` |  |
| `write_off_amount` | `integer` |  |
| `credits_applied` | `integer` |  |
| `amount_due` | `integer` |  |
| `paid_at` | `integer` |  |
| `dunning_status` | `string` |  |
| `updated_at` | `integer` |  |
| `resource_version` | `integer` |  |
| `deleted` | `boolean` |  |
| `object` | `string` |  |
| `first_invoice` | `boolean` |  |
| `amount_to_collect` | `integer` |  |
| `round_off_amount` | `integer` |  |
| `new_sales_amount` | `integer` |  |
| `has_advance_charges` | `boolean` |  |
| `tax` | `integer` |  |
| `sub_total` | `integer` |  |
| `sub_total_in_local_currency` | `integer` |  |
| `total_in_local_currency` | `integer` |  |
| `exchange_rate` | `number` |  |
| `base_currency_code` | `string` |  |
| `is_gifted` | `boolean` |  |
| `generated_at` | `integer` |  |
| `expected_payment_date` | `integer` |  |
| `channel` | `string` |  |
| `business_entity_id` | `string` |  |
| `line_items` | `array<object>` |  |
| `discounts` | `array<object>` |  |
| `line_item_discounts` | `array<object>` |  |
| `taxes` | `array<object>` |  |
| `line_item_taxes` | `array<object>` |  |
| `line_item_tiers` | `array<object>` |  |
| `linked_payments` | `array<object>` |  |
| `dunning_attempts` | `array<object>` |  |
| `applied_credits` | `array<object>` |  |
| `adjustment_credit_notes` | `array<object>` |  |
| `issued_credit_notes` | `array<object>` |  |
| `linked_orders` | `array<object>` |  |
| `notes` | `array<object>` |  |
| `billing_address` | `object` |  |
| `shipping_address` | `object` |  |
| `linked_taxes_withheld` | `array<object>` |  |
| `custom_fields` | `array<object>` |  |
| `void_reason_code` | `string` |  |
| `voided_at` | `integer` |  |
| `created_at` | `integer` |  |


</details>

### Invoice Search

Search and filter invoice records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await chargebee.invoice.search(
    query={"filter": {"eq": {"adjustment_credit_notes": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "invoice",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"adjustment_credit_notes": []}}}
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
| `adjustment_credit_notes` | `array` | Details of adjustment credit notes applied to the invoice |
| `amount_adjusted` | `integer` | Total amount adjusted in the invoice |
| `amount_due` | `integer` | Amount due for payment |
| `amount_paid` | `integer` | Amount already paid |
| `amount_to_collect` | `integer` | Amount yet to be collected |
| `applied_credits` | `array` | Details of credits applied to the invoice |
| `base_currency_code` | `string` | Currency code used as base for the invoice |
| `billing_address` | `object` | Details of the billing address associated with the invoice |
| `business_entity_id` | `string` | ID of the business entity |
| `channel` | `string` | Channel through which the invoice was generated |
| `credits_applied` | `integer` | Total credits applied to the invoice |
| `currency_code` | `string` | Currency code of the invoice |
| `custom_fields` | `array` |  |
| `customer_id` | `string` | ID of the customer |
| `date` | `integer` | Date of the invoice |
| `deleted` | `boolean` | Flag indicating if the invoice is deleted |
| `discounts` | `array` | Discount details applied to the invoice |
| `due_date` | `integer` | Due date for payment |
| `dunning_attempts` | `array` | Details of dunning attempts made |
| `dunning_status` | `string` | Status of dunning for the invoice |
| `einvoice` | `object` | Details of electronic invoice |
| `exchange_rate` | `number` | Exchange rate used for currency conversion |
| `expected_payment_date` | `integer` | Expected date of payment |
| `first_invoice` | `boolean` | Flag indicating whether it's the first invoice |
| `generated_at` | `integer` | Date when the invoice was generated |
| `has_advance_charges` | `boolean` | Flag indicating if there are advance charges |
| `id` | `string` | Unique ID of the invoice |
| `is_digital` | `boolean` | Flag indicating if the invoice is digital |
| `is_gifted` | `boolean` | Flag indicating if the invoice is gifted |
| `issued_credit_notes` | `array` | Details of credit notes issued |
| `line_item_discounts` | `array` | Details of line item discounts |
| `line_item_taxes` | `array` | Tax details applied to each line item in the invoice |
| `line_item_tiers` | `array` | Tiers information for each line item in the invoice |
| `line_items` | `array` | Details of individual line items in the invoice |
| `linked_orders` | `array` | Details of linked orders to the invoice |
| `linked_payments` | `array` | Details of linked payments |
| `linked_taxes_withheld` | `array` | Details of linked taxes withheld on the invoice |
| `local_currency_code` | `string` | Local currency code of the invoice |
| `local_currency_exchange_rate` | `number` | Exchange rate for local currency conversion |
| `net_term_days` | `integer` | Net term days for payment |
| `new_sales_amount` | `integer` | New sales amount in the invoice |
| `next_retry_at` | `integer` | Date of the next payment retry |
| `notes` | `array` | Notes associated with the invoice |
| `object` | `string` | Type of object |
| `paid_at` | `integer` | Date when the invoice was paid |
| `payment_owner` | `string` | Owner of the payment |
| `po_number` | `string` | Purchase order number |
| `price_type` | `string` | Type of pricing |
| `recurring` | `boolean` | Flag indicating if it's a recurring invoice |
| `resource_version` | `integer` | Resource version of the invoice |
| `round_off_amount` | `integer` | Amount rounded off |
| `shipping_address` | `object` | Details of the shipping address associated with the invoice |
| `statement_descriptor` | `object` | Descriptor for the statement |
| `status` | `string` | Status of the invoice |
| `sub_total` | `integer` | Subtotal amount |
| `sub_total_in_local_currency` | `integer` | Subtotal amount in local currency |
| `subscription_id` | `string` | ID of the subscription associated |
| `tax` | `integer` | Total tax amount |
| `tax_category` | `string` | Tax category |
| `taxes` | `array` | Details of taxes applied |
| `term_finalized` | `boolean` | Flag indicating if the term is finalized |
| `total` | `integer` | Total amount of the invoice |
| `total_in_local_currency` | `integer` | Total amount in local currency |
| `updated_at` | `integer` | Date of last update |
| `vat_number` | `string` | VAT number |
| `vat_number_prefix` | `string` | Prefix for the VAT number |
| `void_reason_code` | `string` | Reason code for voiding the invoice |
| `voided_at` | `integer` | Date when the invoice was voided |
| `write_off_amount` | `integer` | Amount written off |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].adjustment_credit_notes` | `array` | Details of adjustment credit notes applied to the invoice |
| `data[].amount_adjusted` | `integer` | Total amount adjusted in the invoice |
| `data[].amount_due` | `integer` | Amount due for payment |
| `data[].amount_paid` | `integer` | Amount already paid |
| `data[].amount_to_collect` | `integer` | Amount yet to be collected |
| `data[].applied_credits` | `array` | Details of credits applied to the invoice |
| `data[].base_currency_code` | `string` | Currency code used as base for the invoice |
| `data[].billing_address` | `object` | Details of the billing address associated with the invoice |
| `data[].business_entity_id` | `string` | ID of the business entity |
| `data[].channel` | `string` | Channel through which the invoice was generated |
| `data[].credits_applied` | `integer` | Total credits applied to the invoice |
| `data[].currency_code` | `string` | Currency code of the invoice |
| `data[].custom_fields` | `array` |  |
| `data[].customer_id` | `string` | ID of the customer |
| `data[].date` | `integer` | Date of the invoice |
| `data[].deleted` | `boolean` | Flag indicating if the invoice is deleted |
| `data[].discounts` | `array` | Discount details applied to the invoice |
| `data[].due_date` | `integer` | Due date for payment |
| `data[].dunning_attempts` | `array` | Details of dunning attempts made |
| `data[].dunning_status` | `string` | Status of dunning for the invoice |
| `data[].einvoice` | `object` | Details of electronic invoice |
| `data[].exchange_rate` | `number` | Exchange rate used for currency conversion |
| `data[].expected_payment_date` | `integer` | Expected date of payment |
| `data[].first_invoice` | `boolean` | Flag indicating whether it's the first invoice |
| `data[].generated_at` | `integer` | Date when the invoice was generated |
| `data[].has_advance_charges` | `boolean` | Flag indicating if there are advance charges |
| `data[].id` | `string` | Unique ID of the invoice |
| `data[].is_digital` | `boolean` | Flag indicating if the invoice is digital |
| `data[].is_gifted` | `boolean` | Flag indicating if the invoice is gifted |
| `data[].issued_credit_notes` | `array` | Details of credit notes issued |
| `data[].line_item_discounts` | `array` | Details of line item discounts |
| `data[].line_item_taxes` | `array` | Tax details applied to each line item in the invoice |
| `data[].line_item_tiers` | `array` | Tiers information for each line item in the invoice |
| `data[].line_items` | `array` | Details of individual line items in the invoice |
| `data[].linked_orders` | `array` | Details of linked orders to the invoice |
| `data[].linked_payments` | `array` | Details of linked payments |
| `data[].linked_taxes_withheld` | `array` | Details of linked taxes withheld on the invoice |
| `data[].local_currency_code` | `string` | Local currency code of the invoice |
| `data[].local_currency_exchange_rate` | `number` | Exchange rate for local currency conversion |
| `data[].net_term_days` | `integer` | Net term days for payment |
| `data[].new_sales_amount` | `integer` | New sales amount in the invoice |
| `data[].next_retry_at` | `integer` | Date of the next payment retry |
| `data[].notes` | `array` | Notes associated with the invoice |
| `data[].object` | `string` | Type of object |
| `data[].paid_at` | `integer` | Date when the invoice was paid |
| `data[].payment_owner` | `string` | Owner of the payment |
| `data[].po_number` | `string` | Purchase order number |
| `data[].price_type` | `string` | Type of pricing |
| `data[].recurring` | `boolean` | Flag indicating if it's a recurring invoice |
| `data[].resource_version` | `integer` | Resource version of the invoice |
| `data[].round_off_amount` | `integer` | Amount rounded off |
| `data[].shipping_address` | `object` | Details of the shipping address associated with the invoice |
| `data[].statement_descriptor` | `object` | Descriptor for the statement |
| `data[].status` | `string` | Status of the invoice |
| `data[].sub_total` | `integer` | Subtotal amount |
| `data[].sub_total_in_local_currency` | `integer` | Subtotal amount in local currency |
| `data[].subscription_id` | `string` | ID of the subscription associated |
| `data[].tax` | `integer` | Total tax amount |
| `data[].tax_category` | `string` | Tax category |
| `data[].taxes` | `array` | Details of taxes applied |
| `data[].term_finalized` | `boolean` | Flag indicating if the term is finalized |
| `data[].total` | `integer` | Total amount of the invoice |
| `data[].total_in_local_currency` | `integer` | Total amount in local currency |
| `data[].updated_at` | `integer` | Date of last update |
| `data[].vat_number` | `string` | VAT number |
| `data[].vat_number_prefix` | `string` | Prefix for the VAT number |
| `data[].void_reason_code` | `string` | Reason code for voiding the invoice |
| `data[].voided_at` | `integer` | Date when the invoice was voided |
| `data[].write_off_amount` | `integer` | Amount written off |

</details>

## Credit Note

### Credit Note List

List credit notes

#### Python SDK

```python
await chargebee.credit_note.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "credit_note",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No |  |
| `offset` | `string` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `customer_id` | `string` |  |
| `subscription_id` | `string` |  |
| `reference_invoice_id` | `string` |  |
| `type` | `string` |  |
| `reason_code` | `string` |  |
| `status` | `string` |  |
| `date` | `integer` |  |
| `price_type` | `string` |  |
| `currency_code` | `string` |  |
| `total` | `integer` |  |
| `amount_allocated` | `integer` |  |
| `amount_refunded` | `integer` |  |
| `amount_available` | `integer` |  |
| `refunded_at` | `integer` |  |
| `voided_at` | `integer` |  |
| `generated_at` | `integer` |  |
| `resource_version` | `integer` |  |
| `updated_at` | `integer` |  |
| `sub_total` | `integer` |  |
| `sub_total_in_local_currency` | `integer` |  |
| `total_in_local_currency` | `integer` |  |
| `round_off_amount` | `integer` |  |
| `channel` | `string` |  |
| `exchange_rate` | `number` |  |
| `base_currency_code` | `string` |  |
| `business_entity_id` | `string` |  |
| `deleted` | `boolean` |  |
| `object` | `string` |  |
| `create_reason_code` | `string` |  |
| `void_reason_code` | `string` |  |
| `fractional_correction` | `integer` |  |
| `line_items` | `array<object>` |  |
| `discounts` | `array<object>` |  |
| `line_item_discounts` | `array<object>` |  |
| `line_item_tiers` | `array<object>` |  |
| `taxes` | `array<object>` |  |
| `line_item_taxes` | `array<object>` |  |
| `linked_refunds` | `array<object>` |  |
| `allocations` | `array<object>` |  |
| `linked_tax_withheld_refunds` | `array<object>` |  |
| `shipping_address` | `object` |  |
| `billing_address` | `object` |  |
| `custom_fields` | `array<object>` |  |
| `created_at` | `integer` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_offset` | `string` |  |

</details>

### Credit Note Get

Retrieve a credit note

#### Python SDK

```python
await chargebee.credit_note.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "credit_note",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Credit note ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `customer_id` | `string` |  |
| `subscription_id` | `string` |  |
| `reference_invoice_id` | `string` |  |
| `type` | `string` |  |
| `reason_code` | `string` |  |
| `status` | `string` |  |
| `date` | `integer` |  |
| `price_type` | `string` |  |
| `currency_code` | `string` |  |
| `total` | `integer` |  |
| `amount_allocated` | `integer` |  |
| `amount_refunded` | `integer` |  |
| `amount_available` | `integer` |  |
| `refunded_at` | `integer` |  |
| `voided_at` | `integer` |  |
| `generated_at` | `integer` |  |
| `resource_version` | `integer` |  |
| `updated_at` | `integer` |  |
| `sub_total` | `integer` |  |
| `sub_total_in_local_currency` | `integer` |  |
| `total_in_local_currency` | `integer` |  |
| `round_off_amount` | `integer` |  |
| `channel` | `string` |  |
| `exchange_rate` | `number` |  |
| `base_currency_code` | `string` |  |
| `business_entity_id` | `string` |  |
| `deleted` | `boolean` |  |
| `object` | `string` |  |
| `create_reason_code` | `string` |  |
| `void_reason_code` | `string` |  |
| `fractional_correction` | `integer` |  |
| `line_items` | `array<object>` |  |
| `discounts` | `array<object>` |  |
| `line_item_discounts` | `array<object>` |  |
| `line_item_tiers` | `array<object>` |  |
| `taxes` | `array<object>` |  |
| `line_item_taxes` | `array<object>` |  |
| `linked_refunds` | `array<object>` |  |
| `allocations` | `array<object>` |  |
| `linked_tax_withheld_refunds` | `array<object>` |  |
| `shipping_address` | `object` |  |
| `billing_address` | `object` |  |
| `custom_fields` | `array<object>` |  |
| `created_at` | `integer` |  |


</details>

### Credit Note Search

Search and filter credit note records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await chargebee.credit_note.search(
    query={"filter": {"eq": {"allocations": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "credit_note",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"allocations": []}}}
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
| `allocations` | `array` | Details of allocations associated with the credit note |
| `amount_allocated` | `integer` | The amount of credits allocated. |
| `amount_available` | `integer` | The amount of credits available. |
| `amount_refunded` | `integer` | The amount of credits refunded. |
| `base_currency_code` | `string` | The base currency code for the credit note. |
| `billing_address` | `object` | Details of the billing address associated with the credit note |
| `business_entity_id` | `string` | The ID of the business entity associated with the credit note. |
| `channel` | `string` | The channel through which the credit note was created. |
| `create_reason_code` | `string` | The reason code for creating the credit note. |
| `currency_code` | `string` | The currency code for the credit note. |
| `custom_fields` | `array` |  |
| `customer_id` | `string` | The ID of the customer associated with the credit note. |
| `customer_notes` | `string` | Notes provided by the customer for the credit note. |
| `date` | `integer` | The date when the credit note was created. |
| `deleted` | `boolean` | Indicates if the credit note has been deleted. |
| `discounts` | `array` | Details of discounts applied to the credit note |
| `exchange_rate` | `number` | The exchange rate used for currency conversion. |
| `fractional_correction` | `integer` | Fractional correction for rounding off decimals. |
| `generated_at` | `integer` | The date when the credit note was generated. |
| `id` | `string` | The unique identifier for the credit note. |
| `is_digital` | `boolean` | Indicates if the credit note is in digital format. |
| `is_vat_moss_registered` | `boolean` | Indicates if VAT MOSS registration applies. |
| `line_item_discounts` | `array` | Details of discounts applied at the line item level in the credit note |
| `line_item_taxes` | `array` | Details of taxes applied at the line item level in the credit note |
| `line_item_tiers` | `array` | Details of tiers applied to line items in the credit note |
| `line_items` | `array` | Details of line items in the credit note |
| `linked_refunds` | `array` | Details of linked refunds to the credit note |
| `linked_tax_withheld_refunds` | `array` | Details of linked tax withheld refunds to the credit note |
| `local_currency_code` | `string` | The local currency code for the credit note. |
| `object` | `string` | The object type of the credit note. |
| `price_type` | `string` | The type of pricing used for the credit note. |
| `reason_code` | `string` | The reason code for creating the credit note. |
| `reference_invoice_id` | `string` | The ID of the invoice this credit note references. |
| `refunded_at` | `integer` | The date when the credit note was refunded. |
| `resource_version` | `integer` | The version of the credit note resource. |
| `round_off_amount` | `integer` | Amount rounded off for currency conversions. |
| `shipping_address` | `object` | Details of the shipping address associated with the credit note |
| `status` | `string` | The status of the credit note. |
| `sub_total` | `integer` | The subtotal amount of the credit note. |
| `sub_total_in_local_currency` | `integer` | The subtotal amount in local currency. |
| `subscription_id` | `string` | The ID of the subscription associated with the credit note. |
| `taxes` | `array` | List of taxes applied to the credit note |
| `total` | `integer` | The total amount of the credit note. |
| `total_in_local_currency` | `integer` | The total amount in local currency. |
| `type` | `string` | The type of credit note. |
| `updated_at` | `integer` | The date when the credit note was last updated. |
| `vat_number` | `string` | VAT number associated with the credit note. |
| `vat_number_prefix` | `string` | Prefix for the VAT number. |
| `voided_at` | `integer` | The date when the credit note was voided. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].allocations` | `array` | Details of allocations associated with the credit note |
| `data[].amount_allocated` | `integer` | The amount of credits allocated. |
| `data[].amount_available` | `integer` | The amount of credits available. |
| `data[].amount_refunded` | `integer` | The amount of credits refunded. |
| `data[].base_currency_code` | `string` | The base currency code for the credit note. |
| `data[].billing_address` | `object` | Details of the billing address associated with the credit note |
| `data[].business_entity_id` | `string` | The ID of the business entity associated with the credit note. |
| `data[].channel` | `string` | The channel through which the credit note was created. |
| `data[].create_reason_code` | `string` | The reason code for creating the credit note. |
| `data[].currency_code` | `string` | The currency code for the credit note. |
| `data[].custom_fields` | `array` |  |
| `data[].customer_id` | `string` | The ID of the customer associated with the credit note. |
| `data[].customer_notes` | `string` | Notes provided by the customer for the credit note. |
| `data[].date` | `integer` | The date when the credit note was created. |
| `data[].deleted` | `boolean` | Indicates if the credit note has been deleted. |
| `data[].discounts` | `array` | Details of discounts applied to the credit note |
| `data[].exchange_rate` | `number` | The exchange rate used for currency conversion. |
| `data[].fractional_correction` | `integer` | Fractional correction for rounding off decimals. |
| `data[].generated_at` | `integer` | The date when the credit note was generated. |
| `data[].id` | `string` | The unique identifier for the credit note. |
| `data[].is_digital` | `boolean` | Indicates if the credit note is in digital format. |
| `data[].is_vat_moss_registered` | `boolean` | Indicates if VAT MOSS registration applies. |
| `data[].line_item_discounts` | `array` | Details of discounts applied at the line item level in the credit note |
| `data[].line_item_taxes` | `array` | Details of taxes applied at the line item level in the credit note |
| `data[].line_item_tiers` | `array` | Details of tiers applied to line items in the credit note |
| `data[].line_items` | `array` | Details of line items in the credit note |
| `data[].linked_refunds` | `array` | Details of linked refunds to the credit note |
| `data[].linked_tax_withheld_refunds` | `array` | Details of linked tax withheld refunds to the credit note |
| `data[].local_currency_code` | `string` | The local currency code for the credit note. |
| `data[].object` | `string` | The object type of the credit note. |
| `data[].price_type` | `string` | The type of pricing used for the credit note. |
| `data[].reason_code` | `string` | The reason code for creating the credit note. |
| `data[].reference_invoice_id` | `string` | The ID of the invoice this credit note references. |
| `data[].refunded_at` | `integer` | The date when the credit note was refunded. |
| `data[].resource_version` | `integer` | The version of the credit note resource. |
| `data[].round_off_amount` | `integer` | Amount rounded off for currency conversions. |
| `data[].shipping_address` | `object` | Details of the shipping address associated with the credit note |
| `data[].status` | `string` | The status of the credit note. |
| `data[].sub_total` | `integer` | The subtotal amount of the credit note. |
| `data[].sub_total_in_local_currency` | `integer` | The subtotal amount in local currency. |
| `data[].subscription_id` | `string` | The ID of the subscription associated with the credit note. |
| `data[].taxes` | `array` | List of taxes applied to the credit note |
| `data[].total` | `integer` | The total amount of the credit note. |
| `data[].total_in_local_currency` | `integer` | The total amount in local currency. |
| `data[].type` | `string` | The type of credit note. |
| `data[].updated_at` | `integer` | The date when the credit note was last updated. |
| `data[].vat_number` | `string` | VAT number associated with the credit note. |
| `data[].vat_number_prefix` | `string` | Prefix for the VAT number. |
| `data[].voided_at` | `integer` | The date when the credit note was voided. |

</details>

## Coupon

### Coupon List

List coupons

#### Python SDK

```python
await chargebee.coupon.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "coupon",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No |  |
| `offset` | `string` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `invoice_name` | `string` |  |
| `discount_type` | `string` |  |
| `discount_percentage` | `number` |  |
| `discount_amount` | `integer` |  |
| `discount_quantity` | `integer` |  |
| `currency_code` | `string` |  |
| `duration_type` | `string` |  |
| `duration_month` | `integer` |  |
| `valid_till` | `integer` |  |
| `max_redemptions` | `integer` |  |
| `status` | `string` |  |
| `apply_discount_on` | `string` |  |
| `apply_on` | `string` |  |
| `plan_constraint` | `string` |  |
| `addon_constraint` | `string` |  |
| `created_at` | `integer` |  |
| `archived_at` | `integer` |  |
| `resource_version` | `integer` |  |
| `updated_at` | `integer` |  |
| `object` | `string` |  |
| `redemptions` | `integer` |  |
| `invoice_notes` | `string` |  |
| `period` | `integer` |  |
| `period_unit` | `string` |  |
| `item_constraints` | `array<object>` |  |
| `item_constraint_criteria` | `array<object>` |  |
| `coupon_constraints` | `array<object>` |  |
| `deleted` | `boolean` |  |
| `custom_fields` | `array<object>` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_offset` | `string` |  |

</details>

### Coupon Get

Retrieve a coupon

#### Python SDK

```python
await chargebee.coupon.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "coupon",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Coupon ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `invoice_name` | `string` |  |
| `discount_type` | `string` |  |
| `discount_percentage` | `number` |  |
| `discount_amount` | `integer` |  |
| `discount_quantity` | `integer` |  |
| `currency_code` | `string` |  |
| `duration_type` | `string` |  |
| `duration_month` | `integer` |  |
| `valid_till` | `integer` |  |
| `max_redemptions` | `integer` |  |
| `status` | `string` |  |
| `apply_discount_on` | `string` |  |
| `apply_on` | `string` |  |
| `plan_constraint` | `string` |  |
| `addon_constraint` | `string` |  |
| `created_at` | `integer` |  |
| `archived_at` | `integer` |  |
| `resource_version` | `integer` |  |
| `updated_at` | `integer` |  |
| `object` | `string` |  |
| `redemptions` | `integer` |  |
| `invoice_notes` | `string` |  |
| `period` | `integer` |  |
| `period_unit` | `string` |  |
| `item_constraints` | `array<object>` |  |
| `item_constraint_criteria` | `array<object>` |  |
| `coupon_constraints` | `array<object>` |  |
| `deleted` | `boolean` |  |
| `custom_fields` | `array<object>` |  |


</details>

### Coupon Search

Search and filter coupon records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await chargebee.coupon.search(
    query={"filter": {"eq": {"apply_discount_on": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "coupon",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"apply_discount_on": "<str>"}}}
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
| `apply_discount_on` | `string` | Determines where the discount is applied on (e.g. subtotal, total). |
| `apply_on` | `string` | Specify on what type of items the coupon applies (e.g. subscription, addon). |
| `archived_at` | `integer` | Timestamp when the coupon was archived. |
| `coupon_constraints` | `array` | Represents the constraints associated with the coupon |
| `created_at` | `integer` | Timestamp of the coupon creation. |
| `currency_code` | `string` | The currency code for the coupon (e.g. USD, EUR). |
| `custom_fields` | `array` |  |
| `discount_amount` | `integer` | The fixed discount amount applied by the coupon. |
| `discount_percentage` | `number` | Percentage discount applied by the coupon. |
| `discount_quantity` | `integer` | Specifies the number of free units provided for the item price, without affecting the total quantity sold. This parameter is applicable only when the discount_type is set to offer_quantity. |
| `discount_type` | `string` | Type of discount (e.g. fixed, percentage). |
| `duration_month` | `integer` | Duration of the coupon in months. |
| `duration_type` | `string` | Type of duration (e.g. forever, one-time). |
| `id` | `string` | Unique identifier for the coupon. |
| `invoice_name` | `string` | Name displayed on invoices when the coupon is used. |
| `invoice_notes` | `string` | Additional notes displayed on invoices when the coupon is used. |
| `item_constraint_criteria` | `array` | Criteria for item constraints |
| `item_constraints` | `array` | Constraints related to the items |
| `max_redemptions` | `integer` | Maximum number of times the coupon can be redeemed. |
| `name` | `string` | Name of the coupon. |
| `object` | `string` | Type of object (usually 'coupon'). |
| `period` | `integer` | Duration or frequency for which the coupon is valid. |
| `period_unit` | `string` | Unit of the period (e.g. days, weeks). |
| `redemptions` | `integer` | Number of times the coupon has been redeemed. |
| `resource_version` | `integer` | Version of the resource. |
| `status` | `string` | Current status of the coupon (e.g. active, inactive). |
| `updated_at` | `integer` | Timestamp when the coupon was last updated. |
| `valid_till` | `integer` | Date until which the coupon is valid for use. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].apply_discount_on` | `string` | Determines where the discount is applied on (e.g. subtotal, total). |
| `data[].apply_on` | `string` | Specify on what type of items the coupon applies (e.g. subscription, addon). |
| `data[].archived_at` | `integer` | Timestamp when the coupon was archived. |
| `data[].coupon_constraints` | `array` | Represents the constraints associated with the coupon |
| `data[].created_at` | `integer` | Timestamp of the coupon creation. |
| `data[].currency_code` | `string` | The currency code for the coupon (e.g. USD, EUR). |
| `data[].custom_fields` | `array` |  |
| `data[].discount_amount` | `integer` | The fixed discount amount applied by the coupon. |
| `data[].discount_percentage` | `number` | Percentage discount applied by the coupon. |
| `data[].discount_quantity` | `integer` | Specifies the number of free units provided for the item price, without affecting the total quantity sold. This parameter is applicable only when the discount_type is set to offer_quantity. |
| `data[].discount_type` | `string` | Type of discount (e.g. fixed, percentage). |
| `data[].duration_month` | `integer` | Duration of the coupon in months. |
| `data[].duration_type` | `string` | Type of duration (e.g. forever, one-time). |
| `data[].id` | `string` | Unique identifier for the coupon. |
| `data[].invoice_name` | `string` | Name displayed on invoices when the coupon is used. |
| `data[].invoice_notes` | `string` | Additional notes displayed on invoices when the coupon is used. |
| `data[].item_constraint_criteria` | `array` | Criteria for item constraints |
| `data[].item_constraints` | `array` | Constraints related to the items |
| `data[].max_redemptions` | `integer` | Maximum number of times the coupon can be redeemed. |
| `data[].name` | `string` | Name of the coupon. |
| `data[].object` | `string` | Type of object (usually 'coupon'). |
| `data[].period` | `integer` | Duration or frequency for which the coupon is valid. |
| `data[].period_unit` | `string` | Unit of the period (e.g. days, weeks). |
| `data[].redemptions` | `integer` | Number of times the coupon has been redeemed. |
| `data[].resource_version` | `integer` | Version of the resource. |
| `data[].status` | `string` | Current status of the coupon (e.g. active, inactive). |
| `data[].updated_at` | `integer` | Timestamp when the coupon was last updated. |
| `data[].valid_till` | `integer` | Date until which the coupon is valid for use. |

</details>

## Transaction

### Transaction List

List transactions

#### Python SDK

```python
await chargebee.transaction.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "transaction",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No |  |
| `offset` | `string` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `customer_id` | `string` |  |
| `subscription_id` | `string` |  |
| `gateway_account_id` | `string` |  |
| `payment_source_id` | `string` |  |
| `payment_method` | `string` |  |
| `reference_number` | `string` |  |
| `gateway` | `string` |  |
| `type` | `string` |  |
| `date` | `integer` |  |
| `settled_at` | `integer` |  |
| `exchange_rate` | `number` |  |
| `currency_code` | `string` |  |
| `amount` | `integer` |  |
| `id_at_gateway` | `string` |  |
| `status` | `string` |  |
| `fraud_flag` | `string` |  |
| `initiator_type` | `string` |  |
| `three_d_secure` | `boolean` |  |
| `authorization_reason` | `string` |  |
| `error_code` | `string` |  |
| `error_text` | `string` |  |
| `voided_at` | `integer` |  |
| `resource_version` | `integer` |  |
| `updated_at` | `integer` |  |
| `fraud_reason` | `string` |  |
| `amount_unused` | `integer` |  |
| `masked_card_number` | `string` |  |
| `reference_transaction_id` | `string` |  |
| `refunded_txn_id` | `string` |  |
| `reference_authorization_id` | `string` |  |
| `amount_capturable` | `integer` |  |
| `reversal_transaction_id` | `string` |  |
| `deleted` | `boolean` |  |
| `iin` | `string` |  |
| `last4` | `string` |  |
| `merchant_reference_id` | `string` |  |
| `business_entity_id` | `string` |  |
| `payment_method_details` | `any` |  |
| `object` | `string` |  |
| `base_currency_code` | `string` |  |
| `linked_invoices` | `array<object>` |  |
| `linked_credit_notes` | `array<object>` |  |
| `linked_refunds` | `array<object>` |  |
| `linked_payments` | `array<object>` |  |
| `custom_fields` | `array<object>` |  |
| `created_at` | `integer` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_offset` | `string` |  |

</details>

### Transaction Get

Retrieve a transaction

#### Python SDK

```python
await chargebee.transaction.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "transaction",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Transaction ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `customer_id` | `string` |  |
| `subscription_id` | `string` |  |
| `gateway_account_id` | `string` |  |
| `payment_source_id` | `string` |  |
| `payment_method` | `string` |  |
| `reference_number` | `string` |  |
| `gateway` | `string` |  |
| `type` | `string` |  |
| `date` | `integer` |  |
| `settled_at` | `integer` |  |
| `exchange_rate` | `number` |  |
| `currency_code` | `string` |  |
| `amount` | `integer` |  |
| `id_at_gateway` | `string` |  |
| `status` | `string` |  |
| `fraud_flag` | `string` |  |
| `initiator_type` | `string` |  |
| `three_d_secure` | `boolean` |  |
| `authorization_reason` | `string` |  |
| `error_code` | `string` |  |
| `error_text` | `string` |  |
| `voided_at` | `integer` |  |
| `resource_version` | `integer` |  |
| `updated_at` | `integer` |  |
| `fraud_reason` | `string` |  |
| `amount_unused` | `integer` |  |
| `masked_card_number` | `string` |  |
| `reference_transaction_id` | `string` |  |
| `refunded_txn_id` | `string` |  |
| `reference_authorization_id` | `string` |  |
| `amount_capturable` | `integer` |  |
| `reversal_transaction_id` | `string` |  |
| `deleted` | `boolean` |  |
| `iin` | `string` |  |
| `last4` | `string` |  |
| `merchant_reference_id` | `string` |  |
| `business_entity_id` | `string` |  |
| `payment_method_details` | `any` |  |
| `object` | `string` |  |
| `base_currency_code` | `string` |  |
| `linked_invoices` | `array<object>` |  |
| `linked_credit_notes` | `array<object>` |  |
| `linked_refunds` | `array<object>` |  |
| `linked_payments` | `array<object>` |  |
| `custom_fields` | `array<object>` |  |
| `created_at` | `integer` |  |


</details>

### Transaction Search

Search and filter transaction records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await chargebee.transaction.search(
    query={"filter": {"eq": {"amount": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "transaction",
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `amount` | `integer` | The total amount of the transaction. |
| `amount_capturable` | `integer` | The remaining amount that can be captured in the transaction. |
| `amount_unused` | `integer` | The amount in the transaction that remains unused. |
| `authorization_reason` | `string` | Reason for authorization of the transaction. |
| `base_currency_code` | `string` | The base currency code of the transaction. |
| `business_entity_id` | `string` | The ID of the business entity related to the transaction. |
| `cn_create_reason_code` | `string` | Reason code for creating a credit note. |
| `cn_date` | `integer` | Date of the credit note. |
| `cn_reference_invoice_id` | `string` | ID of the invoice referenced in the credit note. |
| `cn_status` | `string` | Status of the credit note. |
| `cn_total` | `integer` | Total amount of the credit note. |
| `currency_code` | `string` | The currency code of the transaction. |
| `custom_fields` | `array` |  |
| `customer_id` | `string` | The ID of the customer associated with the transaction. |
| `date` | `integer` | Date of the transaction. |
| `deleted` | `boolean` | Flag indicating if the transaction is deleted. |
| `error_code` | `string` | Error code associated with the transaction. |
| `error_detail` | `string` | Detailed error information related to the transaction. |
| `error_text` | `string` | Error message text of the transaction. |
| `exchange_rate` | `number` | Exchange rate used in the transaction. |
| `fraud_flag` | `string` | Flag indicating if the transaction is flagged for fraud. |
| `fraud_reason` | `string` | Reason for flagging the transaction as fraud. |
| `gateway` | `string` | The payment gateway used in the transaction. |
| `gateway_account_id` | `string` | ID of the gateway account used in the transaction. |
| `id` | `string` | Unique identifier of the transaction. |
| `id_at_gateway` | `string` | Transaction ID assigned by the gateway. |
| `iin` | `string` | Bank identification number of the transaction. |
| `initiator_type` | `string` | Type of initiator involved in the transaction. |
| `last4` | `string` | Last 4 digits of the card used in the transaction. |
| `linked_credit_notes` | `array` | Linked credit notes associated with the transaction. |
| `linked_invoices` | `array` | Linked invoices associated with the transaction. |
| `linked_payments` | `array` | Linked payments associated with the transaction. |
| `linked_refunds` | `array` | Linked refunds associated with the transaction. |
| `masked_card_number` | `string` | Masked card number used in the transaction. |
| `merchant_reference_id` | `string` | Merchant reference ID of the transaction. |
| `object` | `string` | Type of object representing the transaction. |
| `payment_method` | `string` | Payment method used in the transaction. |
| `payment_method_details` | `string` | Details of the payment method used in the transaction. |
| `payment_source_id` | `string` | ID of the payment source used in the transaction. |
| `reference_authorization_id` | `string` | Reference authorization ID of the transaction. |
| `reference_number` | `string` | Reference number associated with the transaction. |
| `reference_transaction_id` | `string` | ID of the reference transaction. |
| `refrence_number` | `string` | Reference number of the transaction. |
| `refunded_txn_id` | `string` | ID of the refunded transaction. |
| `resource_version` | `integer` | Resource version of the transaction. |
| `reversal_transaction_id` | `string` | ID of the reversal transaction, if any. |
| `settled_at` | `integer` | Date when the transaction was settled. |
| `status` | `string` | Status of the transaction. |
| `subscription_id` | `string` | ID of the subscription related to the transaction. |
| `three_d_secure` | `boolean` | Flag indicating if 3D secure was used in the transaction. |
| `txn_amount` | `integer` | Amount of the transaction. |
| `txn_date` | `integer` | Date of the transaction. |
| `type` | `string` | Type of the transaction. |
| `updated_at` | `integer` | Date when the transaction was last updated. |
| `voided_at` | `integer` | Date when the transaction was voided. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].amount` | `integer` | The total amount of the transaction. |
| `data[].amount_capturable` | `integer` | The remaining amount that can be captured in the transaction. |
| `data[].amount_unused` | `integer` | The amount in the transaction that remains unused. |
| `data[].authorization_reason` | `string` | Reason for authorization of the transaction. |
| `data[].base_currency_code` | `string` | The base currency code of the transaction. |
| `data[].business_entity_id` | `string` | The ID of the business entity related to the transaction. |
| `data[].cn_create_reason_code` | `string` | Reason code for creating a credit note. |
| `data[].cn_date` | `integer` | Date of the credit note. |
| `data[].cn_reference_invoice_id` | `string` | ID of the invoice referenced in the credit note. |
| `data[].cn_status` | `string` | Status of the credit note. |
| `data[].cn_total` | `integer` | Total amount of the credit note. |
| `data[].currency_code` | `string` | The currency code of the transaction. |
| `data[].custom_fields` | `array` |  |
| `data[].customer_id` | `string` | The ID of the customer associated with the transaction. |
| `data[].date` | `integer` | Date of the transaction. |
| `data[].deleted` | `boolean` | Flag indicating if the transaction is deleted. |
| `data[].error_code` | `string` | Error code associated with the transaction. |
| `data[].error_detail` | `string` | Detailed error information related to the transaction. |
| `data[].error_text` | `string` | Error message text of the transaction. |
| `data[].exchange_rate` | `number` | Exchange rate used in the transaction. |
| `data[].fraud_flag` | `string` | Flag indicating if the transaction is flagged for fraud. |
| `data[].fraud_reason` | `string` | Reason for flagging the transaction as fraud. |
| `data[].gateway` | `string` | The payment gateway used in the transaction. |
| `data[].gateway_account_id` | `string` | ID of the gateway account used in the transaction. |
| `data[].id` | `string` | Unique identifier of the transaction. |
| `data[].id_at_gateway` | `string` | Transaction ID assigned by the gateway. |
| `data[].iin` | `string` | Bank identification number of the transaction. |
| `data[].initiator_type` | `string` | Type of initiator involved in the transaction. |
| `data[].last4` | `string` | Last 4 digits of the card used in the transaction. |
| `data[].linked_credit_notes` | `array` | Linked credit notes associated with the transaction. |
| `data[].linked_invoices` | `array` | Linked invoices associated with the transaction. |
| `data[].linked_payments` | `array` | Linked payments associated with the transaction. |
| `data[].linked_refunds` | `array` | Linked refunds associated with the transaction. |
| `data[].masked_card_number` | `string` | Masked card number used in the transaction. |
| `data[].merchant_reference_id` | `string` | Merchant reference ID of the transaction. |
| `data[].object` | `string` | Type of object representing the transaction. |
| `data[].payment_method` | `string` | Payment method used in the transaction. |
| `data[].payment_method_details` | `string` | Details of the payment method used in the transaction. |
| `data[].payment_source_id` | `string` | ID of the payment source used in the transaction. |
| `data[].reference_authorization_id` | `string` | Reference authorization ID of the transaction. |
| `data[].reference_number` | `string` | Reference number associated with the transaction. |
| `data[].reference_transaction_id` | `string` | ID of the reference transaction. |
| `data[].refrence_number` | `string` | Reference number of the transaction. |
| `data[].refunded_txn_id` | `string` | ID of the refunded transaction. |
| `data[].resource_version` | `integer` | Resource version of the transaction. |
| `data[].reversal_transaction_id` | `string` | ID of the reversal transaction, if any. |
| `data[].settled_at` | `integer` | Date when the transaction was settled. |
| `data[].status` | `string` | Status of the transaction. |
| `data[].subscription_id` | `string` | ID of the subscription related to the transaction. |
| `data[].three_d_secure` | `boolean` | Flag indicating if 3D secure was used in the transaction. |
| `data[].txn_amount` | `integer` | Amount of the transaction. |
| `data[].txn_date` | `integer` | Date of the transaction. |
| `data[].type` | `string` | Type of the transaction. |
| `data[].updated_at` | `integer` | Date when the transaction was last updated. |
| `data[].voided_at` | `integer` | Date when the transaction was voided. |

</details>

## Event

### Event List

List events

#### Python SDK

```python
await chargebee.event.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "event",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No |  |
| `offset` | `string` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `occurred_at` | `integer` |  |
| `source` | `string` |  |
| `user` | `string` |  |
| `event_type` | `string` |  |
| `api_version` | `string` |  |
| `content` | `object` |  |
| `object` | `string` |  |
| `webhook_status` | `string` |  |
| `webhooks` | `array<object>` |  |
| `custom_fields` | `array<object>` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_offset` | `string` |  |

</details>

### Event Get

Retrieve an event

#### Python SDK

```python
await chargebee.event.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "event",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Event ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `occurred_at` | `integer` |  |
| `source` | `string` |  |
| `user` | `string` |  |
| `event_type` | `string` |  |
| `api_version` | `string` |  |
| `content` | `object` |  |
| `object` | `string` |  |
| `webhook_status` | `string` |  |
| `webhooks` | `array<object>` |  |
| `custom_fields` | `array<object>` |  |


</details>

### Event Search

Search and filter event records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await chargebee.event.search(
    query={"filter": {"eq": {"api_version": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "event",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"api_version": "<str>"}}}
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
| `api_version` | `string` | The version of the Chargebee API being used to fetch the event data. |
| `content` | `object` | The specific content or information associated with the event. |
| `custom_fields` | `array` |  |
| `event_type` | `string` | The type or category of the event. |
| `id` | `string` | Unique identifier for the event data record. |
| `object` | `string` | The object or entity that the event is triggered for. |
| `occurred_at` | `integer` | The datetime when the event occurred. |
| `source` | `string` | The source or origin of the event data. |
| `user` | `string` | Information about the user or entity associated with the event. |
| `webhook_status` | `string` | The status of the webhook execution for the event. |
| `webhooks` | `array` | List of webhooks associated with the event. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].api_version` | `string` | The version of the Chargebee API being used to fetch the event data. |
| `data[].content` | `object` | The specific content or information associated with the event. |
| `data[].custom_fields` | `array` |  |
| `data[].event_type` | `string` | The type or category of the event. |
| `data[].id` | `string` | Unique identifier for the event data record. |
| `data[].object` | `string` | The object or entity that the event is triggered for. |
| `data[].occurred_at` | `integer` | The datetime when the event occurred. |
| `data[].source` | `string` | The source or origin of the event data. |
| `data[].user` | `string` | Information about the user or entity associated with the event. |
| `data[].webhook_status` | `string` | The status of the webhook execution for the event. |
| `data[].webhooks` | `array` | List of webhooks associated with the event. |

</details>

## Order

### Order List

List orders

#### Python SDK

```python
await chargebee.order.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "order",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No |  |
| `offset` | `string` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `document_number` | `string` |  |
| `invoice_id` | `string` |  |
| `subscription_id` | `string` |  |
| `customer_id` | `string` |  |
| `status` | `string` |  |
| `cancellation_reason` | `string` |  |
| `payment_status` | `string` |  |
| `order_type` | `string` |  |
| `price_type` | `string` |  |
| `reference_id` | `string` |  |
| `fulfillment_status` | `string` |  |
| `order_date` | `integer` |  |
| `shipping_date` | `integer` |  |
| `note` | `string` |  |
| `tracking_id` | `string` |  |
| `tracking_url` | `string` |  |
| `batch_id` | `string` |  |
| `created_by` | `string` |  |
| `shipment_carrier` | `string` |  |
| `invoice_round_off_amount` | `integer` |  |
| `tax` | `integer` |  |
| `amount_paid` | `integer` |  |
| `amount_adjusted` | `integer` |  |
| `refundable_credits_issued` | `integer` |  |
| `refundable_credits` | `integer` |  |
| `rounding_adjustement` | `integer` |  |
| `paid_on` | `integer` |  |
| `shipping_cut_off_date` | `integer` |  |
| `created_at` | `integer` |  |
| `status_update_at` | `integer` |  |
| `delivered_at` | `integer` |  |
| `shipped_at` | `integer` |  |
| `resource_version` | `integer` |  |
| `updated_at` | `integer` |  |
| `cancelled_at` | `integer` |  |
| `resent_status` | `string` |  |
| `is_resent` | `boolean` |  |
| `original_order_id` | `string` |  |
| `deleted` | `boolean` |  |
| `currency_code` | `string` |  |
| `is_gifted` | `boolean` |  |
| `gift_note` | `string` |  |
| `gift_id` | `string` |  |
| `resend_reason` | `string` |  |
| `business_entity_id` | `string` |  |
| `object` | `string` |  |
| `discount` | `integer` |  |
| `sub_total` | `integer` |  |
| `total` | `integer` |  |
| `order_line_items` | `array<object>` |  |
| `shipping_address` | `object` |  |
| `billing_address` | `object` |  |
| `line_item_taxes` | `array<object>` |  |
| `line_item_discounts` | `array<object>` |  |
| `linked_credit_notes` | `array<object>` |  |
| `resent_orders` | `array<object>` |  |
| `custom_fields` | `array<object>` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_offset` | `string` |  |

</details>

### Order Get

Retrieve an order

#### Python SDK

```python
await chargebee.order.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "order",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Order ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `document_number` | `string` |  |
| `invoice_id` | `string` |  |
| `subscription_id` | `string` |  |
| `customer_id` | `string` |  |
| `status` | `string` |  |
| `cancellation_reason` | `string` |  |
| `payment_status` | `string` |  |
| `order_type` | `string` |  |
| `price_type` | `string` |  |
| `reference_id` | `string` |  |
| `fulfillment_status` | `string` |  |
| `order_date` | `integer` |  |
| `shipping_date` | `integer` |  |
| `note` | `string` |  |
| `tracking_id` | `string` |  |
| `tracking_url` | `string` |  |
| `batch_id` | `string` |  |
| `created_by` | `string` |  |
| `shipment_carrier` | `string` |  |
| `invoice_round_off_amount` | `integer` |  |
| `tax` | `integer` |  |
| `amount_paid` | `integer` |  |
| `amount_adjusted` | `integer` |  |
| `refundable_credits_issued` | `integer` |  |
| `refundable_credits` | `integer` |  |
| `rounding_adjustement` | `integer` |  |
| `paid_on` | `integer` |  |
| `shipping_cut_off_date` | `integer` |  |
| `created_at` | `integer` |  |
| `status_update_at` | `integer` |  |
| `delivered_at` | `integer` |  |
| `shipped_at` | `integer` |  |
| `resource_version` | `integer` |  |
| `updated_at` | `integer` |  |
| `cancelled_at` | `integer` |  |
| `resent_status` | `string` |  |
| `is_resent` | `boolean` |  |
| `original_order_id` | `string` |  |
| `deleted` | `boolean` |  |
| `currency_code` | `string` |  |
| `is_gifted` | `boolean` |  |
| `gift_note` | `string` |  |
| `gift_id` | `string` |  |
| `resend_reason` | `string` |  |
| `business_entity_id` | `string` |  |
| `object` | `string` |  |
| `discount` | `integer` |  |
| `sub_total` | `integer` |  |
| `total` | `integer` |  |
| `order_line_items` | `array<object>` |  |
| `shipping_address` | `object` |  |
| `billing_address` | `object` |  |
| `line_item_taxes` | `array<object>` |  |
| `line_item_discounts` | `array<object>` |  |
| `linked_credit_notes` | `array<object>` |  |
| `resent_orders` | `array<object>` |  |
| `custom_fields` | `array<object>` |  |


</details>

### Order Search

Search and filter order records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await chargebee.order.search(
    query={"filter": {"eq": {"amount_adjusted": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "order",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"amount_adjusted": 0}}}
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
| `amount_adjusted` | `integer` | Adjusted amount for the order. |
| `amount_paid` | `integer` | Amount paid for the order. |
| `base_currency_code` | `string` | The base currency code used for the order. |
| `batch_id` | `string` | Unique identifier for the batch the order belongs to. |
| `billing_address` | `object` | The billing address associated with the order |
| `business_entity_id` | `string` | Identifier for the business entity associated with the order. |
| `cancellation_reason` | `string` | Reason for order cancellation. |
| `cancelled_at` | `integer` | Timestamp when the order was cancelled. |
| `created_at` | `integer` | Timestamp when the order was created. |
| `created_by` | `string` | User or system that created the order. |
| `currency_code` | `string` | Currency code used for the order. |
| `custom_fields` | `array` |  |
| `customer_id` | `string` | Identifier for the customer placing the order. |
| `deleted` | `boolean` | Flag indicating if the order has been deleted. |
| `delivered_at` | `integer` | Timestamp when the order was delivered. |
| `discount` | `integer` | Discount amount applied to the order. |
| `document_number` | `string` | Unique document number associated with the order. |
| `exchange_rate` | `number` | Rate used for currency exchange in the order. |
| `fulfillment_status` | `string` | Status of fulfillment for the order. |
| `gift_id` | `string` | Identifier for any gift associated with the order. |
| `gift_note` | `string` | Note attached to any gift in the order. |
| `id` | `string` | Unique identifier for the order. |
| `invoice_id` | `string` | Identifier for the invoice associated with the order. |
| `invoice_round_off_amount` | `integer` | Round-off amount applied to the invoice. |
| `is_gifted` | `boolean` | Flag indicating if the order is a gift. |
| `is_resent` | `boolean` | Flag indicating if the order has been resent. |
| `line_item_discounts` | `array` | Discounts applied to individual line items |
| `line_item_taxes` | `array` | Taxes applied to individual line items |
| `linked_credit_notes` | `array` | Credit notes linked to the order |
| `note` | `string` | Additional notes or comments for the order. |
| `object` | `string` | Type of object representing an order in the system. |
| `order_date` | `integer` | Date when the order was created. |
| `order_line_items` | `array` | List of line items in the order |
| `order_type` | `string` | Type of order such as purchase order or sales order. |
| `original_order_id` | `string` | Identifier for the original order if this is a modified order. |
| `paid_on` | `integer` | Timestamp when the order was paid for. |
| `payment_status` | `string` | Status of payment for the order. |
| `price_type` | `string` | Type of pricing used for the order. |
| `reference_id` | `string` | Reference identifier for the order. |
| `refundable_credits` | `integer` | Credits that can be refunded for the whole order. |
| `refundable_credits_issued` | `integer` | Credits already issued for refund for the whole order. |
| `resend_reason` | `string` | Reason for resending the order. |
| `resent_orders` | `array` | Orders that were resent to the customer |
| `resent_status` | `string` | Status of the resent order. |
| `resource_version` | `integer` | Version of the resource or order data. |
| `rounding_adjustement` | `integer` | Adjustment made for rounding off the order amount. |
| `shipment_carrier` | `string` | Carrier for shipping the order. |
| `shipped_at` | `integer` | Timestamp when the order was shipped. |
| `shipping_address` | `object` | The shipping address for the order |
| `shipping_cut_off_date` | `integer` | Date indicating the shipping cut-off for the order. |
| `shipping_date` | `integer` | Date when the order is scheduled for shipping. |
| `status` | `string` | Current status of the order. |
| `status_update_at` | `integer` | Timestamp when the status of the order was last updated. |
| `sub_total` | `integer` | Sub-total amount for the order before applying taxes or discounts. |
| `subscription_id` | `string` | Identifier for the subscription associated with the order. |
| `tax` | `integer` | Total tax amount for the order. |
| `total` | `integer` | Total amount including taxes and discounts for the order. |
| `tracking_id` | `string` | Tracking identifier for the order shipment. |
| `tracking_url` | `string` | URL for tracking the order shipment. |
| `updated_at` | `integer` | Timestamp when the order data was last updated. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].amount_adjusted` | `integer` | Adjusted amount for the order. |
| `data[].amount_paid` | `integer` | Amount paid for the order. |
| `data[].base_currency_code` | `string` | The base currency code used for the order. |
| `data[].batch_id` | `string` | Unique identifier for the batch the order belongs to. |
| `data[].billing_address` | `object` | The billing address associated with the order |
| `data[].business_entity_id` | `string` | Identifier for the business entity associated with the order. |
| `data[].cancellation_reason` | `string` | Reason for order cancellation. |
| `data[].cancelled_at` | `integer` | Timestamp when the order was cancelled. |
| `data[].created_at` | `integer` | Timestamp when the order was created. |
| `data[].created_by` | `string` | User or system that created the order. |
| `data[].currency_code` | `string` | Currency code used for the order. |
| `data[].custom_fields` | `array` |  |
| `data[].customer_id` | `string` | Identifier for the customer placing the order. |
| `data[].deleted` | `boolean` | Flag indicating if the order has been deleted. |
| `data[].delivered_at` | `integer` | Timestamp when the order was delivered. |
| `data[].discount` | `integer` | Discount amount applied to the order. |
| `data[].document_number` | `string` | Unique document number associated with the order. |
| `data[].exchange_rate` | `number` | Rate used for currency exchange in the order. |
| `data[].fulfillment_status` | `string` | Status of fulfillment for the order. |
| `data[].gift_id` | `string` | Identifier for any gift associated with the order. |
| `data[].gift_note` | `string` | Note attached to any gift in the order. |
| `data[].id` | `string` | Unique identifier for the order. |
| `data[].invoice_id` | `string` | Identifier for the invoice associated with the order. |
| `data[].invoice_round_off_amount` | `integer` | Round-off amount applied to the invoice. |
| `data[].is_gifted` | `boolean` | Flag indicating if the order is a gift. |
| `data[].is_resent` | `boolean` | Flag indicating if the order has been resent. |
| `data[].line_item_discounts` | `array` | Discounts applied to individual line items |
| `data[].line_item_taxes` | `array` | Taxes applied to individual line items |
| `data[].linked_credit_notes` | `array` | Credit notes linked to the order |
| `data[].note` | `string` | Additional notes or comments for the order. |
| `data[].object` | `string` | Type of object representing an order in the system. |
| `data[].order_date` | `integer` | Date when the order was created. |
| `data[].order_line_items` | `array` | List of line items in the order |
| `data[].order_type` | `string` | Type of order such as purchase order or sales order. |
| `data[].original_order_id` | `string` | Identifier for the original order if this is a modified order. |
| `data[].paid_on` | `integer` | Timestamp when the order was paid for. |
| `data[].payment_status` | `string` | Status of payment for the order. |
| `data[].price_type` | `string` | Type of pricing used for the order. |
| `data[].reference_id` | `string` | Reference identifier for the order. |
| `data[].refundable_credits` | `integer` | Credits that can be refunded for the whole order. |
| `data[].refundable_credits_issued` | `integer` | Credits already issued for refund for the whole order. |
| `data[].resend_reason` | `string` | Reason for resending the order. |
| `data[].resent_orders` | `array` | Orders that were resent to the customer |
| `data[].resent_status` | `string` | Status of the resent order. |
| `data[].resource_version` | `integer` | Version of the resource or order data. |
| `data[].rounding_adjustement` | `integer` | Adjustment made for rounding off the order amount. |
| `data[].shipment_carrier` | `string` | Carrier for shipping the order. |
| `data[].shipped_at` | `integer` | Timestamp when the order was shipped. |
| `data[].shipping_address` | `object` | The shipping address for the order |
| `data[].shipping_cut_off_date` | `integer` | Date indicating the shipping cut-off for the order. |
| `data[].shipping_date` | `integer` | Date when the order is scheduled for shipping. |
| `data[].status` | `string` | Current status of the order. |
| `data[].status_update_at` | `integer` | Timestamp when the status of the order was last updated. |
| `data[].sub_total` | `integer` | Sub-total amount for the order before applying taxes or discounts. |
| `data[].subscription_id` | `string` | Identifier for the subscription associated with the order. |
| `data[].tax` | `integer` | Total tax amount for the order. |
| `data[].total` | `integer` | Total amount including taxes and discounts for the order. |
| `data[].tracking_id` | `string` | Tracking identifier for the order shipment. |
| `data[].tracking_url` | `string` | URL for tracking the order shipment. |
| `data[].updated_at` | `integer` | Timestamp when the order data was last updated. |

</details>

## Item

### Item List

List items

#### Python SDK

```python
await chargebee.item.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "item",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No |  |
| `offset` | `string` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `external_name` | `string` |  |
| `description` | `string` |  |
| `status` | `string` |  |
| `resource_version` | `integer` |  |
| `updated_at` | `integer` |  |
| `item_family_id` | `string` |  |
| `type` | `string` |  |
| `is_shippable` | `boolean` |  |
| `is_giftable` | `boolean` |  |
| `redirect_url` | `string` |  |
| `enabled_for_checkout` | `boolean` |  |
| `enabled_in_portal` | `boolean` |  |
| `included_in_mrr` | `boolean` |  |
| `item_applicability` | `string` |  |
| `gift_claim_redirect_url` | `string` |  |
| `unit` | `string` |  |
| `metered` | `boolean` |  |
| `usage_calculation` | `string` |  |
| `archived_at` | `integer` |  |
| `channel` | `string` |  |
| `metadata` | `object` |  |
| `deleted` | `boolean` |  |
| `object` | `string` |  |
| `applicable_items` | `array<object>` |  |
| `bundle_items` | `array<object>` |  |
| `bundle_configuration` | `object` |  |
| `business_entity_id` | `string` |  |
| `is_percentage_pricing` | `boolean` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_offset` | `string` |  |

</details>

### Item Get

Retrieve an item

#### Python SDK

```python
await chargebee.item.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "item",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Item ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `external_name` | `string` |  |
| `description` | `string` |  |
| `status` | `string` |  |
| `resource_version` | `integer` |  |
| `updated_at` | `integer` |  |
| `item_family_id` | `string` |  |
| `type` | `string` |  |
| `is_shippable` | `boolean` |  |
| `is_giftable` | `boolean` |  |
| `redirect_url` | `string` |  |
| `enabled_for_checkout` | `boolean` |  |
| `enabled_in_portal` | `boolean` |  |
| `included_in_mrr` | `boolean` |  |
| `item_applicability` | `string` |  |
| `gift_claim_redirect_url` | `string` |  |
| `unit` | `string` |  |
| `metered` | `boolean` |  |
| `usage_calculation` | `string` |  |
| `archived_at` | `integer` |  |
| `channel` | `string` |  |
| `metadata` | `object` |  |
| `deleted` | `boolean` |  |
| `object` | `string` |  |
| `applicable_items` | `array<object>` |  |
| `bundle_items` | `array<object>` |  |
| `bundle_configuration` | `object` |  |
| `business_entity_id` | `string` |  |
| `is_percentage_pricing` | `boolean` |  |


</details>

### Item Search

Search and filter item records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await chargebee.item.search(
    query={"filter": {"eq": {"applicable_items": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "item",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"applicable_items": []}}}
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
| `applicable_items` | `array` | Items associated with the item |
| `archived_at` | `integer` | Date and time when the item was archived |
| `channel` | `string` | Channel the item belongs to |
| `custom_fields` | `array` | Custom field entries for the item |
| `description` | `string` | Description of the item |
| `enabled_for_checkout` | `boolean` | Flag indicating if the item is enabled for checkout |
| `enabled_in_portal` | `boolean` | Flag indicating if the item is enabled in the portal |
| `external_name` | `string` | Name of the item in an external system |
| `gift_claim_redirect_url` | `string` | URL to redirect for gift claim |
| `id` | `string` | Unique identifier for the item |
| `included_in_mrr` | `boolean` | Flag indicating if the item is included in Monthly Recurring Revenue |
| `is_giftable` | `boolean` | Flag indicating if the item is giftable |
| `is_shippable` | `boolean` | Flag indicating if the item is shippable |
| `item_applicability` | `string` | Applicability of the item |
| `item_family_id` | `string` | ID of the item's family |
| `metadata` | `object` | Additional data associated with the item |
| `metered` | `boolean` | Flag indicating if the item is metered |
| `name` | `string` | Name of the item |
| `object` | `string` | Type of object |
| `redirect_url` | `string` | URL to redirect for the item |
| `resource_version` | `integer` | Version of the resource |
| `status` | `string` | Status of the item |
| `type` | `string` | Type of the item |
| `unit` | `string` | Unit associated with the item |
| `updated_at` | `integer` | Date and time when the item was last updated |
| `usage_calculation` | `string` | Calculation method used for item usage |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].applicable_items` | `array` | Items associated with the item |
| `data[].archived_at` | `integer` | Date and time when the item was archived |
| `data[].channel` | `string` | Channel the item belongs to |
| `data[].custom_fields` | `array` | Custom field entries for the item |
| `data[].description` | `string` | Description of the item |
| `data[].enabled_for_checkout` | `boolean` | Flag indicating if the item is enabled for checkout |
| `data[].enabled_in_portal` | `boolean` | Flag indicating if the item is enabled in the portal |
| `data[].external_name` | `string` | Name of the item in an external system |
| `data[].gift_claim_redirect_url` | `string` | URL to redirect for gift claim |
| `data[].id` | `string` | Unique identifier for the item |
| `data[].included_in_mrr` | `boolean` | Flag indicating if the item is included in Monthly Recurring Revenue |
| `data[].is_giftable` | `boolean` | Flag indicating if the item is giftable |
| `data[].is_shippable` | `boolean` | Flag indicating if the item is shippable |
| `data[].item_applicability` | `string` | Applicability of the item |
| `data[].item_family_id` | `string` | ID of the item's family |
| `data[].metadata` | `object` | Additional data associated with the item |
| `data[].metered` | `boolean` | Flag indicating if the item is metered |
| `data[].name` | `string` | Name of the item |
| `data[].object` | `string` | Type of object |
| `data[].redirect_url` | `string` | URL to redirect for the item |
| `data[].resource_version` | `integer` | Version of the resource |
| `data[].status` | `string` | Status of the item |
| `data[].type` | `string` | Type of the item |
| `data[].unit` | `string` | Unit associated with the item |
| `data[].updated_at` | `integer` | Date and time when the item was last updated |
| `data[].usage_calculation` | `string` | Calculation method used for item usage |

</details>

## Item Price

### Item Price List

List item prices

#### Python SDK

```python
await chargebee.item_price.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "item_price",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No |  |
| `offset` | `string` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `item_family_id` | `string` |  |
| `item_id` | `string` |  |
| `item_type` | `string` |  |
| `description` | `string` |  |
| `status` | `string` |  |
| `external_name` | `string` |  |
| `pricing_model` | `string` |  |
| `price` | `integer` |  |
| `price_in_decimal` | `string` |  |
| `period` | `integer` |  |
| `period_unit` | `string` |  |
| `trial_period` | `integer` |  |
| `trial_period_unit` | `string` |  |
| `trial_end_action` | `string` |  |
| `shipping_period` | `integer` |  |
| `shipping_period_unit` | `string` |  |
| `billing_cycles` | `integer` |  |
| `free_quantity` | `integer` |  |
| `free_quantity_in_decimal` | `string` |  |
| `currency_code` | `string` |  |
| `resource_version` | `integer` |  |
| `updated_at` | `integer` |  |
| `created_at` | `integer` |  |
| `archived_at` | `integer` |  |
| `invoice_notes` | `string` |  |
| `is_taxable` | `boolean` |  |
| `metadata` | `object` |  |
| `tax_detail` | `object` |  |
| `accounting_detail` | `object` |  |
| `tiers` | `array<object>` |  |
| `tax_providers_fields` | `array<object>` |  |
| `object` | `string` |  |
| `channel` | `string` |  |
| `show_description_in_invoices` | `boolean` |  |
| `show_description_in_quotes` | `boolean` |  |
| `business_entity_id` | `string` |  |
| `deleted` | `boolean` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_offset` | `string` |  |

</details>

### Item Price Get

Retrieve an item price

#### Python SDK

```python
await chargebee.item_price.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "item_price",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Item price ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `item_family_id` | `string` |  |
| `item_id` | `string` |  |
| `item_type` | `string` |  |
| `description` | `string` |  |
| `status` | `string` |  |
| `external_name` | `string` |  |
| `pricing_model` | `string` |  |
| `price` | `integer` |  |
| `price_in_decimal` | `string` |  |
| `period` | `integer` |  |
| `period_unit` | `string` |  |
| `trial_period` | `integer` |  |
| `trial_period_unit` | `string` |  |
| `trial_end_action` | `string` |  |
| `shipping_period` | `integer` |  |
| `shipping_period_unit` | `string` |  |
| `billing_cycles` | `integer` |  |
| `free_quantity` | `integer` |  |
| `free_quantity_in_decimal` | `string` |  |
| `currency_code` | `string` |  |
| `resource_version` | `integer` |  |
| `updated_at` | `integer` |  |
| `created_at` | `integer` |  |
| `archived_at` | `integer` |  |
| `invoice_notes` | `string` |  |
| `is_taxable` | `boolean` |  |
| `metadata` | `object` |  |
| `tax_detail` | `object` |  |
| `accounting_detail` | `object` |  |
| `tiers` | `array<object>` |  |
| `tax_providers_fields` | `array<object>` |  |
| `object` | `string` |  |
| `channel` | `string` |  |
| `show_description_in_invoices` | `boolean` |  |
| `show_description_in_quotes` | `boolean` |  |
| `business_entity_id` | `string` |  |
| `deleted` | `boolean` |  |


</details>

### Item Price Search

Search and filter item price records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await chargebee.item_price.search(
    query={"filter": {"eq": {"accounting_detail": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "item_price",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"accounting_detail": {}}}}
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
| `accounting_detail` | `object` | Details related to accounting such as cost, revenue, expenses, etc. |
| `archived_at` | `integer` | Date and time when the item was archived. |
| `billing_cycles` | `integer` | Number of billing cycles for the item. |
| `channel` | `string` | The channel through which the item is sold. |
| `created_at` | `integer` | Date and time when the item was created. |
| `currency_code` | `string` | The currency code used for pricing the item. |
| `custom_fields` | `array` | Custom field entries for the item price. |
| `description` | `string` | Description of the item. |
| `external_name` | `string` | External name of the item. |
| `free_quantity` | `integer` | Free quantity allowed for the item. |
| `free_quantity_in_decimal` | `string` | Free quantity allowed represented in decimal format. |
| `id` | `string` | Unique identifier for the item price. |
| `invoice_notes` | `string` | Notes to be included in the invoice for the item. |
| `is_taxable` | `boolean` | Flag indicating whether the item is taxable. |
| `item_family_id` | `string` | Identifier for the item family to which the item belongs. |
| `item_id` | `string` | Unique identifier for the parent item. |
| `item_type` | `string` | Type of the item (e.g., product, service). |
| `metadata` | `object` | Additional metadata associated with the item. |
| `name` | `string` | Name of the item price. |
| `object` | `string` | Object type representing the item price. |
| `period` | `integer` | Duration of the item's billing period. |
| `period_unit` | `string` | Unit of measurement for the billing period duration. |
| `price` | `integer` | Price of the item. |
| `price_in_decimal` | `string` | Price of the item represented in decimal format. |
| `pricing_model` | `string` | The pricing model used for the item (e.g., flat fee, usage-based). |
| `resource_version` | `integer` | Version of the item price resource. |
| `shipping_period` | `integer` | Duration of the item's shipping period. |
| `shipping_period_unit` | `string` | Unit of measurement for the shipping period duration. |
| `show_description_in_invoices` | `boolean` | Flag indicating whether to show the description in invoices. |
| `show_description_in_quotes` | `boolean` | Flag indicating whether to show the description in quotes. |
| `status` | `string` | Current status of the item price (e.g., active, inactive). |
| `tax_detail` | `object` | Information about taxes associated with the item price. |
| `tiers` | `array` | Different pricing tiers for the item. |
| `trial_end_action` | `string` | Action to be taken at the end of the trial period. |
| `trial_period` | `integer` | Duration of the trial period. |
| `trial_period_unit` | `string` | Unit of measurement for the trial period duration. |
| `updated_at` | `integer` | Date and time when the item price was last updated. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].accounting_detail` | `object` | Details related to accounting such as cost, revenue, expenses, etc. |
| `data[].archived_at` | `integer` | Date and time when the item was archived. |
| `data[].billing_cycles` | `integer` | Number of billing cycles for the item. |
| `data[].channel` | `string` | The channel through which the item is sold. |
| `data[].created_at` | `integer` | Date and time when the item was created. |
| `data[].currency_code` | `string` | The currency code used for pricing the item. |
| `data[].custom_fields` | `array` | Custom field entries for the item price. |
| `data[].description` | `string` | Description of the item. |
| `data[].external_name` | `string` | External name of the item. |
| `data[].free_quantity` | `integer` | Free quantity allowed for the item. |
| `data[].free_quantity_in_decimal` | `string` | Free quantity allowed represented in decimal format. |
| `data[].id` | `string` | Unique identifier for the item price. |
| `data[].invoice_notes` | `string` | Notes to be included in the invoice for the item. |
| `data[].is_taxable` | `boolean` | Flag indicating whether the item is taxable. |
| `data[].item_family_id` | `string` | Identifier for the item family to which the item belongs. |
| `data[].item_id` | `string` | Unique identifier for the parent item. |
| `data[].item_type` | `string` | Type of the item (e.g., product, service). |
| `data[].metadata` | `object` | Additional metadata associated with the item. |
| `data[].name` | `string` | Name of the item price. |
| `data[].object` | `string` | Object type representing the item price. |
| `data[].period` | `integer` | Duration of the item's billing period. |
| `data[].period_unit` | `string` | Unit of measurement for the billing period duration. |
| `data[].price` | `integer` | Price of the item. |
| `data[].price_in_decimal` | `string` | Price of the item represented in decimal format. |
| `data[].pricing_model` | `string` | The pricing model used for the item (e.g., flat fee, usage-based). |
| `data[].resource_version` | `integer` | Version of the item price resource. |
| `data[].shipping_period` | `integer` | Duration of the item's shipping period. |
| `data[].shipping_period_unit` | `string` | Unit of measurement for the shipping period duration. |
| `data[].show_description_in_invoices` | `boolean` | Flag indicating whether to show the description in invoices. |
| `data[].show_description_in_quotes` | `boolean` | Flag indicating whether to show the description in quotes. |
| `data[].status` | `string` | Current status of the item price (e.g., active, inactive). |
| `data[].tax_detail` | `object` | Information about taxes associated with the item price. |
| `data[].tiers` | `array` | Different pricing tiers for the item. |
| `data[].trial_end_action` | `string` | Action to be taken at the end of the trial period. |
| `data[].trial_period` | `integer` | Duration of the trial period. |
| `data[].trial_period_unit` | `string` | Unit of measurement for the trial period duration. |
| `data[].updated_at` | `integer` | Date and time when the item price was last updated. |

</details>

## Payment Source

### Payment Source List

List payment sources

#### Python SDK

```python
await chargebee.payment_source.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "payment_source",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No |  |
| `offset` | `string` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `customer_id` | `string` |  |
| `type` | `string` |  |
| `reference_id` | `string` |  |
| `status` | `string` |  |
| `gateway` | `string` |  |
| `gateway_account_id` | `string` |  |
| `ip_address` | `string` |  |
| `issuing_country` | `string` |  |
| `created_at` | `integer` |  |
| `updated_at` | `integer` |  |
| `resource_version` | `integer` |  |
| `deleted` | `boolean` |  |
| `business_entity_id` | `string` |  |
| `object` | `string` |  |
| `card` | `object` |  |
| `bank_account` | `object` |  |
| `amazon_payment` | `object` |  |
| `paypal` | `object` |  |
| `upi` | `object` |  |
| `mandates` | `object` |  |
| `custom_fields` | `array<object>` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_offset` | `string` |  |

</details>

### Payment Source Get

Retrieve a payment source

#### Python SDK

```python
await chargebee.payment_source.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "payment_source",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Payment source ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `customer_id` | `string` |  |
| `type` | `string` |  |
| `reference_id` | `string` |  |
| `status` | `string` |  |
| `gateway` | `string` |  |
| `gateway_account_id` | `string` |  |
| `ip_address` | `string` |  |
| `issuing_country` | `string` |  |
| `created_at` | `integer` |  |
| `updated_at` | `integer` |  |
| `resource_version` | `integer` |  |
| `deleted` | `boolean` |  |
| `business_entity_id` | `string` |  |
| `object` | `string` |  |
| `card` | `object` |  |
| `bank_account` | `object` |  |
| `amazon_payment` | `object` |  |
| `paypal` | `object` |  |
| `upi` | `object` |  |
| `mandates` | `object` |  |
| `custom_fields` | `array<object>` |  |


</details>

### Payment Source Search

Search and filter payment source records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await chargebee.payment_source.search(
    query={"filter": {"eq": {"amazon_payment": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "payment_source",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"amazon_payment": {}}}}
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
| `amazon_payment` | `object` | Data related to Amazon Pay payment source |
| `bank_account` | `object` | Data related to bank account payment source |
| `business_entity_id` | `string` | Identifier for the business entity associated with the payment source |
| `card` | `object` | Data related to card payment source |
| `created_at` | `integer` | Timestamp indicating when the payment source was created |
| `custom_fields` | `array` |  |
| `customer_id` | `string` | Unique identifier for the customer associated with the payment source |
| `deleted` | `boolean` | Indicates if the payment source has been deleted |
| `gateway` | `string` | Name of the payment gateway used for the payment source |
| `gateway_account_id` | `string` | Identifier for the gateway account tied to the payment source |
| `id` | `string` | Unique identifier for the payment source |
| `ip_address` | `string` | IP address associated with the payment source |
| `issuing_country` | `string` | Country where the payment source was issued |
| `mandates` | `object` | Data related to mandates for payments |
| `object` | `string` | Type of object, e.g., payment_source |
| `paypal` | `object` | Data related to PayPal payment source |
| `reference_id` | `string` | Reference identifier for the payment source |
| `resource_version` | `integer` | Version of the payment source resource |
| `status` | `string` | Status of the payment source, e.g., active or inactive |
| `type` | `string` | Type of payment source, e.g., card, bank_account |
| `updated_at` | `integer` | Timestamp indicating when the payment source was last updated |
| `upi` | `object` | Data related to UPI payment source |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].amazon_payment` | `object` | Data related to Amazon Pay payment source |
| `data[].bank_account` | `object` | Data related to bank account payment source |
| `data[].business_entity_id` | `string` | Identifier for the business entity associated with the payment source |
| `data[].card` | `object` | Data related to card payment source |
| `data[].created_at` | `integer` | Timestamp indicating when the payment source was created |
| `data[].custom_fields` | `array` |  |
| `data[].customer_id` | `string` | Unique identifier for the customer associated with the payment source |
| `data[].deleted` | `boolean` | Indicates if the payment source has been deleted |
| `data[].gateway` | `string` | Name of the payment gateway used for the payment source |
| `data[].gateway_account_id` | `string` | Identifier for the gateway account tied to the payment source |
| `data[].id` | `string` | Unique identifier for the payment source |
| `data[].ip_address` | `string` | IP address associated with the payment source |
| `data[].issuing_country` | `string` | Country where the payment source was issued |
| `data[].mandates` | `object` | Data related to mandates for payments |
| `data[].object` | `string` | Type of object, e.g., payment_source |
| `data[].paypal` | `object` | Data related to PayPal payment source |
| `data[].reference_id` | `string` | Reference identifier for the payment source |
| `data[].resource_version` | `integer` | Version of the payment source resource |
| `data[].status` | `string` | Status of the payment source, e.g., active or inactive |
| `data[].type` | `string` | Type of payment source, e.g., card, bank_account |
| `data[].updated_at` | `integer` | Timestamp indicating when the payment source was last updated |
| `data[].upi` | `object` | Data related to UPI payment source |

</details>

