# NASA

## Overview

The NASA source supports full refresh syncs

### Output schema

Asingle output stream is available (at the moment) from this source:

\*[APOD](https://github.com/nasa/apod-api#docs-).

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |
| SSL connection    | No         |
| Namespaces        | No         |

### Performance considerations

The NASA connector should not run into NASA API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- NASA API Key. You can use `DEMO_KEY` (see rate limits [here](https://api.nasa.gov/)).

### Connect using `API Key`:

1. Generate an API Key as described [here](https://api.nasa.gov/).
2. Use the generated `API Key` in the Airbyte connection.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                    |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------------------- |
| 0.2.0   | 2023-10-10 | [31051](https://github.com/airbytehq/airbyte/pull/31051) | Migrate to lowcode                         |
| 0.1.1   | 2023-02-13 | [22934](https://github.com/airbytehq/airbyte/pull/22934) | Specified date formatting in specification |
| 0.1.0   | 2022-10-24 | [18394](https://github.com/airbytehq/airbyte/pull/18394) | 🎉 New Source: NASA APOD                   |
