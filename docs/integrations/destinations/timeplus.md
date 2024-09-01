# Timeplus

This page guides you through the process of setting up the [Timeplus](https://timeplus.com)
destination connector.

## Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Overwrite                 | Yes                  |       |
| Incremental - Append Sync | Yes                  |       |

#### Output Schema

Each stream will be output into its own stream in Timeplus, with corresponding schema/columns.

## Getting Started (Airbyte Cloud)

Coming soon...

## Getting Started (Airbyte Open Source)

You can follow the
[Quickstart with Timeplus Ingestion API](https://docs.timeplus.com/quickstart-ingest-api) to createa
a workspace and API key.

### Setup the Timeplus Destination in Airbyte

You should now have all the requirements needed to configure Timeplus as a destination in the UI.
You'll need the following information to configure the Timeplus destination:

- **Endpoint** example https://us.timeplus.cloud/randomId123
- **API key**

## Compatibility

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject              |
|:--------| :--------- | :-------------------------------------------------------- | :------------------- |
| 0.1.18 | 2024-08-31 | [45020](https://github.com/airbytehq/airbyte/pull/45020) | Update dependencies |
| 0.1.17 | 2024-08-24 | [44707](https://github.com/airbytehq/airbyte/pull/44707) | Update dependencies |
| 0.1.16 | 2024-08-22 | [44530](https://github.com/airbytehq/airbyte/pull/44530) | Update test dependencies |
| 0.1.15 | 2024-08-17 | [44363](https://github.com/airbytehq/airbyte/pull/44363) | Update dependencies |
| 0.1.14 | 2024-08-12 | [43854](https://github.com/airbytehq/airbyte/pull/43854) | Update dependencies |
| 0.1.13 | 2024-08-03 | [43216](https://github.com/airbytehq/airbyte/pull/43216) | Update dependencies |
| 0.1.12 | 2024-07-27 | [42761](https://github.com/airbytehq/airbyte/pull/42761) | Update dependencies |
| 0.1.11 | 2024-07-20 | [42354](https://github.com/airbytehq/airbyte/pull/42354) | Update dependencies |
| 0.1.10 | 2024-07-13 | [41861](https://github.com/airbytehq/airbyte/pull/41861) | Update dependencies |
| 0.1.9 | 2024-07-10 | [41392](https://github.com/airbytehq/airbyte/pull/41392) | Update dependencies |
| 0.1.8 | 2024-07-09 | [41257](https://github.com/airbytehq/airbyte/pull/41257) | Update dependencies |
| 0.1.7 | 2024-07-06 | [40864](https://github.com/airbytehq/airbyte/pull/40864) | Update dependencies |
| 0.1.6 | 2024-06-25 | [40270](https://github.com/airbytehq/airbyte/pull/40270) | Update dependencies |
| 0.1.5 | 2024-06-22 | [39990](https://github.com/airbytehq/airbyte/pull/39990) | Update dependencies |
| 0.1.4 | 2024-06-06 | [39301](https://github.com/airbytehq/airbyte/pull/39301) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.3 | 2024-06-03 | [38901](https://github.com/airbytehq/airbyte/pull/38901) | Replace AirbyteLogger with logging.Logger |
| 0.1.2 | 2024-05-21 | [38491](https://github.com/airbytehq/airbyte/pull/38491) | [autopull] base image + poetry + up_to_date |
| 0.1.1   | 2024-03-05 | [#35838](https://github.com/airbytehq/airbyte/pull/35838) | Un-archive connector |
| 0.1.0   | 2023-06-14 | [21226](https://github.com/airbytehq/airbyte/pull/21226)  | Destination Timeplus |

</details>
