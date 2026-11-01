# Redis source

The Redis source currently supports connection checks and static stream
discovery. Record reading is in progress and is not available in this version.

## Prerequisites

- Redis 6.0 or newer. The check verifies Redis version information when the
  configured ACL user is allowed to run `INFO`; it also probes `SCAN TYPE`.
- Network access from Airbyte to the Redis host and port.
- For ACL authentication, a username and password with permission to connect,
  run `SCAN`, and run `DBSIZE`. `INFO` is optional; the check tolerates an ACL
  denial for that command.

## Setup

1. Enter the Redis host and port. The default port is `6379`.
2. Optionally configure an ACL username and password. The password is stored
   as a secret. A password can also be supplied when the Redis default user
   does not require authentication.
3. Select the logical database index (default `0`).
4. Choose an SSL mode:
   - **Disable**: connect without TLS.
   - **Require**: use TLS without validating the server certificate.
   - **Verify CA**: validate the server certificate using the configured CA
     certificate, or the system trust store if no CA certificate is supplied.
   - **Verify Full**: verify both the certificate authority and the Redis
     server hostname. This mode cannot be used through an SSH tunnel.
5. Optionally configure an SSH tunnel if Redis is only reachable through a
   bastion host.

The client certificate, client key, and optional key password are used for
mutual TLS when configured with a verification mode. Configure both a client
certificate and key together.

The `key_pattern`, `scan_batch_size`, `checkpoint_target_interval_seconds`,
and `max_db_connections` settings are reserved for the planned record-reading
implementation. They do not affect connection checks or static discovery in
this version.

## Streams and data model

Discovery is static and does not inspect the Redis keyspace. It always returns
the following streams, whether the selected database is empty or populated:

| Stream | Fields | Primary key | Sync modes |
| --- | --- | --- | --- |
| `strings` | `key` (string), `value` (string), `ttl` (integer) | `key` | Full refresh |
| `hashes` | `key` (string), `value` (object of string values), `ttl` (integer) | `key` | Full refresh |
| `lists` | `key` (string), `value` (array of strings), `ttl` (integer) | `key` | Full refresh |
| `sets` | `key` (string), `value` (array of strings), `ttl` (integer) | `key` | Full refresh |
| `sorted_sets` | `key` (string), `value` (array of `{member, score}` objects), `ttl` (integer) | `key` | Full refresh |
| `streams` | `key` (string), `id` (string), `fields` (object of string values) | `key`, `id` | Full refresh, incremental (`id` cursor) |

## TLS and SSH

Use **Verify CA** for encrypted connections through a tunnel when certificate
hostname verification is not possible. **Verify Full** cannot be combined
with SSH tunneling because the local tunnel endpoint is not the Redis
server's certificate hostname. Do not use **Require** for production unless
certificate validation is handled by another trusted layer.

## Limitations

- Redis Cluster mode is not supported.
- Reading records is not implemented yet.
- Verify Full cannot be used through an SSH tunnel.
- Discovery is static; the six stream definitions are returned without
  scanning keys.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull request | Description |
| --- | --- | --- | --- |
| 0.1.0 | 2026-10-20 | [TBD](https://github.com/airbytehq/airbyte/pull/TBD) | New Bulk CDK connector: spec, check and discover |

</details>
