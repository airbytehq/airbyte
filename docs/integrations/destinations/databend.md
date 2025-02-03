# Databend

This page guides you through the process of setting up the [Databend](https://databend.rs/)
destination connector.

## Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | Yes                  |       |

#### Output Schema

Each stream will be output into its own table in Databend. Each table will contain 3 columns:

- `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in
  Databend is `VARCHAR`.
- `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source.
  The column type in Databend is `TIMESTAMP`.
- `_airbyte_data`: a json blob representing with the event data. The column type in Databend is
  `VARVHAR`.

## Getting Started (Airbyte Cloud)

Coming soon...

## Getting Started (Airbyte Open Source)

You can follow the
[Connecting to a Warehouse docs](https://docs.databend.com/using-databend-cloud/warehouses/connecting-a-warehouse)
to get the user, password, host etc.

Or you can create such a user by running:

```
GRANT CREATE ON * TO airbyte_user;
```

Make sure the Databend user with the following permissions:

- can create tables and write rows.
- can create databases e.g:

You can also use a pre-existing user but we highly recommend creating a dedicated user for Airbyte.

#### Target Database

You will need to choose an existing database or create a new database that will be used to store
synced data from Airbyte.

### Setup the Databend Destination in Airbyte

You should now have all the requirements needed to configure Databend as a destination in the UI.
You'll need the following information to configure the Databend destination:

- **Host**
- **Port**
- **Username**
- **Password**
- **Database**

## Compatibility

If your databend version >= v0.9.0 or later, you need to use databend-sqlalchemy version >= v0.1.0.
And the [Databend Cloud](https://app.databend.com/) will only support databend version > 0.9.0.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version                                                  | Date                                     | Pull Request                                              | Subject                                                  |
| :------------------------------------------------------- | :--------------------------------------- | :-------------------------------------------------------- | :------------------------------------------------------- | ----------- |
| 0.1.37 | 2025-02-01 | [52895](https://github.com/airbytehq/airbyte/pull/52895) | Update dependencies |
| 0.1.36 | 2025-01-25 | [52215](https://github.com/airbytehq/airbyte/pull/52215) | Update dependencies |
| 0.1.35 | 2025-01-18 | [51721](https://github.com/airbytehq/airbyte/pull/51721) | Update dependencies |
| 0.1.34 | 2025-01-11 | [51280](https://github.com/airbytehq/airbyte/pull/51280) | Update dependencies |
| 0.1.33 | 2024-12-28 | [50472](https://github.com/airbytehq/airbyte/pull/50472) | Update dependencies |
| 0.1.32 | 2024-12-21 | [50201](https://github.com/airbytehq/airbyte/pull/50201) | Update dependencies |
| 0.1.31 | 2024-12-14 | [48916](https://github.com/airbytehq/airbyte/pull/48916) | Update dependencies |
| 0.1.30 | 2024-11-25 | [48664](https://github.com/airbytehq/airbyte/pull/48664) | Update dependencies |
| 0.1.29 | 2024-10-19 | [46992](https://github.com/airbytehq/airbyte/pull/46992) | add ssl param for databend destination |
| 0.1.28 | 2024-11-04 | [48272](https://github.com/airbytehq/airbyte/pull/48272) | Update dependencies |
| 0.1.27 | 2024-10-28 | [47069](https://github.com/airbytehq/airbyte/pull/47069) | Update dependencies |
| 0.1.26 | 2024-10-12 | [46811](https://github.com/airbytehq/airbyte/pull/46811) | Update dependencies |
| 0.1.25 | 2024-10-05 | [46418](https://github.com/airbytehq/airbyte/pull/46418) | Update dependencies |
| 0.1.24 | 2024-09-28 | [46197](https://github.com/airbytehq/airbyte/pull/46197) | Update dependencies |
| 0.1.23 | 2024-09-21 | [45824](https://github.com/airbytehq/airbyte/pull/45824) | Update dependencies |
| 0.1.22 | 2024-09-14 | [45531](https://github.com/airbytehq/airbyte/pull/45531) | Update dependencies |
| 0.1.21 | 2024-09-07 | [45237](https://github.com/airbytehq/airbyte/pull/45237) | Update dependencies |
| 0.1.20 | 2024-08-31 | [45001](https://github.com/airbytehq/airbyte/pull/45001) | Update dependencies |
| 0.1.19 | 2024-08-24 | [44756](https://github.com/airbytehq/airbyte/pull/44756) | Update dependencies |
| 0.1.18 | 2024-08-22 | [44530](https://github.com/airbytehq/airbyte/pull/44530) | Update test dependencies |
| 0.1.17 | 2024-08-17 | [44300](https://github.com/airbytehq/airbyte/pull/44300) | Update dependencies |
| 0.1.16 | 2024-08-10 | [43611](https://github.com/airbytehq/airbyte/pull/43611) | Update dependencies |
| 0.1.15 | 2024-08-03 | [43234](https://github.com/airbytehq/airbyte/pull/43234) | Update dependencies |
| 0.1.14 | 2024-07-27 | [42588](https://github.com/airbytehq/airbyte/pull/42588) | Update dependencies |
| 0.1.13 | 2024-07-20 | [42164](https://github.com/airbytehq/airbyte/pull/42164) | Update dependencies |
| 0.1.12 | 2024-07-13 | [41800](https://github.com/airbytehq/airbyte/pull/41800) | Update dependencies |
| 0.1.11 | 2024-07-10 | [41429](https://github.com/airbytehq/airbyte/pull/41429) | Update dependencies |
| 0.1.10 | 2024-07-09 | [41243](https://github.com/airbytehq/airbyte/pull/41243) | Update dependencies |
| 0.1.9 | 2024-07-06 | [40916](https://github.com/airbytehq/airbyte/pull/40916) | Update dependencies |
| 0.1.8 | 2024-06-27 | [40215](https://github.com/airbytehq/airbyte/pull/40215) | Replaced deprecated AirbyteLogger with logging.Logger |
| 0.1.7 | 2024-06-25 | [40301](https://github.com/airbytehq/airbyte/pull/40301) | Update dependencies |
| 0.1.6 | 2024-06-21 | [39936](https://github.com/airbytehq/airbyte/pull/39936) | Update dependencies |
| 0.1.5 | 2024-06-04 | [39090](https://github.com/airbytehq/airbyte/pull/39090) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.4 | 2024-05-21 | [38510](https://github.com/airbytehq/airbyte/pull/38510) | [autopull] base image + poetry + up_to_date |
| 0.1.3                                                    | 2024-03-05                               | [#35838](https://github.com/airbytehq/airbyte/pull/35838) | Un-archive connector                                     |
| 0.1.2                                                    | 2023-02-11                               | [22855](https://github.com/airbytehq/airbyte/pull/22855)  | Fix compatibility                                        |
| issue with databend-query 0.9                            |                                          | 0.1.1                                                     | 2022-01-09                                               |
| [21182](https://github.com/airbytehq/airbyte/pull/21182) | Remove protocol option and enforce HTTPS |
|                                                          | 0.1.0                                    | 2022-01-09                                                | [20909](https://github.com/airbytehq/airbyte/pull/20909) | Destination |
| Databend                                                 |

</details>
