# SFTP JSON

## Overview

This destination writes data to a directory on an SFTP server.

### Sync Overview

#### Output schema

Each stream will be output into its own file.
Each file will contain a collection of `json` objects which correspond directly with the data supplied by the source.

#### Performance considerations

This integration will be constrained by the connection speed to the SFTP server and speed at which that server accepts writes.

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | No |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | No |

## Getting Started

The `destination_path` can refer to any path that the associated account has write permissions to.

The `filename` **should not** have an extension in the configuration, as `.jsonl` will be added on by the connector.

### Authentication

The connector supports two authentication methods:

- **Password authentication** (`SSH_PASSWORD_AUTH`): Connect with a username and password.
- **SSH key authentication** (`SSH_KEY_AUTH`): Connect with a username and an SSH private key (RSA, Ed25519, or ECDSA in PEM/OpenSSH format).

### Host Key Checking

By default, the connector uses `auto_add` mode, which accepts and logs a warning for unknown server host keys on first connection. **This does not protect against man-in-the-middle (MITM) attacks.** An attacker who can intercept the initial connection could present their own key, and the connector would accept it.

For production environments where MITM protection is important, use `strict` mode and supply the server's expected host key. You can obtain the host key by running:

```bash
ssh-keyscan -t ed25519 your-sftp-host.example.com
```

Then configure `host_key_checking` with `mode: strict`, the `host_key_type` (e.g., `ssh-ed25519`), and the base64-encoded `host_key`.

### Example:

If `destination_path` is set to `/myfolder/files` and `filename` is set to `mydata`, the resulting file will be `/myfolder/files/mydata.jsonl`.

These files can then be accessed by creating an SFTP connection to the server and navigating to the `destination_path`.

## Namespace support

This destination does not support [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                           | Subject                       |
| :------ | :--------- | :----------------------------------------------------- | :---------------------------- |
| 1.0.0 | 2026-08-20 | [79620](https://github.com/airbytehq/airbyte/pull/79620) | Add SSH key authentication, host key checking, and migrate to paramiko (breaking: `password` replaced by `credentials` block). See [migration guide](sftp-json-migrations.md). |
| 0.2.16 | 2026-05-15 | [78111](https://github.com/airbytehq/airbyte/pull/78111) | Fixed SFTP connection checks for passwords with URI-reserved characters. |
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
