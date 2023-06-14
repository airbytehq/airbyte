# Xata

Airbyte destination connector for Xata.

## Introduction

Currently only `append` is supported.

Conventions:

- The `stream` name will be define the name of the table in Xata.
- The `message` data will be mapped one by one to the table schema.

For example, as stream name `nyc_taxi_fares_2022` will attempt to write to a table with the same name. 
If the message has the following shape:
```
{
    "name": "Yellow Cab, co",
    "date": "2022-05-15",
    "driver": "Joe Doe"
}
```
the table must have the same columns, mapping the names and [data types](https://xata.io/docs/concepts/data-model), one-by-one.

## Getting Started

In order to connect, you need:
* API Key: go to your [account settings](https://app.xata.io/settings) to generate a key.
* Database URL: navigate to the configuration tab in your workspace and copy the `Workspace API base URL`.

## CHANGELOG

| Version | Date       | Pull Request                                                  | Subject                 |
|:--------|:-----------|:--------------------------------------------------------------|:------------------------|
| 0.1.0   | 2023-06-14 | [#24192](https://github.com/airbytehq/airbyte/pull/24192)     | New Destination Connector Xata |
