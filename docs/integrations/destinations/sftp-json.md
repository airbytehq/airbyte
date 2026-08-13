# SFTP JSON

This destination writes each stream to a newline-delimited JSON file in a directory on an SFTP server.

## Prerequisites

- An SFTP server reachable from your Airbyte deployment.
- A username and password for that server. This destination authenticates with a password only. It doesn't support SSH key or keyboard-interactive authentication.
- An existing directory on the server that the account can read from and write to. The connector doesn't create the directory for you.

## Setup

Configure the following fields:

| Field | Required | Default | Description |
| :--- | :--- | :--- | :--- |
| **Host** | Yes | | Hostname or IP address of the SFTP server. |
| **Port** | No | `22` | Port the SFTP server listens on. |
| **User** | Yes | | Username used to sign in to the server. |
| **Password** | Yes | | Password for that username. |
| **Destination path** | Yes | | Absolute path to the directory where the connector writes files, such as `/json_data`. |

When you test the connection, the connector writes a small file to **Destination path** and then deletes it, so the account needs write and delete permissions in that directory, not just read access.

## Output files

The connector writes one file per stream and names it after the stream:

```text
{destination_path}/airbyte_json_{stream_name}.jsonl
```

For example, if **Destination path** is `/json_data` and you sync a stream named `users`, the connector writes `/json_data/airbyte_json_users.jsonl`.

Each line in the file is a single JSON object holding the record exactly as the source emitted it. The connector doesn't add Airbyte metadata fields such as `_airbyte_raw_id` or `_airbyte_extracted_at`, so the file contains only your source data.

Because the file name comes from the stream name alone, two streams with the same name in different namespaces write to the same file. This destination doesn't support [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces).

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | No |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | No |

In overwrite mode, the connector deletes the stream's existing file at the start of the sync and writes a new one. In the append modes, it appends records to the end of the existing file and never rewrites earlier lines, so records from failed or partial syncs stay in the file. Deduplicate downstream if that matters to you.

## Performance considerations

Throughput depends on your network connection to the SFTP server and how quickly the server accepts writes. The connector holds one open file handle per stream and writes records as it receives them, so it doesn't batch or compress data.

## Troubleshooting

### The connection test fails with an authentication error

Confirm that the server accepts password authentication for this account. Servers configured for public key authentication only reject this connector.

### The connection test fails but the credentials are correct

Check that **Destination path** already exists and that the account can write to it and delete files in it. The connector doesn't create missing directories.

### Passwords containing special characters

Version 0.2.16 and later percent-encode the username, password, host, and path before building the SFTP URI, so credentials containing characters such as `#`, `@`, `/`, or `?` work as entered. On earlier versions, these characters truncated or corrupted the URI and syncs and connection tests failed. If you're on an earlier version, upgrade rather than changing the password.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                           | Subject                       |
| :------ | :--------- | :----------------------------------------------------- | :---------------------------- |
| 0.2.16 | 2026-08-13 | [78111](https://github.com/airbytehq/airbyte/pull/78111) | Escape URI-reserved characters in credentials and paths, fixing syncs and connection checks for passwords containing characters such as `#` |
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
