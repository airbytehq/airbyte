# Select Star

Select Star is an intelligent data discovery platform that automatically analyzes and documents your data.
Many data scientists and business analysts spend too much time looking for the right data, often spending excessive amounts of time having to ask other people to find it.
Select Star provides an easy to use data portal that everyone can use to find and understand data.

The source connector fetches data from [Select Star API](https://docs.selectstar.com/select-star-api)

## Prerequisites

* You own an Select Star account
* Follow the [Setup guide](#setup-guide) to authorize Airbyte to read data from your account.

## Setup guide

### Step 1: Obtain API Token for Select Star Account

1. It's free to [Create a Token](https://docs.selectstar.com/select-star-api/authentication) in Auth0.

## Supported sync modes

The Auth0 source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
 - Full Refresh

## Supported Streams

- [Tables](https://api.production.selectstar.com/docs/#tag/tables)
- [Lineage](https://api.production.selectstar.com/docs/#tag/lineage)

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                        |
|:--------|:-----------|:---------------------------------------------------------|:-------------------------------------------------------------------------------|
| 0.1.0  | 2023-08-04 | TBD | Add tables and lineage streams |

