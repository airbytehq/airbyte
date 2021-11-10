# Jenkins

## Overview

The Jenkins source is maintained by [Faros
AI](https://github.com/faros-ai/airbyte-connectors/tree/main/sources/jenkins-source)
and supports both Full Refresh and Incremental syncs. You can choose if this
connector will copy only the new or updated data, or all rows in the tables and
columns you set up for replication, every time a sync is run.

### Output schema

Several output streams are available from this source:

* [Builds](TODO) \(Incremental\)
* [Jobs](TODO)

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

The Jenkins source should not run into Jenkins API limitations under normal
usage. Please [create an
issue](https://github.com/faros-ai/airbyte-connectors/issues/new) if you see any
rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Jenkins Server
* Jenkins User
* Jenkins API Token

### Setup guide

Login to your Jenkins server in your browser and go to
`$JENKINS_SERVER_URL/me/configure` to generate your API token.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.23 | 2021-10-01 | [114](https://github.com/faros-ai/airbyte-connectors/pull/114) | Added projects stream to Phabricator + cleanup |
| 0.1.22 | 2021-10-01 | [113](https://github.com/faros-ai/airbyte-connectors/pull/113) | Added revisions & users streams to Phabricator source + bump version |
| 0.1.21 | 2021-09-27 | [101](https://github.com/faros-ai/airbyte-connectors/pull/101) | Exclude tests from Docker + fix path + bump version |
| 0.1.20 | 2021-09-27 | [100](https://github.com/faros-ai/airbyte-connectors/pull/100) | Update Jenkins spec + refactor + add Phabricator source skeleton |
| 0.1.7 | 2021-09-25 | [64](https://github.com/faros-ai/airbyte-connectors/pull/64) | Add Jenkins source |

