# Dockerhub

## Sync overview

This source can sync data for the DockerHub API. It currently supports only [listing public repos](https://github.com/airbytehq/airbyte/issues/12773) and Full Refresh syncing for now. You supply a `docker_username`, and it will sync down all info about repos published under that name.

### Output schema

This Source is capable of syncing the following Streams:

* DockerHub

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |
| Namespaces | No |  |

### Performance considerations

This connector has been tested for the Airbyte organization, which has 266 repos, and works fine. It should not run into limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* None

### Setup guide

1. Define a `docker_username`: the username that the connector will pull all repo data from.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.0 | 2022-05-20 | [13007](https://github.com/airbytehq/airbyte/pull/13007) | New source |

