# Aircall

This page contains the setup guide and reference information for the [Aircall](https://developer.aircall.io/api-references/#rest-api) source

## Prerequisites

- Access to the Aircall API
- Aircall [API Token](https://dashboard.aircall.io/integrations/api-keys) 

## Setup guide
1. Enter a name for the source.
2. Enter the **App ID**. This is the auto-generated ID of your account.
3. Enter the **API Token**. This can be found in the [settings](https://dashboard.aircall.io/integrations/api-keys).
4. Enter the **Date-From Filter** in the format 
YYYY-MM-DDTHH:mm:ss.SSSZ. Only date after this date will be synced.

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