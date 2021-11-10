# Mixpanel

## Overview

The Mixpanel source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This Source Connector is based on a [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

### Output schema

Several output streams are available from this source:

* [Export](https://developer.mixpanel.com/docs/exporting-raw-data#section-export-api-reference) \(Incremental\)
* [Engage](https://developer.mixpanel.com/docs/data-export-api#section-engage) \(Full table\)
* [Funnels](https://developer.mixpanel.com/docs/data-export-api#section-funnels) \(Incremental\)
* [Revenue](https://developer.mixpanel.com/docs/data-export-api#section-hr-span-style-font-family-courier-revenue-span) \(Incremental\)
* [Annotations](https://developer.mixpanel.com/docs/data-export-api#section-annotations) \(Full table\)
* [Cohorts](https://developer.mixpanel.com/docs/cohorts#section-list-cohorts) \(Full table\)
* [Cohort Members](https://developer.mixpanel.com/docs/data-export-api#section-engage) \(Full table\)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Replicate Incremental Deletes | Coming soon |
| SSL connection | Yes |
| Namespaces | No |

Please note, that incremental sync could return duplicated \(old records\) for the state date due to API filter limitation, which is granular to the whole day only.

### Performance considerations

The Mixpanel connector should not run into Mixpanel API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

* Export stream - 60 reqs per hour
* All streams - 400 reqs per hour

## Getting started

### Requirements

* Mixpanel API Secret
* Project region `US` or `EU`

### Setup guide
<!-- markdown-link-check-disable-next-line -->
Please read [Find API Secret](https://help.mixpanel.com/hc/en-us/articles/115004502806-Find-Project-Token-).

<!-- markdown-link-check-disable-next-line -->
Select the correct region \(EU or US\) for your Mixpanel project. See detail [here](https://help.mixpanel.com/hc/en-us/articles/360039135652-Data-Residency-in-EU)

*Note:* If `start_date` is not set, the connector will replicate data from up to one year ago by default.

## CHANGELOG

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| `0.1.5` | 2021-11-10 | [7451](https://github.com/airbytehq/airbyte/issues/7451) | Support `start_date` older than 1 year |
| `0.1.4` | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499)   | Remove base-python dependencies |
| `0.1.3` | 2021-10-30 | [7505](https://github.com/airbytehq/airbyte/issues/7505) | Guarantee that standard and custom mixpanel properties in the `Engage` stream are written as strings |
| `0.1.2` | 2021-11-02 | [7439](https://github.com/airbytehq/airbyte/issues/7439) | Added delay for all streams to match API limitation of requests rate |
| `0.1.1` | 2021-09-16 | [6075](https://github.com/airbytehq/airbyte/issues/6075) | Added option to select project region |
| `0.1.0` | 2021-07-06 | [3698](https://github.com/airbytehq/airbyte/issues/3698) | created CDK native mixpanel connector |

