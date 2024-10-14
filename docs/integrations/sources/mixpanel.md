# Mixpanel

This page contains the setup guide and reference information for the Mixpanel source connector.

## Prerequisites

To set up the Mixpanel source connector, you'll need a Mixpanel [Service Account](https://developer.mixpanel.com/reference/service-accounts) and it's [Project ID](https://help.mixpanel.com/hc/en-us/articles/115004490503-Project-Settings#project-id), the [Project Timezone](https://help.mixpanel.com/hc/en-us/articles/115004547203-Manage-Timezones-for-Projects-in-Mixpanel), and the Project region (`US` or `EU`).

## Set up the Mixpanel connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) or navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Mixpanel** from the Source type dropdown.
4. Enter the name for the Mixpanel connector.
5. For **Authentication**, select **Service Account** from the dropdown and enter the [Mixpanel Service Account secret](https://developer.mixpanel.com/reference/service-accounts).
6. For **Project ID**, enter the [Mixpanel Project ID](https://help.mixpanel.com/hc/en-us/articles/115004490503-Project-Settings#project-id).
7. For **Attribution Window**, enter the number of days for the length of the attribution window.
8. For **Project Timezone**, enter the [timezone](https://help.mixpanel.com/hc/en-us/articles/115004547203-Manage-Timezones-for-Projects-in-Mixpanel) for your Mixpanel project.
9. For **Start Date**, enter the date in YYYY-MM-DD format. The data added on and after this date will be replicated. If left blank, the connector will replicate data from up to one year ago by default.
10. For **End Date**, enter the date in YYYY-MM-DD format.
11. For **Region**, enter the [region](https://help.mixpanel.com/hc/en-us/articles/360039135652-Data-Residency-in-EU) for your Mixpanel project.
12. For **Date slicing window**, enter the number of days to slice through data. If you encounter RAM usage issues due to a huge amount of data in each window, try using a lower value for this parameter.
13. Click **Set up source**.

## Supported sync modes

The Mixpanel source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

Note: Incremental sync returns duplicated \(old records\) for the state date due to API filter limitation, which is granular to the whole day only.

### Supported Streams

- [Export](https://developer.mixpanel.com/reference/raw-event-export) \(Incremental\)
- [Engage](https://developer.mixpanel.com/reference/engage-query) \(Incremental\)
- [Funnels](https://developer.mixpanel.com/reference/funnels-query) \(Incremental\)
- [Revenue](https://developer.mixpanel.com/reference/engage-query) \(Incremental\)
- [Annotations](https://developer.mixpanel.com/reference/overview-1) \(Full table\)
- [Cohorts](https://developer.mixpanel.com/reference/cohorts-list) \(Incremental\)
- [Cohort Members](https://developer.mixpanel.com/reference/engage-query) \(Incremental\)

### Primary key selection for Export stream

Mixpanel recommends using `[insert_id, event_time, event_name, distinct_id]` as the primary key. However, note that some rows might lack an `insert_id` for certain users. Ensure you select a primary key that aligns with your data.

## Performance considerations

Syncing huge date windows may take longer due to Mixpanel's low API rate-limits \(**60 reqs per hour**\).

## CHANGELOG

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                                                                                                                                                                                                                                                                                            |
|:--------|:-----------|:---------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 3.4.8 | 2024-10-12 | [46792](https://github.com/airbytehq/airbyte/pull/46792) | Update dependencies |
| 3.4.7 | 2024-10-05 | [46428](https://github.com/airbytehq/airbyte/pull/46428) | Update dependencies |
| 3.4.6 | 2024-09-28 | [45747](https://github.com/airbytehq/airbyte/pull/45747) | Update dependencies |
| 3.4.5 | 2024-09-14 | [45473](https://github.com/airbytehq/airbyte/pull/45473) | Update dependencies |
| 3.4.4 | 2024-09-07 | [45264](https://github.com/airbytehq/airbyte/pull/45264) | Update dependencies |
| 3.4.3 | 2024-08-31 | [45059](https://github.com/airbytehq/airbyte/pull/45059) | Update dependencies |
| 3.4.2 | 2024-08-24 | [44643](https://github.com/airbytehq/airbyte/pull/44643) | Update dependencies |
| 3.4.1 | 2024-08-17 | [44274](https://github.com/airbytehq/airbyte/pull/44274) | Update dependencies |
| 3.4.0 | 2024-07-16 | [41969](https://github.com/airbytehq/airbyte/pull/41969) | Update to v4 CDK |
| 3.3.3 | 2024-08-10 | [43575](https://github.com/airbytehq/airbyte/pull/43575) | Update dependencies |
| 3.3.2 | 2024-08-03 | [43182](https://github.com/airbytehq/airbyte/pull/43182) | Update dependencies |
| 3.3.1 | 2024-07-27 | [42391](https://github.com/airbytehq/airbyte/pull/42391) | Update dependencies |
| 3.3.0 | 2024-07-15 | [41754](https://github.com/airbytehq/airbyte/pull/41754) | Add engage page size to configuration |
| 3.2.4 | 2024-07-13 | [41754](https://github.com/airbytehq/airbyte/pull/41754) | Update dependencies |
| 3.2.3 | 2024-07-10 | [41420](https://github.com/airbytehq/airbyte/pull/41420) | Update dependencies |
| 3.2.2 | 2024-07-09 | [41289](https://github.com/airbytehq/airbyte/pull/41289) | Update dependencies |
| 3.2.1 | 2024-07-06 | [40806](https://github.com/airbytehq/airbyte/pull/40806) | Update dependencies |
| 3.2.0 | 2024-06-26 | [40607](https://github.com/airbytehq/airbyte/pull/40607) | Make engage stream really incremental |
| 3.1.5 | 2024-06-26 | [40549](https://github.com/airbytehq/airbyte/pull/40549) | Migrate off deprecated auth package |
| 3.1.4 | 2024-06-25 | [40376](https://github.com/airbytehq/airbyte/pull/40376) | Update dependencies |
| 3.1.3 | 2024-06-22 | [40138](https://github.com/airbytehq/airbyte/pull/40138) | Update dependencies |
| 3.1.2 | 2024-06-18 | [38710](https://github.com/airbytehq/airbyte/pull/38710) | Update authenticator CDK package |
| 3.1.1 | 2024-06-04 | [39006](https://github.com/airbytehq/airbyte/pull/39006) | [autopull] Upgrade base image to v1.2.1 |
| 3.1.0 | 2024-05-30 | [38757](https://github.com/airbytehq/airbyte/pull/38757) | change format for `start_date` and `end_date` from `date` to `date-time` |
| 3.0.0 | 2024-05-22 | [38066](https://github.com/airbytehq/airbyte/pull/38066) | Changed key to distinct_id, cohort_id and changed state to per-patition format for `CohortMembers` stream; fixed pagination for `Engage` stream; fixed incorrect client-side filtering for semi-incremental streams when data comes not in chronological order; semi-incremental `Cohorts`, `CohortMembers` and `Engage` streams with client-side filtering extract records since user provided or default (1 year old) start_date |
| 2.3.1 | 2024-05-20 | [38267](https://github.com/airbytehq/airbyte/pull/38267) | Replace AirbyteLogger with logging.Logger |
| 2.3.0 | 2024-04-12 | [36724](https://github.com/airbytehq/airbyte/pull/36724) | Connector migrated to low-code |
| 2.2.2 | 2024-04-19 | [36651](https://github.com/airbytehq/airbyte/pull/36651) | Updating to 0.80.0 CDK |
| 2.2.1 | 2024-04-12 | [36651](https://github.com/airbytehq/airbyte/pull/36651) | Schema descriptions |
| 2.2.0 | 2024-03-19 | [36267](https://github.com/airbytehq/airbyte/pull/36267) | Pin airbyte-cdk version to `^0` |
| 2.1.0 | 2024-02-13 | [35203](https://github.com/airbytehq/airbyte/pull/35203) | Update stream Funnels schema with custom_event_id and custom_event fields |
| 2.0.2 | 2024-02-12 | [35151](https://github.com/airbytehq/airbyte/pull/35151) | Manage dependencies with Poetry |
| 2.0.1 | 2024-01-11 | [34147](https://github.com/airbytehq/airbyte/pull/34147) | prepare for airbyte-lib |
| 2.0.0 | 2023-10-30 | [31955](https://github.com/airbytehq/airbyte/pull/31955) | Delete the default primary key for the Export stream |
| 1.0.1 | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 1.0.0 | 2023-09-27 | [30025](https://github.com/airbytehq/airbyte/pull/30025) | Fix type of datetime field in engage stream; fix primary key for export stream. |
| 0.1.41 | 2023-09-26 | [30149](https://github.com/airbytehq/airbyte/pull/30149) | Change config schema; set checkpointing interval; add suggested streams; add casting datetime fields. |
| 0.1.40 | 2022-09-20 | [30090](https://github.com/airbytehq/airbyte/pull/30090) | Handle 400 error when the credentials become expired |
| 0.1.39 | 2023-09-15 | [30469](https://github.com/airbytehq/airbyte/pull/30469) | Add default primary key `distinct_id` to `Export` stream |
| 0.1.38 | 2023-08-31 | [30028](https://github.com/airbytehq/airbyte/pull/30028) | Handle gracefully project timezone mismatch |
| 0.1.37 | 2023-07-20 | [27932](https://github.com/airbytehq/airbyte/pull/27932) | Fix spec: change start/end date format to `date` |
| 0.1.36 | 2023-06-27 | [27752](https://github.com/airbytehq/airbyte/pull/27752) | Partially revert version 0.1.32; Use exponential backoff |
| 0.1.35 | 2023-06-12 | [27252](https://github.com/airbytehq/airbyte/pull/27252) | Add should_retry False for 402 error |
| 0.1.34 | 2023-05-15 | [21837](https://github.com/airbytehq/airbyte/pull/21837) | Add "insert_id" field to "export" stream schema |
| 0.1.33 | 2023-04-25 | [25543](https://github.com/airbytehq/airbyte/pull/25543) | Set should_retry for 104 error in stream export |
| 0.1.32 | 2023-04-11 | [25056](https://github.com/airbytehq/airbyte/pull/25056) | Set HttpAvailabilityStrategy, add exponential backoff, streams export and annotations add undeclared fields |
| 0.1.31 | 2023-02-13 | [22936](https://github.com/airbytehq/airbyte/pull/22936) | Specified date formatting in specification |
| 0.1.30 | 2023-01-27 | [22017](https://github.com/airbytehq/airbyte/pull/22017) | Set `AvailabilityStrategy` for streams explicitly to `None` |
| 0.1.29 | 2022-11-02 | [18846](https://github.com/airbytehq/airbyte/pull/18846) | For "export" stream make line parsing more robust |
| 0.1.28 | 2022-10-06 | [17699](https://github.com/airbytehq/airbyte/pull/17699) | Fix discover step issue cursor field None |
| 0.1.27 | 2022-09-29 | [17415](https://github.com/airbytehq/airbyte/pull/17415) | Disable stream "cohort_members" on discover if not access |
| 0.1.26 | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/pull/17304) | Migrate to per-stream states |
| 0.1.25 | 2022-09-27 | [17145](https://github.com/airbytehq/airbyte/pull/17145) | Disable streams "export", "engage" on discover if not access |
| 0.1.24 | 2022-09-26 | [16915](https://github.com/airbytehq/airbyte/pull/16915) | Added Service Accounts support |
| 0.1.23 | 2022-09-18 | [16843](https://github.com/airbytehq/airbyte/pull/16843) | Add stream=True for `export` stream |
| 0.1.22 | 2022-09-15 | [16770](https://github.com/airbytehq/airbyte/pull/16770) | Use "Retry-After" header for backoff |
| 0.1.21 | 2022-09-11 | [16191](https://github.com/airbytehq/airbyte/pull/16191) | Improved connector's input configuration validation |
| 0.1.20 | 2022-08-22 | [15091](https://github.com/airbytehq/airbyte/pull/15091) | Improve `export` stream cursor support |
| 0.1.19 | 2022-08-18 | [15739](https://github.com/airbytehq/airbyte/pull/15739) | Update `titile` and `description` for `Project Secret` field |
| 0.1.18 | 2022-07-21 | [14924](https://github.com/airbytehq/airbyte/pull/14924) | Remove `additionalProperties` field from schemas and specs |
| 0.1.17  | 2022-06-01 | [12801](https://github.com/airbytehq/airbyte/pull/13372) | Acceptance tests fix, fixing some bugs for beta release                                                                                                                                                                                                                                                                                                                                                                            |
| 0.1.16  | 2022-05-30 | [12801](https://github.com/airbytehq/airbyte/pull/12801) | Add end_date parameter                                                                                                                                                                                                                                                                                                                                                                                                             |
| 0.1.15  | 2022-05-04 | [12482](https://github.com/airbytehq/airbyte/pull/12482) | Update input configuration copy                                                                                                                                                                                                                                                                                                                                                                                                    |
| 0.1.14  | 2022-05-02 | [11501](https://github.com/airbytehq/airbyte/pull/11501) | Improve incremental sync method to streams                                                                                                                                                                                                                                                                                                                                                                                         |
| 0.1.13  | 2022-04-27 | [12335](https://github.com/airbytehq/airbyte/pull/12335) | Adding fixtures to mock time.sleep for connectors that explicitly sleep                                                                                                                                                                                                                                                                                                                                                            |
| 0.1.12  | 2022-03-31 | [11633](https://github.com/airbytehq/airbyte/pull/11633) | Increase unit test coverage                                                                                                                                                                                                                                                                                                                                                                                                        |
| 0.1.11  | 2022-04-04 | [11318](https://github.com/airbytehq/airbyte/pull/11318) | Change Response Reading                                                                                                                                                                                                                                                                                                                                                                                                            |
| 0.1.10  | 2022-03-31 | [11227](https://github.com/airbytehq/airbyte/pull/11227) | Fix cohort id always null in the cohort_members stream                                                                                                                                                                                                                                                                                                                                                                             |
| 0.1.9   | 2021-12-07 | [8429](https://github.com/airbytehq/airbyte/pull/8578)   | Updated titles and descriptions                                                                                                                                                                                                                                                                                                                                                                                                    |
| 0.1.7   | 2021-12-01 | [8381](https://github.com/airbytehq/airbyte/pull/8381)   | Increased performance for `discovery` stage during connector setup                                                                                                                                                                                                                                                                                                                                                                 |
| 0.1.6   | 2021-11-25 | [8256](https://github.com/airbytehq/airbyte/issues/8256) | Deleted `date_window_size` and fix schemas date type issue                                                                                                                                                                                                                                                                                                                                                                         |
| 0.1.5   | 2021-11-10 | [7451](https://github.com/airbytehq/airbyte/issues/7451) | Support `start_date` older than 1 year                                                                                                                                                                                                                                                                                                                                                                                             |
| 0.1.4   | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499)   | Remove base-python dependencies                                                                                                                                                                                                                                                                                                                                                                                                    |
| 0.1.3   | 2021-10-30 | [7505](https://github.com/airbytehq/airbyte/issues/7505) | Guarantee that standard and custom mixpanel properties in the `Engage` stream are written as strings                                                                                                                                                                                                                                                                                                                               |
| 0.1.2   | 2021-11-02 | [7439](https://github.com/airbytehq/airbyte/issues/7439) | Added delay for all streams to match API limitation of requests rate                                                                                                                                                                                                                                                                                                                                                               |
| 0.1.1   | 2021-09-16 | [6075](https://github.com/airbytehq/airbyte/issues/6075) | Added option to select project region                                                                                                                                                                                                                                                                                                                                                                                              |
| 0.1.0   | 2021-07-06 | [3698](https://github.com/airbytehq/airbyte/issues/3698) | Created CDK native mixpanel connector                                                                                                                                                                                                                                                                                                                                                                                              |

</details>
