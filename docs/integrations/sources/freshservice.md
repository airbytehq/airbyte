# Freshservice

## Overview

The Freshservice source supports full refresh syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

Several output streams are available from this source:

* [Tickets](https://api.freshservice.com/v2/#view_all_ticket) (Incremental)
* [Problems](https://api.freshservice.com/v2/#problems) (Incremental)
* [Changes](https://api.freshservice.com/v2/#changes) (Incremental)
* [Releases](https://api.freshservice.com/v2/#releases) (Incremental)
* [Requesters](https://api.freshservice.com/v2/#requesters)
* [Agents](https://api.freshservice.com/v2/#agents)
* [Locations](https://api.freshservice.com/v2/#locations)
* [Products](https://api.freshservice.com/v2/#products)
* [Vendors](https://api.freshservice.com/v2/#vendors)
* [Assets](https://api.freshservice.com/v2/#assets)
* [PurchaseOrders](https://api.freshservice.com/v2/#purchase-order)
* [Software](https://api.freshservice.com/v2/#software)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

## Getting started

To set up the Freshservice connector in Airbyte, follow these steps:

### Prerequisites

Before you begin, you need the following:

* A Freshservice account.
* A Freshservice API Key.
* Your Freshservice domain name.
* Replication start date in the format `YYYY-MM-DDTHH:MM:SSZ`.

### Retrieve your Freshservice API key

1. Log in to your Freshservice account.
2. In the navigation pane, click your profile picture.
3. Click **Profile settings**.
4. In the menu on the left, click **API Key**.
5. Click the **Generate new key** button to generate a new API key.

### Configure the Freshservice connector in Airbyte

1. In Airbyte, go to the New Connection page.
2. Choose the Freshservice source.
3. Enter your Freshservice domain name in the `domain_name` field.
4. Enter your Freshservice API key in the `api_key` field.
5. Enter your Replication start date in the `start_date` field in the format `YYYY-MM-DDTHH:MM:SSZ`.
6. Click the `Check connection` button to verify the credentials are correct.
7. Once the connection is verified, click the `Create` button to create the Freshservice connection.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 1.0.0 | 2023-05-02 | [25743](https://github.com/airbytehq/airbyte/pull/25743) | Correct data types in tickets, agents and requesters schemas to match Freshservice API |
| 0.1.1 | 2021-12-28 | [9143](https://github.com/airbytehq/airbyte/pull/9143) | Update titles and descriptions |
| 0.1.0 | 2021-10-29 | [6967](https://github.com/airbytehq/airbyte/pull/6967) | 🎉 New Source: Freshservice |

## Connector specification

```
{
  "documentationUrl": "https://docs.airbyte.io/integrations/sources/freshservice",
  "connectionSpecification": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Freshservice Spec",
    "type": "object",
    "required": ["domain_name", "api_key", "start_date"],
    "additionalProperties": false,
    "properties": {
      "domain_name": {
        "type": "string",
        "title": "Domain Name",
        "description": "The name of your Freshservice domain",
        "examples": ["mydomain.freshservice.com"]
      },
      "api_key": {
        "title": "API Key",
        "type": "string",
        "description": "Freshservice API Key. See <a href=\"https://api.freshservice.com/#authentication\">here</a>. The key is case sensitive.",
        "airbyte_secret": true
      },
      "start_date": {
        "title": "Start Date",
        "type": "string",
        "description": "UTC date and time in the format 2020-10-01T00:00:00Z. Any data before this date will not be replicated.",
        "examples": ["2020-10-01T00:00:00Z"],
        "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"
      }
    }
  }
}
```