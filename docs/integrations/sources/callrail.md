# CallRail

## Overview

The CallRail source supports Full Refresh and Incremental syncs. 

### Output schema

This Source is capable of syncing the following core Streams:

* [Calls](https://apidocs.callrail.com/#calls)
* [Companies](https://apidocs.callrail.com/#companies)
* [Text Messages](https://apidocs.callrail.com/#text-messages)
* [Users](https://apidocs.callrail.com/#users)


### Features

| Feature | Supported? |
| :--- |:-----------|
| Full Refresh Sync | Yes        |
| Incremental - Append Sync | Yes        |
| Incremental - Dedupe Sync | Yes        |
| SSL connection | No         |
| Namespaces | No         |

## Getting started

### Requirements

* CallRail Account
* CallRail API Token

### How to obtain an API key and Account ID

1. Log in to CallRail account.
2. Go to **Account Settings** > **API**.
3. Copy the **API Key** and **Account Identifier**.

Refer to [CallRail API Documentation](https://apidocs.callrail.com/) for more information.

### Configuration

The configuration screen is driven by the spec of the Airbyte Connector:

```
documentationUrl: https://docs.airbyte.com/integrations/sources/callrail
connectionSpecification:
  $schema: http://json-schema.org/draft-07/schema#
  title: Call Rail Spec
  type: object
  required:
    - api_key
    - account_id
    - start_date
  additionalProperties: true
  properties:
    api_key:
      type: string
      description: API access key
      airbyte_secret: true
    account_id:
      type: string
      description: Account ID
      airbyte_secret: true
    start_date:
      type: string
      description: Start getting data from that date.
      pattern: ^[0-9]{4}-[0-9]{2}-[0-9]{2}$
      examples:
        - "%Y-%m-%d"
```

In the Airbyte UI, enter the following information for your CallRail source connection:

* **API Key**: The API Key obtained from CallRail.
* **Account ID**: The Account Identifier obtained from CallRail.
* **Start Date**: The date to start syncing your data from. Use format `%Y-%m-%d`. 

Save your settings and test your connection. 

Note: SSL connection and Namespaces are not supported.

Refer to [CallRail API Documentation](https://apidocs.callrail.com/) for more information. 

## Changelog

| Version | Date       | Pull Request                                            | Subject                           |
| :--- |:-----------|:--------------------------------------------------------|:----------------------------------|
| 0.1.0 | 2022-10-31 | [18739](https://github.com/airbytehq/airbyte/pull/18739) | 🎉 New Source: CallRail                  |

Please make sure to verify all steps with the current CallRail interface to ensure accuracy.