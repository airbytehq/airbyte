# Dockerhub

## Sync overview

This source can sync data for the DockerHub API. It currently supports only [listing public repos](https://github.com/airbytehq/airbyte/issues/12773) and Full Refresh syncing for now. You supply a `docker_username`, and it will sync down all info about repos published under that name.

### Output schema

This Source is capable of syncing the following Streams:

- DockerHub

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |
| Namespaces        | No                   |       |

### Performance considerations

This connector has been tested for the Airbyte organization, which has 266 repos, and works fine. It should not run into limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- None

### Setup guide

1. Define a `docker_username`: the username that the connector will pull all repo data from.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.3.1   | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version   |
| 0.3.0 | 2024-08-15 | [44155](https://github.com/airbytehq/airbyte/pull/44155) | Refactor connector to manifest-only format |
| 0.2.15 | 2024-08-10 | [43670](https://github.com/airbytehq/airbyte/pull/43670) | Update dependencies |
| 0.2.14 | 2024-08-03 | [43145](https://github.com/airbytehq/airbyte/pull/43145) | Update dependencies |
| 0.2.13 | 2024-07-27 | [42715](https://github.com/airbytehq/airbyte/pull/42715) | Update dependencies |
| 0.2.12 | 2024-07-20 | [42265](https://github.com/airbytehq/airbyte/pull/42265) | Update dependencies |
| 0.2.11 | 2024-07-13 | [41908](https://github.com/airbytehq/airbyte/pull/41908) | Update dependencies |
| 0.2.10 | 2024-07-10 | [41515](https://github.com/airbytehq/airbyte/pull/41515) | Update dependencies |
| 0.2.9 | 2024-07-09 | [41079](https://github.com/airbytehq/airbyte/pull/41079) | Update dependencies |
| 0.2.8 | 2024-07-06 | [40830](https://github.com/airbytehq/airbyte/pull/40830) | Update dependencies |
| 0.2.7 | 2024-06-25 | [40261](https://github.com/airbytehq/airbyte/pull/40261) | Update dependencies |
| 0.2.6 | 2024-06-22 | [40021](https://github.com/airbytehq/airbyte/pull/40021) | Update dependencies |
| 0.2.5 | 2024-06-06 | [39295](https://github.com/airbytehq/airbyte/pull/39295) | [autopull] Upgrade base image to v1.2.2 |
| 0.2.4 | 2024-04-19 | [37151](https://github.com/airbytehq/airbyte/pull/37151) | Updating to 0.80.0 CDK |
| 0.2.3 | 2024-04-18 | [37151](https://github.com/airbytehq/airbyte/pull/37151) | Manage dependencies with Poetry. |
| 0.2.2 | 2024-04-15 | [37151](https://github.com/airbytehq/airbyte/pull/37151) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.1 | 2024-04-12 | [37151](https://github.com/airbytehq/airbyte/pull/37151) | schema descriptions |
| 0.2.0 | 2023-08-24 | [29320](https://github.com/airbytehq/airbyte/pull/29320) | Migrate to Low Code |
| 0.1.1 | 2023-08-16 | [13007](https://github.com/airbytehq/airbyte/pull/13007) | Fix schema and tests |
| 0.1.0 | 2022-05-20 | [13007](https://github.com/airbytehq/airbyte/pull/13007) | New source |

</details>
