# Harness

## Overview

The Harness source is maintained by [Faros
AI](https://github.com/faros-ai/airbyte-connectors/tree/main/sources/harness-source).
Please file any support requests on that repo to minimize response time from the
maintainers. The source supports both Full Refresh and Incremental syncs. You
can choose if this source will copy only the new or updated data, or all rows in
the tables and columns you set up for replication, every time a sync is run.

### Output schema

Only one stream is currently available from this source:

* [Executions](https://docs.harness.io/article/ba4vs50071-use-workflows-api) \(Incremental\)

If there are more endpoints you'd like Faros AI to support, please [create an
issue.](https://github.com/faros-ai/airbyte-connectors/issues/new)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

The Harness source should not run into Harness API limitations under normal
usage.  Please [create an
issue](https://github.com/faros-ai/airbyte-connectors/issues/new) if you see any
rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Harness Account Id
* Harness API Key
* Harness API URL, if using a self-hosted Harness instance

Please follow the [their documentation for generating a Harness API
Key](https://ngdocs.harness.io/article/tdoad7xrh9-add-and-manage-api-keys#harness_api_key).

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.23 | 2021-11-16 | [153](https://github.com/faros-ai/airbyte-connectors/pull/153) | Add Harness source and Faros destination's converter |
