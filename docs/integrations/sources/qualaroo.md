# Qualaroo

## Overview

The Qualaroo source supports Full Refresh syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

Several output streams are available from this source:

* [Surveys](https://help.qualaroo.com/hc/en-us/articles/201969438-The-REST-Reporting-API) \(Full table\)
  * [Responses](https://help.qualaroo.com/hc/en-us/articles/201969438-The-REST-Reporting-API) \(Full table\)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | NO |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

The connector is **not** yet restricted by normal requests limitation. As a result, the Qualaroo connector might run into API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Qualaroo API Key
* Qualaroo API Token

### Setup guide
<!-- markdown-link-check-disable-next-line -->
Please read [How to get your APIs Token and Key](https://help.qualaroo.com/hc/en-us/articles/201969438-The-REST-Reporting-API) or you can log in to Qualaroo and visit [Reporting API](https://app.qualaroo.com/account).

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                  |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------------------------------------------------------------------------------------|
| 0.2.0   | 2023-05-24 | [26491](https://github.com/airbytehq/airbyte/pull/26491) | Remove authSpecification from spec.json as OAuth is not supported by Qualaroo + update stream schema     |
| 0.1.2   | 2022-05-24 | [13121](https://github.com/airbytehq/airbyte/pull/13121) | Fix `start_date` and `survey_ids` schema formatting. Separate source and stream files. Add stream_slices |
| 0.1.1   | 2022-05-20 | [13042](https://github.com/airbytehq/airbyte/pull/13042) | Update stream specs                                                                                      |
| 0.1.0   | 2021-08-18 | [8623](https://github.com/airbytehq/airbyte/pull/8623)   | New source: Qualaroo                                                                                     |

