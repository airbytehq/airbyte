# KVdb

This page contains the setup guide and reference information for the [KVdb](https://kvdb.io/) destination connector.

KVdb is a hosted key-value store with a REST API. This connector writes source records to a KVdb bucket.

:::note
KVdb is disabled in Airbyte's default Cloud and Self-Managed connector registries. These instructions apply to installations where the connector has been added separately; it might not appear in the destination picker.
:::

## Prerequisites

- A KVdb bucket that was created with a `secret_key`. KVdb doesn't let you add a secret key to a bucket after it's created, so set one when you create the bucket.
- The bucket ID that KVdb returns when you create the bucket.

## Setup guide

1. [Create a bucket](https://kvdb.io/docs/api/#create-a-bucket) with a secret key and a valid email address. KVdb returns its bucket ID.
2. Configure the KVdb destination's **Bucket ID** and **Secret Key** fields with those values.

When you test the connection, the connector writes a test key with a random UUID name to the bucket and then deletes it.

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | No |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | No |

In overwrite mode, the connector deletes every key that starts with `<stream_name>__ab__` at the start of the sync, then writes the new records.

## Output schema

The connector writes each record as one key-value pair:

- **Key**: `<stream_name>__ab__<timestamp>`, where `<timestamp>` is the time, in milliseconds since the Unix epoch, when the connector processed the record. The timestamp can include a fractional part, for example `users__ab__1728738000123.456`.
- **Value**: the record's data as a JSON object.

The connector doesn't use the source's primary key. To read the records for a stream, [list the bucket's keys](https://kvdb.io/docs/api/#list-keys) with the `<stream_name>__ab__` prefix.

The connector writes records in batches of up to 1,000 using the KVdb [transaction API](https://kvdb.io/docs/api/#execute-transaction).

## Limitations

These limits come from KVdb. For current values, see the [KVdb API documentation](https://kvdb.io/docs/api/) and [pricing](https://kvdb.io/pricing).

- **Key expiration**: By default, KVdb deletes keys that aren't updated within one week. Disabling expiration or extending it beyond one week requires a paid KVdb plan.
- **Value size**: Each value can be up to 16 KB. Records larger than this can't be stored.
- **Key length**: Keys can be up to 128 bytes, including the `__ab__<timestamp>` suffix. Very long stream names can exceed this limit.
- **Rate limits**: KVdb allows 1,000 requests per IP address per hour, with higher limits on paid plans. KVdb returns HTTP 429 when you exceed the limit. Each batch of up to 1,000 records is one request, and overwrite syncs make additional requests to list and delete existing keys.

## Namespace support

This destination does not support [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                                                    |
|:--------| :--------- | :-------------------------------------------------------- | :------------------------------------------------------------------------- |
| 0.1.12  | 2026-10-12 | [88413](https://github.com/airbytehq/airbyte/pull/88413) | Mark `secret_key` as `airbyte_secret`; fix the image entrypoint and move to Python 3.11 (base image 4.0.0) |
| 0.1.11  | 2024-08-22 | [44530](https://github.com/airbytehq/airbyte/pull/44530) | Update test dependencies                                     |
| 0.1.10  | 2024-07-09 | [41285](https://github.com/airbytehq/airbyte/pull/41285) | Update dependencies |
| 0.1.9   | 2024-07-06 | [40796](https://github.com/airbytehq/airbyte/pull/40796) | Update dependencies |
| 0.1.8   | 2024-06-25 | [40409](https://github.com/airbytehq/airbyte/pull/40409) | Update dependencies |
| 0.1.7   | 2024-06-22 | [40016](https://github.com/airbytehq/airbyte/pull/40016) | Update dependencies |
| 0.1.6   | 2024-06-06 | [39236](https://github.com/airbytehq/airbyte/pull/39236) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.5   | 2024-06-03 | [38894](https://github.com/airbytehq/airbyte/pull/38894) | Replace AirbyteLogger with logging.Logger |
| 0.1.4   | 2024-03-05 | [#35838](https://github.com/airbytehq/airbyte/pull/35838) | Un-archive connector                                                       |
| 0.1.3   | 2024-02-20 | [35424](https://github.com/airbytehq/airbyte/pull/35424) | bump connector version to publish, convert to base docker image and poetry |
| 0.1.2   | 2024-02-19 | [35422](https://github.com/airbytehq/airbyte/pull/35422)  | bump connector version to publish                                          |
| 0.1.1   | 2024-02-16 | [35370](https://github.com/airbytehq/airbyte/pull/35370)  | bump connector version to publish                                          |
| 0.1.0   | 2021-07-19 | [4786](https://github.com/airbytehq/airbyte/pull/4786)    | Python Demo Destination: KVDB                                              |

</details>
