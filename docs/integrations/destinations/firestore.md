# Firestore

This destination writes data to Google Firestore.

Google Firestore, officially known as Cloud Firestore, is a flexible, scalable database for mobile, web, and server development from Firebase and Google Cloud. It is commonly used for developing applications as a NoSQL database that provides real-time data syncing across user devices.

## Getting started

### Requirements

- An existing GCP project
- A role with permissions to create a Service Account Key in GCP

### Step 1: Create a Service Account

1. Log in to the Google Cloud Console. Select the project where your Firestore database is located.
2. Navigate to "IAM & Admin" and select "Service Accounts". Create a Service Account and assign appropriate roles. Ensure “Cloud Datastore User” or “Firebase Rules System” are enabled.
3. Navigate to the service account and generate the JSON key. Download and copy the contents to the configuration.

## Sync overview

### Output schema

Each stream will be output into a BigQuery table.

#### Features

| Feature                        | Supported?\(Yes/No\) | Notes |
| :----------------------------- | :------------------- | :---- |
| Full Refresh Sync              | ✅                   |       |
| Incremental - Append Sync      | ✅                   |       |
| Incremental - Append + Deduped | ✅                   |       |
| Namespaces                     | ✅                   |       |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                           | Subject                       |
|:--------| :--------- | :----------------------------------------------------- | :---------------------------- |
| 0.2.9 | 2025-01-25 | [52152](https://github.com/airbytehq/airbyte/pull/52152) | Update dependencies |
| 0.2.8 | 2025-01-11 | [51229](https://github.com/airbytehq/airbyte/pull/51229) | Update dependencies |
| 0.2.7 | 2025-01-04 | [50911](https://github.com/airbytehq/airbyte/pull/50911) | Update dependencies |
| 0.2.6 | 2024-12-28 | [50507](https://github.com/airbytehq/airbyte/pull/50507) | Update dependencies |
| 0.2.5 | 2024-12-21 | [50212](https://github.com/airbytehq/airbyte/pull/50212) | Update dependencies |
| 0.2.4 | 2024-12-14 | [49294](https://github.com/airbytehq/airbyte/pull/49294) | Update dependencies |
| 0.2.3 | 2024-11-25 | [48681](https://github.com/airbytehq/airbyte/pull/48681) | Update dependencies |
| 0.2.2 | 2024-11-04 | [48223](https://github.com/airbytehq/airbyte/pull/48223) | Update dependencies |
| 0.2.1 | 2024-10-29 | [43758](https://github.com/airbytehq/airbyte/pull/43758) | Update dependencies |
| 0.2.0 | 2024-10-14 | [46874](https://github.com/airbytehq/airbyte/pull/46874) | Bump Airbyte CDK version to 5.13 |
| 0.1.8 | 2024-08-22 | [44530](https://github.com/airbytehq/airbyte/pull/44530) | Update test dependencies |
| 0.1.7 | 2024-07-06 | [40834](https://github.com/airbytehq/airbyte/pull/40834) | Update dependencies |
| 0.1.6 | 2024-06-25 | [40477](https://github.com/airbytehq/airbyte/pull/40477) | Update dependencies |
| 0.1.5 | 2024-06-22 | [40053](https://github.com/airbytehq/airbyte/pull/40053) | Update dependencies |
| 0.1.4 | 2024-06-06 | [39149](https://github.com/airbytehq/airbyte/pull/39149) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.3 | 2024-06-03 | [38902](https://github.com/airbytehq/airbyte/pull/38902) | Replace AirbyteLogger with logging.Logger |
| 0.1.2 | 2024-05-20 | [38422](https://github.com/airbytehq/airbyte/pull/38422) | [autopull] base image + poetry + up_to_date |
| 0.1.1 | 2021-11-21 | [8158](https://github.com/airbytehq/airbyte/pull/8158) | Publish Destination Firestore |

</details>
