# CallRail

## Overview

The CallRail source supports Full Refresh and Incremental syncs.

### Output schema

This Source is capable of syncing the following core Streams:

- [Calls](https://apidocs.callrail.com/#calls)
- [Companies](https://apidocs.callrail.com/#companies)
- [Text Messages](https://apidocs.callrail.com/#text-messages)
- [Users](https://apidocs.callrail.com/#users)

### Features

| Feature                     | Supported? |
| :--------------------------|:-----------|
| Full Refresh Sync           | Yes        |
| Incremental - Append Sync   | Yes        |
| Incremental - Dedupe Sync   | Yes        |
| SSL connection              | No         |
| Namespaces                  | No         |

## Getting started

### Requirements

- CallRail Account
- CallRail API Token

### Configuration

To set up the CallRail source in Airbyte, you will first need to navigate to your CallRail account and obtain an API key. 

1. Log in to your CallRail account and navigate to the API section of the left navigation menu.
2. Click Generate API Key, or copy an existing key if you already have one.
3. In Airbyte, enter your API key in the `api_key` field in the configuration form.
4. Next, you will need to enter your Account ID in the `account_id` field in the configuration form. The Account ID can be found in the URL of your CallRail account when logged in. 
5. In CallRail, navigate to any page in your account. The Account ID is the string of numbers in the URL between `accounts/` and `/dashboard`. For example, in the URL `https://www.callrail.com/accounts/12345678/dashboard`, the Account ID is `12345678`.
6. Finally, enter the date you want to start syncing data from in the `start_date` field in the configuration form. This date should be in the format `YYYY-MM-DD`. 

For more information on the CallRail API, please refer to the [CallRail API Documentation](https://apidocs.callrail.com/docs/introduction) 

Here is the current spec for reference:

```yaml
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
      pattern: "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
      examples: ["%Y-%m-%d"]
```