# Mixpanel

This page contains the setup guide and reference information for the Mixpanel source connector.

## Prerequisites

* Mixpanel API Secret
* Project region `US` or `EU`

## Setup guide

### Step 1: Set up

<!-- markdown-link-check-disable-next-line -->
Please read [Find Project Secret](https://developer.mixpanel.com/reference/project-secret#managing-a-projects-secret), and get your Project Secret.

<!-- markdown-link-check-disable-next-line -->
Select the correct region \(EU or US\) for your Mixpanel project. See detail [here](https://help.mixpanel.com/hc/en-us/articles/360039135652-Data-Residency-in-EU)


### Step 2: Set up the Mixpanel connector in Airbyte
Choose start date, from which data will be synced

*Note:* If `start_date` is not set, the connector will replicate data from up to one year ago by default.


### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Mixpanel connector and select **Mixpanel** from the Source type dropdown.
4. Select `start_date`, from which your data will need to be synced


## Supported sync modes
The Mixpanel source connector supports the following[ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh](https://docs.airbyte.com/integrations/sources/mongodb#full-refresh-sync)
* [Incremental](https://docs.airbyte.com/integrations/sources/mongodb#incremental-sync)

Please note, that incremental sync could return duplicated \(old records\) for the state date due to API filter limitation, which is granular to the whole day only.

### Supported Streams

* [Export](https://developer.mixpanel.com/reference/raw-event-export) \(Incremental\)
* [Engage](https://developer.mixpanel.com/reference/engage-query) \(Full table\)
* [Funnels](https://developer.mixpanel.com/reference/funnels-query) \(Incremental\)
* [Revenue](https://developer.mixpanel.com/reference/engage-query) \(Incremental\)
* [Annotations](https://developer.mixpanel.com/reference/overview-1) \(Full table\)
* [Cohorts](https://developer.mixpanel.com/reference/cohorts-list) \(Full table\)
* [Cohort Members](https://developer.mixpanel.com/reference/engage-query) \(Full table\)


## Performance considerations

* Due to quite low API rate-limits \(**60 reqs per hour**\), syncing of huge date windows may be quite long
* If you're struggling with high RAM usage, try to decrease `date_window_size` parameter in config


## CHANGELOG

| Version | Date       | Pull Request                                             | Subject                                                                                              |
|:--------|:-----------|:---------------------------------------------------------|:-----------------------------------------------------------------------------------------------------|
| 0.1.20  | 2022-08-22 | [15091](https://github.com/airbytehq/airbyte/pull/15091) | Improve `export` stream cursor support                                                               |
| 0.1.19  | 2022-08-18 | [15739](https://github.com/airbytehq/airbyte/pull/15739) | Update `titile` and `description` for `Project Secret` field                                         |
| 0.1.18  | 2022-07-21 | [14924](https://github.com/airbytehq/airbyte/pull/14924) | Remove `additionalProperties` field from schemas and specs                                           |
| 0.1.17  | 2022-06-01 | [12801](https://github.com/airbytehq/airbyte/pull/13372) | Acceptance tests fix, fixing some bugs for beta release                                              |
| 0.1.16  | 2022-05-30 | [12801](https://github.com/airbytehq/airbyte/pull/12801) | Add end_date parameter                                                                               |
| 0.1.15  | 2022-05-04 | [12482](https://github.com/airbytehq/airbyte/pull/12482) | Update input configuration copy                                                                      |
| 0.1.14  | 2022-05-02 | [11501](https://github.com/airbytehq/airbyte/pull/11501) | Improve incremental sync method to streams                                                           |  
| 0.1.13  | 2022-04-27 | [12335](https://github.com/airbytehq/airbyte/pull/12335) | Adding fixtures to mock time.sleep for connectors that explicitly sleep                              |  
| 0.1.12  | 2022-03-31 | [11633](https://github.com/airbytehq/airbyte/pull/11633) | Increase unit test coverage                                                                          |  
| 0.1.11  | 2022-04-04 | [11318](https://github.com/airbytehq/airbyte/pull/11318) | Change Response Reading                                                                              |
| 0.1.10  | 2022-03-31 | [11227](https://github.com/airbytehq/airbyte/pull/11227) | Fix cohort id always null in the cohort_members stream                                               |
| 0.1.9   | 2021-12-07 | [8429](https://github.com/airbytehq/airbyte/pull/8578)   | Updated titles and descriptions                                                                      |
| 0.1.7   | 2021-12-01 | [8381](https://github.com/airbytehq/airbyte/pull/8381)   | Increased performance for `discovery` stage during connector setup                                   |
| 0.1.6   | 2021-11-25 | [8256](https://github.com/airbytehq/airbyte/issues/8256) | Deleted `date_window_size` and fix schemas date type issue                                           |
| 0.1.5   | 2021-11-10 | [7451](https://github.com/airbytehq/airbyte/issues/7451) | Support `start_date` older than 1 year                                                               |
| 0.1.4   | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499)   | Remove base-python dependencies                                                                      |
| 0.1.3   | 2021-10-30 | [7505](https://github.com/airbytehq/airbyte/issues/7505) | Guarantee that standard and custom mixpanel properties in the `Engage` stream are written as strings |
| 0.1.2   | 2021-11-02 | [7439](https://github.com/airbytehq/airbyte/issues/7439) | Added delay for all streams to match API limitation of requests rate                                 |
| 0.1.1   | 2021-09-16 | [6075](https://github.com/airbytehq/airbyte/issues/6075) | Added option to select project region                                                                |
| 0.1.0   | 2021-07-06 | [3698](https://github.com/airbytehq/airbyte/issues/3698) | Created CDK native mixpanel connector                                                                |


