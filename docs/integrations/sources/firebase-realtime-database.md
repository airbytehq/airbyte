# Firebase Realtime Database

## Overview

The Firebase Realtime Database source supports Full Refresh sync of one stream per source. Configure **Node Path** to select the JSON node to sync. To sync multiple paths independently, create a source for each path.

### Resulting schema

The connector emits one record for each immediate child of the selected node, with two string fields:

- `key`: the child's key.
- `value`: the child's value serialized as JSON. Nested objects remain inside this string.

For example, if `store-a/users` contains:

```json
{
  "liam": { "address": "somewhere", "age": 24 },
  "olivia": { "address": "somewhere", "age": 30 }
}
```

Set **Node Path** to `store-a/users` to sync these records:

```json
[
  {"key": "liam", "value": "{\"address\": \"somewhere\", \"age\": 24}"},
  {"key": "olivia", "value": "{\"address\": \"somewhere\", \"age\": 30}"}
]
```

The stream name is the final segment of **Node Path**, with hyphens replaced by underscores. For this example, the stream name is `users`. If you leave **Node Path** empty, the connector uses **Database Name**, with hyphens replaced by underscores, as the stream name.

### Features

| Feature             | Supported | Notes |
| :------------------ | :-------- | :---- |
| Full Refresh Sync   | Yes       |       |
| Incremental Sync    | No        |       |
| Change Data Capture | No        |       |
| SSL Support         | Yes       |       |

## Getting started

### Requirements

To use the Firebase Realtime Database source, you'll need:

- A Firebase project with a Realtime Database instance and its database URL.
- A Google Cloud service account with the **Firebase Realtime Database Viewer** role (`roles/firebasedatabase.viewer`) in that project.
- A service account key in JSON format.

Select a node whose data is a JSON object keyed by child names, as shown in the record example. The connector expects key-value pairs at this level. Select the parent object rather than an individual scalar value.

#### Service account

