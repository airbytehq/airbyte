# Facebook Marketing

## Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |

This source syncs data from an ElasticSearch domain.

## Supported Tables

This source automatically discovers all indices in the domain and can sync any of them.

## Getting Started \(Airbyte Open-Source\)

#### Requirements

* ElasticSearch credentials (username and password)

### Performance Considerations

ElasticSearch calls may be rate limited by the underlying service.
This is specific to each deployment.

#### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `number` | `number` |  |
| `array` | `array` |  |
| `object` | `object` |  |

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.0 | 2021-11-11 | [7099](https://github.com/airbytehq/airbyte/pull/7099) | New source: ElasticSearch |
