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

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                    |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------------------- |
| 0.3.1   | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version   |
| 0.3.0 | 2024-08-15 | [44115](https://github.com/airbytehq/airbyte/pull/44115) | Refactor connector to manifest-only format |
| 0.2.14 | 2024-08-12 | [43907](https://github.com/airbytehq/airbyte/pull/43907) | Update dependencies |
| 0.2.13 | 2024-08-10 | [43625](https://github.com/airbytehq/airbyte/pull/43625) | Update dependencies |
| 0.2.12 | 2024-08-03 | [43295](https://github.com/airbytehq/airbyte/pull/43295) | Update dependencies |
| 0.2.11 | 2024-07-27 | [42592](https://github.com/airbytehq/airbyte/pull/42592) | Update dependencies |
| 0.2.10 | 2024-07-20 | [42163](https://github.com/airbytehq/airbyte/pull/42163) | Update dependencies |
| 0.2.9 | 2024-07-13 | [41776](https://github.com/airbytehq/airbyte/pull/41776) | Update dependencies |
| 0.2.8 | 2024-07-10 | [41545](https://github.com/airbytehq/airbyte/pull/41545) | Update dependencies |
| 0.2.7 | 2024-07-09 | [41154](https://github.com/airbytehq/airbyte/pull/41154) | Update dependencies |
| 0.2.6 | 2024-07-06 | [40764](https://github.com/airbytehq/airbyte/pull/40764) | Update dependencies |
| 0.2.5 | 2024-06-25 | [40416](https://github.com/airbytehq/airbyte/pull/40416) | Update dependencies |
| 0.2.4 | 2024-06-22 | [40114](https://github.com/airbytehq/airbyte/pull/40114) | Update dependencies |
| 0.2.3 | 2024-06-15 | [39498](https://github.com/airbytehq/airbyte/pull/39498) | Make compatible with builder |
| 0.2.2 | 2024-06-06 | [39218](https://github.com/airbytehq/airbyte/pull/39218) | [autopull] Upgrade base image to v1.2.2 |
| 0.2.1 | 2024-05-21 | [38520](https://github.com/airbytehq/airbyte/pull/38520) | [autopull] base image + poetry + up_to_date |
| 0.2.0 | 2023-10-10 | [31051](https://github.com/airbytehq/airbyte/pull/31051) | Migrate to lowcode |
| 0.1.1 | 2023-02-13 | [22934](https://github.com/airbytehq/airbyte/pull/22934) | Specified date formatting in specification |
| 0.1.0 | 2022-10-24 | [18394](https://github.com/airbytehq/airbyte/pull/18394) | 🎉 New Source: NASA APOD |

</details>
