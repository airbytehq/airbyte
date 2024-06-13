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
| 0.2.5 | 2024-06-06 | [39295](https://github.com/airbytehq/airbyte/pull/39295) | [autopull] Upgrade base image to v1.2.2 |
| 0.2.4 | 2024-04-19 | [37151](https://github.com/airbytehq/airbyte/pull/37151) | Updating to 0.80.0 CDK |
| 0.2.3 | 2024-04-18 | [37151](https://github.com/airbytehq/airbyte/pull/37151) | Manage dependencies with Poetry. |
| 0.2.2 | 2024-04-15 | [37151](https://github.com/airbytehq/airbyte/pull/37151) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.1 | 2024-04-12 | [37151](https://github.com/airbytehq/airbyte/pull/37151) | schema descriptions |
| 0.2.0 | 2023-08-24 | [29320](https://github.com/airbytehq/airbyte/pull/29320) | Migrate to Low Code |
| 0.1.1 | 2023-08-16 | [13007](https://github.com/airbytehq/airbyte/pull/13007) | Fix schema and tests |
| 0.1.0 | 2022-05-20 | [13007](https://github.com/airbytehq/airbyte/pull/13007) | New source |

</details>
