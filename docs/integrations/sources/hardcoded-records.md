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

| Version | Date       | Pull Request                                             | Subject                  |
|:--------|:-----------|:---------------------------------------------------------|:-------------------------|
| 0.0.25 | 2025-01-25 | [52269](https://github.com/airbytehq/airbyte/pull/52269) | Update dependencies |
| 0.0.24 | 2025-01-11 | [51223](https://github.com/airbytehq/airbyte/pull/51223) | Update dependencies |
| 0.0.23 | 2025-01-04 | [50895](https://github.com/airbytehq/airbyte/pull/50895) | Update dependencies |
| 0.0.22 | 2024-12-28 | [50626](https://github.com/airbytehq/airbyte/pull/50626) | Update dependencies |
| 0.0.21 | 2024-12-21 | [50140](https://github.com/airbytehq/airbyte/pull/50140) | Update dependencies |
| 0.0.20 | 2024-12-14 | [49653](https://github.com/airbytehq/airbyte/pull/49653) | Update dependencies |
| 0.0.19 | 2024-12-11 | [48976](https://github.com/airbytehq/airbyte/pull/48976) | Update dependencies |
| 0.0.18 | 2024-11-25 | [48669](https://github.com/airbytehq/airbyte/pull/48669) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.17 | 2024-10-28 | [47052](https://github.com/airbytehq/airbyte/pull/47052) | Update dependencies |
| 0.0.16 | 2024-10-12 | [46773](https://github.com/airbytehq/airbyte/pull/46773) | Update dependencies |
| 0.0.15 | 2024-10-05 | [46492](https://github.com/airbytehq/airbyte/pull/46492) | Update dependencies |
| 0.0.14 | 2024-09-28 | [46200](https://github.com/airbytehq/airbyte/pull/46200) | Update dependencies |
| 0.0.13 | 2024-09-21 | [45756](https://github.com/airbytehq/airbyte/pull/45756) | Update dependencies |
| 0.0.12 | 2024-09-14 | [45496](https://github.com/airbytehq/airbyte/pull/45496) | Update dependencies |
| 0.0.11 | 2024-09-07 | [45280](https://github.com/airbytehq/airbyte/pull/45280) | Update dependencies |
| 0.0.10 | 2024-09-03 | [45097](https://github.com/airbytehq/airbyte/pull/45097) | Update CDK version to ^5 |
| 0.0.9 | 2024-08-31 | [45003](https://github.com/airbytehq/airbyte/pull/45003) | Update dependencies |
| 0.0.8 | 2024-08-24 | [44630](https://github.com/airbytehq/airbyte/pull/44630) | Update dependencies |
| 0.0.7 | 2024-08-17 | [44331](https://github.com/airbytehq/airbyte/pull/44331) | Update dependencies |
| 0.0.6 | 2024-08-12 | [43823](https://github.com/airbytehq/airbyte/pull/43823) | Update dependencies |
| 0.0.5 | 2024-08-10 | [43645](https://github.com/airbytehq/airbyte/pull/43645) | Update dependencies |
| 0.0.4 | 2024-08-03 | [43244](https://github.com/airbytehq/airbyte/pull/43244) | Update dependencies |
| 0.0.3 | 2024-07-29 | [42850](https://github.com/airbytehq/airbyte/pull/42850) | Update Airbyte CDK to v4 |
| 0.0.2 | 2024-07-27 | [42828](https://github.com/airbytehq/airbyte/pull/42828) | Update dependencies |
| 0.0.1 | 2024-07-23 | [42434](https://github.com/airbytehq/airbyte/pull/42434) | Initial Release |

</details>
