# Guru

This page contains the setup guide and reference information for the [Guru](https://app.getguru.com/) source connector. 

## Prerequisites

To set up the Guru source connector, you'll need the [Guru Auth keys](https://developer.getguru.com/reference/authentication) with permissions to the resources Airbyte should be able to access.

## Set up the Greenhouse connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account or navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Guru** from the Source type dropdown.
4. Enter the name for the Greenhouse connector.
5. Enter your [**Guru API Key**](https://developer.getguru.com/reference/authentication) that you obtained from Greenhouse.
6. The `USERNAME` is your `email` and `PASSWORD` is `your api_key`
6. Click **Set up source**.


## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |
| `start_date` | `string` | Start date.  |  |
| `team_id` | `string` | team_id. Team ID received through response of /teams streams, make sure about access to the team |  |
| `search_cards_query` | `string` | search_cards_query. Query for searching cards |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| teams | id | DefaultPaginator | ✅ |  ✅  |
| groups | id | DefaultPaginator | ✅ |  ✅  |
| group_collection_access |  | DefaultPaginator | ✅ |  ✅  |
| group_members |  | DefaultPaginator | ✅ |  ✅  |
| members | id | DefaultPaginator | ✅ |  ✅  |
| team_analytics |  | DefaultPaginator | ✅ |  ❌  |
| collections | id | DefaultPaginator | ✅ |  ✅  |
| folders | id | DefaultPaginator | ✅ |  ❌  |
| folder_items | id | DefaultPaginator | ✅ |  ❌  |
| folders_parent |  | DefaultPaginator | ✅ |  ❌  |
| search_cardmgr | id | DefaultPaginator | ✅ |  ✅  |
| tag_categories |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.45 | 2025-12-09 | [70504](https://github.com/airbytehq/airbyte/pull/70504) | Update dependencies |
| 0.0.44 | 2025-11-25 | [70022](https://github.com/airbytehq/airbyte/pull/70022) | Update dependencies |
| 0.0.43 | 2025-11-18 | [69423](https://github.com/airbytehq/airbyte/pull/69423) | Update dependencies |
| 0.0.42 | 2025-10-29 | [68768](https://github.com/airbytehq/airbyte/pull/68768) | Update dependencies |
| 0.0.41 | 2025-10-21 | [68212](https://github.com/airbytehq/airbyte/pull/68212) | Update dependencies |
| 0.0.40 | 2025-10-14 | [67902](https://github.com/airbytehq/airbyte/pull/67902) | Update dependencies |
| 0.0.39 | 2025-10-07 | [67398](https://github.com/airbytehq/airbyte/pull/67398) | Update dependencies |
| 0.0.38 | 2025-09-30 | [66398](https://github.com/airbytehq/airbyte/pull/66398) | Update dependencies |
| 0.0.37 | 2025-09-09 | [66081](https://github.com/airbytehq/airbyte/pull/66081) | Update dependencies |
| 0.0.36 | 2025-08-23 | [65328](https://github.com/airbytehq/airbyte/pull/65328) | Update dependencies |
| 0.0.35 | 2025-08-09 | [64587](https://github.com/airbytehq/airbyte/pull/64587) | Update dependencies |
| 0.0.34 | 2025-08-02 | [64232](https://github.com/airbytehq/airbyte/pull/64232) | Update dependencies |
| 0.0.33 | 2025-07-26 | [63905](https://github.com/airbytehq/airbyte/pull/63905) | Update dependencies |
| 0.0.32 | 2025-07-19 | [63490](https://github.com/airbytehq/airbyte/pull/63490) | Update dependencies |
| 0.0.31 | 2025-07-12 | [63098](https://github.com/airbytehq/airbyte/pull/63098) | Update dependencies |
| 0.0.30 | 2025-07-05 | [62628](https://github.com/airbytehq/airbyte/pull/62628) | Update dependencies |
| 0.0.29 | 2025-06-28 | [62159](https://github.com/airbytehq/airbyte/pull/62159) | Update dependencies |
| 0.0.28 | 2025-06-21 | [61831](https://github.com/airbytehq/airbyte/pull/61831) | Update dependencies |
| 0.0.27 | 2025-06-14 | [61110](https://github.com/airbytehq/airbyte/pull/61110) | Update dependencies |
| 0.0.26 | 2025-05-24 | [60666](https://github.com/airbytehq/airbyte/pull/60666) | Update dependencies |
| 0.0.25 | 2025-05-10 | [59820](https://github.com/airbytehq/airbyte/pull/59820) | Update dependencies |
| 0.0.24 | 2025-05-03 | [59284](https://github.com/airbytehq/airbyte/pull/59284) | Update dependencies |
| 0.0.23 | 2025-04-26 | [58828](https://github.com/airbytehq/airbyte/pull/58828) | Update dependencies |
| 0.0.22 | 2025-04-19 | [58199](https://github.com/airbytehq/airbyte/pull/58199) | Update dependencies |
| 0.0.21 | 2025-04-12 | [57068](https://github.com/airbytehq/airbyte/pull/57068) | Update dependencies |
| 0.0.20 | 2025-03-29 | [56638](https://github.com/airbytehq/airbyte/pull/56638) | Update dependencies |
| 0.0.19 | 2025-03-22 | [56072](https://github.com/airbytehq/airbyte/pull/56072) | Update dependencies |
| 0.0.18 | 2025-03-08 | [55492](https://github.com/airbytehq/airbyte/pull/55492) | Update dependencies |
| 0.0.17 | 2025-03-01 | [54792](https://github.com/airbytehq/airbyte/pull/54792) | Update dependencies |
| 0.0.16 | 2025-02-22 | [54299](https://github.com/airbytehq/airbyte/pull/54299) | Update dependencies |
| 0.0.15 | 2025-02-15 | [53856](https://github.com/airbytehq/airbyte/pull/53856) | Update dependencies |
| 0.0.14 | 2025-02-08 | [53305](https://github.com/airbytehq/airbyte/pull/53305) | Update dependencies |
| 0.0.13 | 2025-02-01 | [52731](https://github.com/airbytehq/airbyte/pull/52731) | Update dependencies |
| 0.0.12 | 2025-01-25 | [52283](https://github.com/airbytehq/airbyte/pull/52283) | Update dependencies |
| 0.0.11 | 2025-01-18 | [51835](https://github.com/airbytehq/airbyte/pull/51835) | Update dependencies |
| 0.0.10 | 2025-01-11 | [51188](https://github.com/airbytehq/airbyte/pull/51188) | Update dependencies |
| 0.0.9 | 2024-12-28 | [50622](https://github.com/airbytehq/airbyte/pull/50622) | Update dependencies |
| 0.0.8 | 2024-12-21 | [50118](https://github.com/airbytehq/airbyte/pull/50118) | Update dependencies |
| 0.0.7 | 2024-12-14 | [49622](https://github.com/airbytehq/airbyte/pull/49622) | Update dependencies |
| 0.0.6 | 2024-12-12 | [49271](https://github.com/airbytehq/airbyte/pull/49271) | Update dependencies |
| 0.0.5 | 2024-12-11 | [48903](https://github.com/airbytehq/airbyte/pull/48903) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.4 | 2024-11-04 | [48152](https://github.com/airbytehq/airbyte/pull/48152) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47830](https://github.com/airbytehq/airbyte/pull/47830) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47665](https://github.com/airbytehq/airbyte/pull/47665) | Update dependencies |
| 0.0.1 | 2024-08-31 | [45066](https://github.com/airbytehq/airbyte/pull/45066) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