1. [Create a service account](https://cloud.google.com/iam/docs/creating-managing-service-accounts), or use an existing one. A dedicated account makes it easier to manage and audit Airbyte's access.
2. [Grant the service account access to your project](https://cloud.google.com/iam/docs/granting-changing-revoking-access#granting-console) with the [Firebase Realtime Database Viewer role](https://firebase.google.com/docs/projects/iam/roles-predefined-product#realtime-database). Use the service account's email address, such as `<account-name>@<project-name>.iam.gserviceaccount.com`, as the principal.

The connector authenticates through the [Firebase Admin SDK](https://firebase.google.com/docs/database/admin/start). Its connection check reads the database root's keys, even when **Node Path** selects a child node.

#### Service account key

Follow Google's [Create and delete service account keys](https://cloud.google.com/iam/docs/creating-managing-service-account-keys) guide to create and download a JSON key for the service account. Airbyte requires the contents of the JSON file, rather than its filename. After saving the credentials in Airbyte, delete the local copy of the downloaded file.

### Set up the Firebase Realtime Database source in Airbyte

Create a Firebase Realtime Database source in Airbyte and enter the following settings:

- **Database Name**: the name of your database (for databases in `us-central1`, this is the `<database_name>` in `https://<database_name>.firebaseio.com`). If your database is in another region (for example `europe-west1` or `asia-southeast1`), enter the full database URL or hostname instead, e.g. `https://<database_name>.europe-west1.firebasedatabase.app`. You can find the URL in the Firebase console; see [Realtime Database locations](https://firebase.google.com/docs/database/locations).
- **Service Account Key JSON**: the contents of your Service Account Key JSON file.
- **Node Path \[Optional\]**: the path within the database to sync, such as `store-a/users`. Enter a node path without the database URL or a `.json` suffix. Leave it empty to sync the root node.
- **Buffer Size \[Optional\]**: the number of child records to fetch per request. The default is `10000`. Use an integer of at least `2`: pagination includes the previous page's last key, so a buffer size of `1` stops after the first record.

## Limitations

- Each sync reads all records at the configured path.
- An empty or nonexistent node produces no records.
- Firebase limits each read response to 256 MB and queries to paths containing at most 75 million nodes. See [Realtime Database limits](https://firebase.google.com/docs/database/usage/limits) for current quotas. If a read exceeds the response size limit, reduce **Buffer Size** or select a smaller subtree with **Node Path**. Each request includes the child's nested data, so reducing **Buffer Size** can't split an oversized child value.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                                    |
| :------ | :--------- | :--------------------------------------------------------- | :----------------------------------------- |
| 0.1.56 | 2026-11-11 | [90912](https://github.com/airbytehq/airbyte/pull/90912) | Drop support for Python 3.10; Python package installations require Python 3.11–3.13 |
| 0.1.55 | 2026-11-10 | [91505](https://github.com/airbytehq/airbyte/pull/91505) | Update dependencies |
| 0.1.54 | 2026-11-03 | [90548](https://github.com/airbytehq/airbyte/pull/90548) | Update dependencies |
| 0.1.53 | 2026-10-27 | [89874](https://github.com/airbytehq/airbyte/pull/89874) | Update dependencies |
| 0.1.52 | 2026-10-20 | [89214](https://github.com/airbytehq/airbyte/pull/89214) | Update dependencies |
| 0.1.51 | 2026-10-13 | [79248](https://github.com/airbytehq/airbyte/pull/79248) | Update dependencies |
| 0.1.50 | 2026-10-07 | [88178](https://github.com/airbytehq/airbyte/pull/88178) | Support databases outside `us-central1` by accepting a full database URL/hostname (`*.firebasedatabase.app`) in **Database Name**; upgrade to airbyte-cdk 7 / Python 3.13 so the image builds on the current base image |
| 0.1.49 | 2026-06-02 | [78673](https://github.com/airbytehq/airbyte/pull/78673) | Update dependencies |
| 0.1.48 | 2025-05-24 | [60381](https://github.com/airbytehq/airbyte/pull/60381) | Update dependencies |
| 0.1.47 | 2025-05-10 | [59978](https://github.com/airbytehq/airbyte/pull/59978) | Update dependencies |
| 0.1.46 | 2025-05-03 | [59371](https://github.com/airbytehq/airbyte/pull/59371) | Update dependencies |
| 0.1.45 | 2025-04-26 | [58854](https://github.com/airbytehq/airbyte/pull/58854) | Update dependencies |
| 0.1.44 | 2025-04-19 | [58347](https://github.com/airbytehq/airbyte/pull/58347) | Update dependencies |
| 0.1.43 | 2025-04-12 | [57755](https://github.com/airbytehq/airbyte/pull/57755) | Update dependencies |
| 0.1.42 | 2025-04-05 | [57229](https://github.com/airbytehq/airbyte/pull/57229) | Update dependencies |
| 0.1.41 | 2025-03-29 | [56477](https://github.com/airbytehq/airbyte/pull/56477) | Update dependencies |
| 0.1.40 | 2025-03-22 | [55992](https://github.com/airbytehq/airbyte/pull/55992) | Update dependencies |
| 0.1.39 | 2025-03-08 | [55297](https://github.com/airbytehq/airbyte/pull/55297) | Update dependencies |
| 0.1.38 | 2025-03-01 | [54911](https://github.com/airbytehq/airbyte/pull/54911) | Update dependencies |
| 0.1.37 | 2025-02-22 | [54371](https://github.com/airbytehq/airbyte/pull/54371) | Update dependencies |
| 0.1.36 | 2025-02-15 | [53755](https://github.com/airbytehq/airbyte/pull/53755) | Update dependencies |
| 0.1.35 | 2025-02-01 | [52844](https://github.com/airbytehq/airbyte/pull/52844) | Update dependencies |
| 0.1.34 | 2025-01-25 | [52328](https://github.com/airbytehq/airbyte/pull/52328) | Update dependencies |
| 0.1.33 | 2025-01-18 | [51639](https://github.com/airbytehq/airbyte/pull/51639) | Update dependencies |
| 0.1.32 | 2025-01-11 | [51105](https://github.com/airbytehq/airbyte/pull/51105) | Update dependencies |
| 0.1.31 | 2025-01-04 | [50924](https://github.com/airbytehq/airbyte/pull/50924) | Update dependencies |
| 0.1.30 | 2024-12-28 | [50561](https://github.com/airbytehq/airbyte/pull/50561) | Update dependencies |
| 0.1.29 | 2024-12-21 | [50006](https://github.com/airbytehq/airbyte/pull/50006) | Update dependencies |
| 0.1.28 | 2024-12-14 | [49186](https://github.com/airbytehq/airbyte/pull/49186) | Update dependencies |
| 0.1.27 | 2024-11-25 | [48653](https://github.com/airbytehq/airbyte/pull/48653) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.1.26 | 2024-11-04 | [47041](https://github.com/airbytehq/airbyte/pull/47041) | Update dependencies |
| 0.1.25 | 2024-10-12 | [46799](https://github.com/airbytehq/airbyte/pull/46799) | Update dependencies |
| 0.1.24 | 2024-10-05 | [46457](https://github.com/airbytehq/airbyte/pull/46457) | Update dependencies |
| 0.1.23 | 2024-09-28 | [46135](https://github.com/airbytehq/airbyte/pull/46135) | Update dependencies |
| 0.1.22 | 2024-09-21 | [45804](https://github.com/airbytehq/airbyte/pull/45804) | Update dependencies |
| 0.1.21 | 2024-09-14 | [45505](https://github.com/airbytehq/airbyte/pull/45505) | Update dependencies |
| 0.1.20 | 2024-09-07 | [45272](https://github.com/airbytehq/airbyte/pull/45272) | Update dependencies |
| 0.1.19 | 2024-08-31 | [45055](https://github.com/airbytehq/airbyte/pull/45055) | Update dependencies |
| 0.1.18 | 2024-08-24 | [44674](https://github.com/airbytehq/airbyte/pull/44674) | Update dependencies |
| 0.1.17 | 2024-08-17 | [44299](https://github.com/airbytehq/airbyte/pull/44299) | Update dependencies |
| 0.1.16 | 2024-08-12 | [43795](https://github.com/airbytehq/airbyte/pull/43795) | Update dependencies |
| 0.1.15 | 2024-08-10 | [43600](https://github.com/airbytehq/airbyte/pull/43600) | Update dependencies |
| 0.1.14 | 2024-08-03 | [43092](https://github.com/airbytehq/airbyte/pull/43092) | Update dependencies |
| 0.1.13 | 2024-07-27 | [42609](https://github.com/airbytehq/airbyte/pull/42609) | Update dependencies |
| 0.1.12 | 2024-07-20 | [42260](https://github.com/airbytehq/airbyte/pull/42260) | Update dependencies |
| 0.1.11 | 2024-07-13 | [41900](https://github.com/airbytehq/airbyte/pull/41900) | Update dependencies |
| 0.1.10 | 2024-07-10 | [41469](https://github.com/airbytehq/airbyte/pull/41469) | Update dependencies |
| 0.1.9 | 2024-07-06 | [40816](https://github.com/airbytehq/airbyte/pull/40816) | Update dependencies |
| 0.1.8 | 2024-06-29 | [40628](https://github.com/airbytehq/airbyte/pull/40628) | Update dependencies |
| 0.1.7 | 2024-06-26 | [40538](https://github.com/airbytehq/airbyte/pull/40538) | Update dependencies |
| 0.1.6 | 2024-06-25 | [40328](https://github.com/airbytehq/airbyte/pull/40328) | Update dependencies |
| 0.1.5 | 2024-06-22 | [40181](https://github.com/airbytehq/airbyte/pull/40181) | Update dependencies |
| 0.1.4 | 2024-06-06 | [39200](https://github.com/airbytehq/airbyte/pull/39200) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.3 | 2024-06-03 | [38910](https://github.com/airbytehq/airbyte/pull/38910) | Replace AirbyteLogger with logging.Logger |
| 0.1.2 | 2024-06-03 | [38910](https://github.com/airbytehq/airbyte/pull/38910) | Replace AirbyteLogger with logging.Logger |
| 0.1.1 | 2024-05-20 | [38416](https://github.com/airbytehq/airbyte/pull/38416) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2022-10-16 | [\#18029](https://github.com/airbytehq/airbyte/pull/18029) | 🎉 New Source: Firebase Realtime Database. |

</details>
