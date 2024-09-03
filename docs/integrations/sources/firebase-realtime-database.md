# Firebase Realtime Database

## Overview

The Firebase Realtime Database source supports Full Refresh sync. As the database data is stored as JSON objects and there are no records or tables, you can sync only one stream which you specifed as a JSON node path on your database at a time.

### Resulting schema

As mentioned above, fetched data is just a JSON objects. The resulting records conformed of two columns `key` and `value`. The `key`'s value is keys (string) of fetched JSON object. The `value`'s value is string representation of values (string representation of any JSON object) of fetched JSON object.

If your database has data as below at path `https://{your-database-name}.firebaseio.com/store-a/users.json` ...

```json
{
  "liam": { "address": "somewhere", "age": 24 },
  "olivia": { "address": "somewhere", "age": 30 }
}
```

and you specified a `store-a/users` as a path in configuration, you would sync records like below ...

```json
{"key": "liam", "value": "{\"address\": \"somewhere\", \"age\": 24}}"}
{"key": "olivia", "value": "{\"address\": \"somewhere\", \"age\": 30}}"}
```

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

- A Google Cloud Project with Firebase enabled
- A Google Cloud Service Account with the "Firebase Realtime Database Viewer" roles in your Google Cloud project
- A Service Account Key to authenticate into your Service Account

See the setup guide for more information about how to create the required resources.

#### Service account

In order for Airbyte to sync data from Firebase Realtime Database, it needs credentials for a [Service Account](https://cloud.google.com/iam/docs/service-accounts) with the "Firebase Realtime Database Viewer" roles, which grants permissions to read from Firebase Realtime Database. We highly recommend that this Service Account is exclusive to Airbyte for ease of permissioning and auditing. However, you can use a pre-existing Service Account if you already have one with the correct permissions.

The easiest way to create a Service Account is to follow Google Cloud's guide for [Creating a Service Account](https://cloud.google.com/iam/docs/creating-managing-service-accounts). Once you've created the Service Account, make sure to keep its ID handy as you will need to reference it when granting roles. Service Account IDs typically take the form `<account-name>@<project-name>.iam.gserviceaccount.com`

Then, add the service account as a Member in your Google Cloud Project with the "Firebase Realtime Database Viewer" role. To do this, follow the instructions for [Granting Access](https://cloud.google.com/iam/docs/granting-changing-revoking-access#granting-console) in the Google documentation. The email address of the member you are adding is the same as the Service Account ID you just created.

At this point you should have a service account with the "Firebase Realtime Database" product-level permission.

#### Service account key

Service Account Keys are used to authenticate as Google Service Accounts. For Airbyte to leverage the permissions you granted to the Service Account in the previous step, you'll need to provide its Service Account Keys. See the [Google documentation](https://cloud.google.com/iam/docs/service-accounts#service_account_keys) for more information about Keys.

Follow the [Creating and Managing Service Account Keys](https://cloud.google.com/iam/docs/creating-managing-service-account-keys) guide to create a key. Airbyte currently supports JSON Keys only, so make sure you create your key in that format. As soon as you created the key, make sure to download it, as that is the only time Google will allow you to see its contents. Once you've successfully configured Firebase Realtime Database as a source in Airbyte, delete this key from your computer.

### Setup the Firebase Realtime Database source in Airbyte

You should now have all the requirements needed to configure Firebase Realtime Database as a source in the UI. You'll need the following information to configure the Firebase Realtime Database source:

- **Database Name**
- **Service Account Key JSON**: the contents of your Service Account Key JSON file.
- **Node Path \[Optional\]**: node path in your database's data which you want to sync. default value is ""(root node).
- **Buffer Size \[Optional\]**: number of records to fetch at one time (buffered). default value is 10000.

Once you've configured Firebase Realtime Database as a source, delete the Service Account Key from your computer.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                                    |
| :------ | :--------- | :--------------------------------------------------------- | :----------------------------------------- |
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
