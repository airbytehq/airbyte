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
| :------ | :--------- | :-------------------------------------------------------- | :------------------- |
| 0.1.5 | 2024-06-22 | [39990](https://github.com/airbytehq/airbyte/pull/39990) | Update dependencies |
| 0.1.4 | 2024-06-06 | [39301](https://github.com/airbytehq/airbyte/pull/39301) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.3 | 2024-06-03 | [38901](https://github.com/airbytehq/airbyte/pull/38901) | Replace AirbyteLogger with logging.Logger |
| 0.1.2 | 2024-05-21 | [38491](https://github.com/airbytehq/airbyte/pull/38491) | [autopull] base image + poetry + up_to_date |
| 0.1.1   | 2024-03-05 | [#35838](https://github.com/airbytehq/airbyte/pull/35838) | Un-archive connector |
| 0.1.0   | 2023-06-14 | [21226](https://github.com/airbytehq/airbyte/pull/21226)  | Destination Timeplus |

</details>
