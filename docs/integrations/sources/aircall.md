# Aircall

This page contains the setup guide and reference information for the [Aircall](https://developer.aircall.io/api-references/#rest-api) source

## Prerequisites

Access Token (which acts as bearer token) is mandate for this connector to work, It could be seen at settings (ref - https://dashboard.aircall.io/integrations/api-keys).

## Setup guide

### Step 1: Set up Aircall connection

- Get an Aircall access token via settings (ref - https://dashboard.aircall.io/integrations/api-keys)
- Setup params (All params are required)
- Available params
    - api_id: The auto generated id
    - api_token: Seen at the Aircall settings (ref - https://dashboard.aircall.io/integrations/api-keys)
    - start_date: Date filter for eligible streams, enter

## Supported sync modes

The Aircall source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

- calls
- company
- contacts
- numbers
- tags
- user_availablity
- users
- teams
- webhooks

## API method example

GET https://api.aircall.io/v1/numbers

## Performance considerations

Aircall [API reference](https://api.aircall.io/v1) has v1 at present. The connector as default uses v1.

## Changelog

| Version | Date       | Pull Request                                           | Subject        |
| :------ | :--------- | :----------------------------------------------------- | :------------- |
| 0.1.0   | 2023-04-19 | [Init](https://github.com/airbytehq/airbyte/pull/)| Initial commit |