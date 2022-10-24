# NASA APOD

## Overview

The NASA APOD (Astronomy Picture Of the Day) supports full refresh syncs

### Output schema

There is only one stream available from this source, and its documentation can be found [here](https://github.com/nasa/apod-api#docs-).

### Features

| Feature           | Supported? |
|:------------------|:-----------|
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| SSL connection    | No         |
| Namespaces        | No         |

### Performance considerations

The NASA APOD connector should not run into NASA APOD API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* NASA API Key. You can use `DEMO_KEY` (see rate limits [here](https://api.nasa.gov/)).

### Connect using `API Key`:
1. Generate an API Key as described [here](https://api.nasa.gov/).
2. Use the generated `API Key` in the Airbyte connection.

## Changelog
TODO: add PR id
| Version | Date       | Pull Request                                             | Subject                                         |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------|
| 0.1.0   | 2022-10-24 | [](https://github.com/airbytehq/airbyte/pull/)   | 🎉 New Source: NASA APOD                           |
