# Xata

Airbyte destination connector for Xata.

## Introduction

Currently only `append` is supported.

Conventions:

- The `stream` name will define the name of the table in Xata.
- The `message` data will be mapped one by one to the table schema.

For example, a stream name `nyc_taxi_fares_2022` will attempt to write to a table with the same
name. If the message has the following shape:

```
{
    "name": "Yellow Cab, co",
    "date": "2022-05-15",
    "driver": "Joe Doe"
}
```

the table must have the same columns, mapping the names and
[data types](https://xata.io/docs/concepts/data-model), one-by-one.

## Getting Started

In order to connect, you need:

- API Key: go to your [account settings](https://app.xata.io/settings) to generate a key.
- Database URL: navigate to the configuration tab in your workspace and copy the
  `Workspace API base URL`.

## CHANGELOG

| Version | Date       | Pull Request                                              | Subject                        |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------- |
| 0.1.4 | 2024-06-04 | [39088](https://github.com/airbytehq/airbyte/pull/39088) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.3 | 2024-05-21 | [38499](https://github.com/airbytehq/airbyte/pull/38499) | [autopull] base image + poetry + up_to_date |
| 0.1.2   | 2024-03-05 | [#35838](https://github.com/airbytehq/airbyte/pull/35838) | Un-archive connector           |
| 0.1.1   | 2023-06-21 | [#27542](https://github.com/airbytehq/airbyte/pull/27542) | Mark api_key as Airbyte Secret |
| 0.1.0   | 2023-06-14 | [#24192](https://github.com/airbytehq/airbyte/pull/24192) | New Destination Connector Xata |
