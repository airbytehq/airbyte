# Hardcoded Records

## Sync overview

The Sample Data (Hardcoded Records) source outputs sample data (same record over and over again, but very fast) and is intended to be used in performance testing.

### Output schemas

This source will generate an dataset with products (skinny), customers (fat) and dummy fields. Here's the examples:

<details>
<summary>Products</summary>

```json
{
  "id": 1,
  "make": "Mazda",
  "model": "MX-5",
  "year": 2008,
  "price": 2869,
  "created_at": "2022-02-01T17:02:19+00:00",
  "updated_at": "2022-11-01T17:02:19+00:00"
}
```

</details>

<br />

<details>
<summary>Customers</summary>

```json
{
  "id": 6569096478909,
  "email": "test@test.com",
  "created_at": "2023-04-13T02:30:04-07:00",
  "updated_at": "2023-04-24T06:53:48-07:00",
  "first_name": "New Test",
  "last_name": "Customer",
  "orders_count": 0,
  "state": "disabled",
  "total_spent": 0.0,
  "last_order_id": null,
  "note": "updated_mon_24.04.2023",
  "verified_email": true,
  "multipass_identifier": null,
  "tax_exempt": false,
  "tags": "",
  "last_order_name": null,
  "currency": "USD",
  "phone": "+380639379992",
  "addresses": [
    {
      "id": 8092523135165,
      "customer_id": 6569096478909,
      "first_name": "New Test",
      "last_name": "Customer",
      "company": "Test Company",
      "address1": "My Best Accent",
      "address2": "",
      "city": "Fair Lawn",
      "province": "New Jersey",
      "country": "United States",
      "zip": "07410",
      "phone": "",
      "name": "New Test Customer",
      "province_code": "NJ",
      "country_code": "US",
      "country_name": "United States",
      "default": true
    }
  ],
  "accepts_marketing": true,
  "accepts_marketing_updated_at": "2023-04-13T02:30:04-07:00",
  "marketing_opt_in_level": "single_opt_in",
  "tax_exemptions": "[]",
  "email_marketing_consent": {
    "state": "subscribed",
    "opt_in_level": "single_opt_in",
    "consent_updated_at": "2023-04-13T02:30:04-07:00"
  },
  "sms_marketing_consent": {
    "state": "not_subscribed",
    "opt_in_level": "single_opt_in",
    "consent_updated_at": null,
    "consent_collected_from": "SHOPIFY"
  },
  "admin_graphql_api_id": "gid://shopify/Customer/6569096478909",
  "default_address": {
    "id": 8092523135165,
    "customer_id": 6569096478909,
    "first_name": "New Test",
    "last_name": "Customer",
    "company": "Test Company",
    "address1": "My Best Accent",
    "address2": "",
    "city": "Fair Lawn",
    "province": "New Jersey",
    "country": "United States",
    "zip": "07410",
    "phone": "",
    "name": "New Test Customer",
    "province_code": "NJ",
    "country_code": "US",
    "country_name": "United States",
    "default": true
  },
  "shop_url": "airbyte-integration-test"
}
```

</details>

<br />

<details>
<summary>Dummy Fields</summary>

```json
{
  "field1": "valuevaluevaluevaluevalue1",
  "field2": "valuevaluevaluevaluevalue1",
  "field3": "valuevaluevaluevaluevalue1",
  "field4": "valuevaluevaluevaluevalue1",
  "field5": "valuevaluevaluevaluevalue1"
}
```

</details>

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
|:------------------|:---------------------|:------|
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |
| Namespaces        | No                   |       |


### Requirements

None!

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject          |
|:--------|:-----------|:---------------------------------------------------------|:-----------------|
| 0.0.1   | 2024-07-23 | [42434](https://github.com/airbytehq/airbyte/pull/42434) | Initial Release  |

</details>
