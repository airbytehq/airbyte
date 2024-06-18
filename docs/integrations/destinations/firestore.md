# Firestore

This destination writes data to Google Firestore.

Google Firestore, officially known as Cloud Firestore, is a flexible, scalable database for mobile, web, and server development from Firebase and Google Cloud. It is commonly used for developing applications as a NoSQL database that provides real-time data syncing across user devices.

## Getting started

### Requiremnets

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
| :------ | :--------- | :----------------------------------------------------- | :---------------------------- |
| 0.1.4 | 2024-06-06 | [39149](https://github.com/airbytehq/airbyte/pull/39149) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.3 | 2024-06-03 | [38902](https://github.com/airbytehq/airbyte/pull/38902) | Replace AirbyteLogger with logging.Logger |
| 0.1.2 | 2024-05-20 | [38422](https://github.com/airbytehq/airbyte/pull/38422) | [autopull] base image + poetry + up_to_date |
| 0.1.1 | 2021-11-21 | [8158](https://github.com/airbytehq/airbyte/pull/8158) | Publish Destination Firestore |

</details>
