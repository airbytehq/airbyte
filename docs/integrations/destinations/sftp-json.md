# SFTP JSON

## Overview

This destination writes data to a directory on an SFTP server.

### Sync Overview

#### Output schema

Each stream will be output into its own file.
Each file will contain a collection of `json` objects which correspond directly with the data supplied by the source.

#### Features

| Feature                   | Supported |
| :------------------------ | :-------- |
| Full Refresh Sync         | Yes       |
| Incremental - Append Sync | Yes       |
| Namespaces                | No        |

#### Performance considerations

This integration will be constrained by the connection speed to the SFTP server and speed at which that server accepts writes.

## Getting Started

The `destination_path` can refer to any path that the associated account has write permissions to.

The `filename` **should not** have an extension in the configuration, as `.jsonl` will be added on by the connector.

### Example:

If `destination_path` is set to `/myfolder/files` and `filename` is set to `mydata`, the resulting file will be `/myfolder/files/mydata.jsonl`.

These files can then be accessed by creating an SFTP connection to the server and navigating to the `destination_path`.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                           | Subject                       |
| :------ | :--------- | :----------------------------------------------------- | :---------------------------- |
| 0.2.15 | 2025-05-27 | [60870](https://github.com/airbytehq/airbyte/pull/60870) | Update dependencies |
| 0.2.14 | 2025-05-10 | [59809](https://github.com/airbytehq/airbyte/pull/59809) | Update dependencies |
| 0.2.13 | 2025-05-03 | [59353](https://github.com/airbytehq/airbyte/pull/59353) | Update dependencies |
| 0.2.12 | 2025-04-26 | [58727](https://github.com/airbytehq/airbyte/pull/58727) | Update dependencies |
| 0.2.11 | 2025-04-19 | [58238](https://github.com/airbytehq/airbyte/pull/58238) | Update dependencies |
| 0.2.10 | 2025-04-12 | [57592](https://github.com/airbytehq/airbyte/pull/57592) | Update dependencies |
| 0.2.9 | 2025-04-05 | [57114](https://github.com/airbytehq/airbyte/pull/57114) | Update dependencies |
| 0.2.8 | 2025-03-29 | [56615](https://github.com/airbytehq/airbyte/pull/56615) | Update dependencies |
| 0.2.7 | 2025-03-22 | [56090](https://github.com/airbytehq/airbyte/pull/56090) | Update dependencies |
| 0.2.6 | 2025-03-08 | [55369](https://github.com/airbytehq/airbyte/pull/55369) | Update dependencies |
| 0.2.5 | 2025-03-01 | [54868](https://github.com/airbytehq/airbyte/pull/54868) | Update dependencies |
| 0.2.4 | 2025-02-22 | [54265](https://github.com/airbytehq/airbyte/pull/54265) | Update dependencies |
| 0.2.3 | 2025-02-15 | [53941](https://github.com/airbytehq/airbyte/pull/53941) | Update dependencies |
| 0.2.2 | 2025-02-08 | [53405](https://github.com/airbytehq/airbyte/pull/53405) | Update dependencies |
| 0.2.1 | 2025-02-01 | [52883](https://github.com/airbytehq/airbyte/pull/52883) | Update dependencies |
| 0.2.0 | 2024-10-14 | [46873](https://github.com/airbytehq/airbyte/pull/46873) | Migrated to Poetry and Airbyte Base Image |
| 0.1.0 | 2022-11-24 | [4924](https://github.com/airbytehq/airbyte/pull/4924) | 🎉 New Destination: SFTP JSON |

</details>
