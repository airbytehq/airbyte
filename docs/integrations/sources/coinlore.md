# MailGun

This page contains the reference information for the [Coinlore](https://www.coinlore.com/) source connector.
Coinlore's API reference can be found [here](https://www.coinlore.com/cryptocurrency-data-api).

## Supported sync modes

The MailGun source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- |:-----------|
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | No         |
| Namespaces                    | No         |

## Supported Streams

- tickers

## API method example

`GET https://api.coinlore.net/api/tickers`

## Changelog

| Version | Date       | Pull Request                                             | Subject              |
| :------ |:-----------|:---------------------------------------------------------|:---------------------|
| 0.1.0   | 2024-01-20 | [34404](https://github.com/airbytehq/airbyte/pull/34404) | New Source: Coinlore |
