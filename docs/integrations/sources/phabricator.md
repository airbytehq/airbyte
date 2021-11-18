# Phabricator

## Overview

The Phabricator source is maintained by [Faros
AI](https://github.com/faros-ai/airbyte-connectors/tree/main/sources/phabricator-source).
Please file any support requests on that repo to minimize response time from the
maintainers. The source supports both Full Refresh and Incremental syncs. You
can choose if this source will copy only the new or updated data, or all rows
in the tables and columns you set up for replication, every time a sync is run.

### Output schema

Several output streams are available from this source:

* [Commits](https://developer.pagerduty.com/api-reference/b3A6Mjc0ODEzOA-list-incidents) \(Incremental\)
* [Projects](https://developer.pagerduty.com/api-reference/b3A6Mjc0ODE1NA-list-log-entries) \(Incremental\)
* [Repositories](https://developer.pagerduty.com/api-reference/b3A6Mjc0ODE2NA-list-priorities) \(Incremental\)
* [Revisions](https://developer.pagerduty.com/api-reference/b3A6Mjc0ODIzMw-list-users) \(Incremental\)
* [Users](https://developer.pagerduty.com/api-reference/b3A6Mjc0ODIzMw-list-users) \(Incremental\)

In the above links, replace `your.phabricator.url` with the url of your
Phabricator instance.

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

The Phabricator source should not run into API limitations under normal
usage. Please [create an
issue](https://github.com/faros-ai/airbyte-connectors/issues/new) if you see any
rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Phabricator Server
* Phabricator API Token
* Desired Start Date to pull data from

### Setup guide

Login to your Phabricator server in your browser and go to
`https://your.phabricator.url/me/configure` to generate your API token.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.23 | 2021-10-01 | [114](https://github.com/faros-ai/airbyte-connectors/pull/114) | Added projects stream to Phabricator + cleanup |
| 0.1.22 | 2021-10-01 | [113](https://github.com/faros-ai/airbyte-connectors/pull/113) | Added revisions & users streams to Phabricator source + bump version |
| 0.1.21 | 2021-09-27 | [101](https://github.com/faros-ai/airbyte-connectors/pull/101) | Exclude tests from Docker + fix path + bump version |
| 0.1.20 | 2021-09-27 | [100](https://github.com/faros-ai/airbyte-connectors/pull/100) | Update Jenkins spec + refactor + add Phabricator source skeleton |
