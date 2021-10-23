# Opentable

## Sync overview

The Opentable source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This connector is based on the [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

### Output schema

This connector can be used to sync the following tables from Opentable:

* **guests.** Contains info about your Opentable guests. [Opentable docs](https://platform.opentable.com/documentation). 
* **reservations.** Contins info about your Opentable reservations. [Opentable docs](https://platform.opentable.com/documentation). 

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `array` | `array` | primitive arrays are converted into arrays of the types described in this table |
| `int`, `long` | `number` |  |
| `object` | `object` |  |
| `string` | `string` | \`\` |
| Namespaces | No |  |

### Features

Feature

| Supported?\(Yes/No\) | Notes |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |

### Performance considerations

By default, this connector waits 5 seconds between each API call.
Each API call limits the amount of records to 1000 (default value).

## Getting started

### Requirements

* Opentable Client ID & Client Secret
* Opentable Endpoint 

### Setup guide

#### Obtain your Endpoint and Identity URLs provided by Opentable

Follow the [Opentable documentation for obtaining your base URL](https://platform.opentable.com/documentation/?shell#obtaining-an-access-token) and get in contact with your Opentable representative to request a Client ID and Secret.
\*\*\*\*

## CHANGELOG

| Version | Date | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| `0.1.0` | 2021-10-22 | https://github.com/airbytehq/airbyte/pull/7299 | Release Opentable CDK Connector|
