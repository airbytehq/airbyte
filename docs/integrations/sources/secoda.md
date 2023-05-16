# Secoda API

## Sync overview

This source can sync data from the [Secoda API](https://docs.secoda.co/secoda-api). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

* collections
* tables
* terms

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |

### Performance considerations

## Getting started

### Requirements

* API Access

### Configuration

1. Obtain an API key from Secoda. See [here](https://docs.secoda.co/secoda-api/authentication) for more information on how to obtain an API key.
2. In the Airbyte Connector setup form, provide the obtained API key in the "Api Key" field.
3. Save the configuration.

Please note that this connector only supports full refresh syncs at this time. 

For more information on the Secoda API, refer to their [documentation](https://docs.secoda.co/secoda-api).