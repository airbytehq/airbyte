# Babelforce

## Overview

The Babelforce source supports _Full Refresh_ as well as _Incremental_ syncs.

_Full Refresh_ sync means every time a sync is run, Airbyte will copy all rows in the tables and columns you set up for replication into the destination in a new table.
_Incremental_ syn means only changed resources are copied from Babelformce. For the first run, it will be a Full Refresh sync.

### Output schema

Several output streams are available from this source:

- [Calls](https://api.babelforce.com/#af7a6b6e-b262-487f-aabd-c59e6fe7ba41)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature                       | Supported?  |
| :---------------------------- | :---------- |
| Full Refresh Sync             | Yes         |
| Incremental Sync              | Yes         |
| Replicate Incremental Deletes | Coming soon |
| SSL connection                | Yes         |
| Namespaces                    | No          |

### Performance considerations

There are no performance consideration in the current version.

## Getting started

### Requirements

- Region/environment as listed in the `Regions & environments` section [here](https://api.babelforce.com/#intro)
- Babelforce access key ID
- Babelforce access token
- (Optional) start date from when the import starts in epoch Unix timestamp

### Setup guide

Generate a API access key ID and token using the [Babelforce documentation](https://help.babelforce.com/hc/en-us/articles/360044753932-API-documentation-and-endpoints-an-introduction-)

## CHANGELOG

| Version | Date       | Pull Request                                             | Subject                     |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------- |
| 0.2.0   | 2023-08-24 | [29314](https://github.com/airbytehq/airbyte/pull/29314) | Migrate to Low Code         |
| 0.1.0   | 2022-05-09 | [12700](https://github.com/airbytehq/airbyte/pull/12700) | Introduce Babelforce source |
