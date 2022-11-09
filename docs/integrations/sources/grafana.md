# Grafana API
API Documentation link [here](https://grafana.com/docs/grafana/latest/developers/http_api/)
## Overview

The Grafana API source supports full refresh syncs

### Output schema

Two output streams are available from this source:

*[datasources](https://grafana.com/docs/grafana/latest/developers/http_api/data_source/).
*[reports](https://grafana.com/docs/grafana/latest/developers/http_api/reporting/).

### Features

| Feature           | Supported? |
|:------------------|:-----------|
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |

### Performance considerations

None Mentioned in the API docuemntation

## Getting started

### Requirements

* Grafana API Key.

### Connect using `API Key`:

1. Generate an API Key as described [here](https://grafana.com/docs/grafana/latest/administration/api-keys/).
2. Use the generated `API Key` in the Airbyte connection.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                         |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------|
| 0.1.0   | 2022-11-01 | [18883](https://github.com/airbytehq/airbyte/pull/18858) | 🎉 New Source: Grafana                          |
