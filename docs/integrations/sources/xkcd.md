# XKCD

This page guides you through the process of setting up the xkcd source connector.

## Prerequisites

XKCD is an open API, so no credentials are needed to set up the surce.

## Supported sync modes

The xkcd source connector supports on full sync refresh.

## Supported Streams

That is just one stream for xkcd, that retrieves a given comic metadata.

### Performance considerations

XKCD does not perform rate limiting.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                   |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------------- |
| 0.1.5 | 2024-04-19 | [37294](https://github.com/airbytehq/airbyte/pull/37294) | Updating to 0.80.0 CDK |
| 0.1.4 | 2024-04-18 | [37294](https://github.com/airbytehq/airbyte/pull/37294) | Manage dependencies with Poetry. |
| 0.1.3 | 2024-04-15 | [37294](https://github.com/airbytehq/airbyte/pull/37294) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.2 | 2024-04-12 | [37294](https://github.com/airbytehq/airbyte/pull/37294) | schema descriptions |
| 0.1.1 | 2022-10-24 | [18386](https://github.com/airbytehq/airbyte/pull/18386) | Readded xkcd to source def yaml |
| 0.1.0 | 2022-10-17 | [18049](https://github.com/airbytehq/airbyte/pull/18049) | Initial version/release of the connector. |
