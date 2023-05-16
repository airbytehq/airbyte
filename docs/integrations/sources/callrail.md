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

### Configuration

To set up the CallRail connector in Airbyte, you will need the following information:

* API access key
* Account ID
* Start date to retrieve data

#### Obtaining the CallRail API Token

1. Log in to your CallRail account. 
2. Click on "Account" in the top-right corner of the page, then choose "My Account" from the dropdown menu.
3. On the left-hand side of the "My Account" page, click on the "API" tab.
4. If no API credentials exist, generate a new set of API credentials. You will then see a new "API Credentials" section on the same page.
5. Copy and paste the API Token into the relevant field on the Airbyte configuration form.

#### Obtaining the Account ID

1. Log in to your CallRail account.
2. Click on the "Menu" icon on the top-left, and navigate to "Settings."
3. Click on "Your Profile" to view your account information.
4. Copy and paste the Account ID into the relevant field on the Airbyte configuration form.

#### Setting the Start Date

Set the start date field to YYYY-MM-DD format. The connector will retrieve all data with a timestamp equal to or greater than this date.

### Example config JSON

```json
{
    "api_key": "your_api_key_here",
    "account_id": "your_account_id_here",
    "start_date": "2022-06-01"
}
``` 

Be sure to verify all information with the CallRail website and documentation.

#### Airbyte Connector Spec

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
      pattern: ^[0-9]{4}-[0-9]{2}-[0-9]{2}$
      examples:
        - "%Y-%m-%d"
``` 

## Changelog

| Version | Date       | Pull Request                                            | Subject                           |
| :--- |:-----------|:--------------------------------------------------------|:----------------------------------|
| 0.1.0 | 2022-10-31 | [18739](https://github.com/airbytehq/airbyte/pull/18739) | 🎉 New Source: CallRail                  |