# Recharge

## Overview

The Recharge supports full refresh and incremental sync.

This source can sync data for the [Recharge API](https://developer.rechargepayments.com/).

### Output schema

Several output streams are available from this source:

* [Addresses](https://developer.rechargepayments.com/v1-shopify?python#list-addresses) \(Incremental sync\)
* [Charges](https://developer.rechargepayments.com/v1-shopify?python#list-charges) \(Incremental sync\)
* [Collections](https://developer.rechargepayments.com/v1-shopify) 
* [Customers](https://developer.rechargepayments.com/v1-shopify?python#list-customers) \(Incremental sync\)
* [Discounts](https://developer.rechargepayments.com/v1-shopify?python#list-discounts) \(Incremental sync\)
* [Metafields](https://developer.rechargepayments.com/v1-shopify?python#list-metafields)
* [Onetimes](https://developer.rechargepayments.com/v1-shopify?python#list-onetimes) \(Incremental sync\)
* [Orders](https://developer.rechargepayments.com/v1-shopify?python#list-orders) \(Incremental sync\)
* [Products](https://developer.rechargepayments.com/v1-shopify?python#list-products)
* [Shop](https://developer.rechargepayments.com/v1-shopify?python#shop)
* [Subscriptions](https://developer.rechargepayments.com/v1-shopify?python#list-subscriptions) \(Incremental sync\)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| SSL connection | Yes |

### Performance considerations

The Recharge connector should gracefully handle Recharge API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Recharge API Token

### Setup guide

Please read [How to generate your API token](https://support.rechargepayments.com/hc/en-us/articles/360008829993-ReCharge-API-).

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.2  | 2021-09-17 | [6149](https://github.com/airbytehq/airbyte/pull/6149) | Change `cursor_field` for Incremental streams |
|