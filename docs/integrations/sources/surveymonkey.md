import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";

# SurveyMonkey

This guide contains instructions for setting up an Airbyte Cloud or Open Source connector for SurveyMonkey.

:::note

OAuth for Survey Monkey is supported only for the US. Airbyte is testing how to enable it in the EU. If you run into issues, [reach out to support](mailto:product@airbyte.io).

:::

## Prerequisites

<Tabs groupId="platform">
<TabItem value="cloud" label="Airbyte Cloud" default>

<!-- env:cloud -->

You have an [Airbyte Cloud](https://docs.airbyte.com/using-airbyte/getting-started/#sign-up-for-airbyte-clouds) account.


<!-- /env:cloud -->

</TabItem>

<TabItem value="oss" label="Airbyte Open Source">

<!-- env:oss -->

You have installed [Airbyte](https://docs.airbyte.com/deploying-airbyte/quickstart).

<!-- /env:oss -->

</TabItem>
</Tabs>

## Setup guide

### Step 1: Set up SurveyMonkey {#surveymonkey-access-token}

Read SurveyMonkey's [Getting started](https://developer.surveymonkey.com/api/v3/#getting-started). Register your app [at SurveyMonkey](https://developer.surveymonkey.com/apps/). For Airbyte Open Source, click **Settings** to find the access token you need to set up the connector.

### Step 2: Set up the source connector in Airbyte

<Tabs groupId="platform">
<TabItem value="cloud" label="Airbyte Cloud" default>

<!-- env:cloud -->

1. Log into your [Airbyte Cloud account](https://cloud.airbyte.com/workspaces).
1. Click **+ New workspace** to create a new workspace. In the `Workspace name` field, enter a name, then click **Save changes**.
1. In the left navigation bar, click **Sources**. Click **SurveyMonkey**, which takes you to the `Create a source` page.
1. Click **Authenticate your account**.
1. Log in to the SurveyMonkey account to authorize your app.
1. In the `Start Date` field, set the required start date.
1. Click **Set up source**.

</TabItem>

<!-- /env:cloud -->

<TabItem value="oss" label="Airbyte Open Source">

<!-- env:oss -->

1. Go to your [local Airbyte](http://localhost:8000/) page.
1. In the left navigation bar, click **Sources**. Click **SurveyMonkey**, which takes you to the `Create a source` page.
1. In the `Access Token` field, enter your SurveyMonkey access token from [Step 1](#surveymonkey-access-token).
1. In the `Start Date` field, set the required start date.
1. Click **Set up source**.

<!-- /env:oss -->

</TabItem>
</Tabs>

## Supported streams and sync modes

Airbyte supports the following SurveyMonkey streams and sync modes. `Incremental` denotes partial support:

- [Surveys](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys) \(Incremental\)
- [SurveyPages](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys-survey_id-pages)
- [SurveyQuestions](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys-survey_id-pages-page_id-questions)
- [SurveyResponses](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys-survey_id-responses-bulk) \(Incremental\)
- [SurveyCollectors](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys-survey_id-collectors)
- [Collectors](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-collectors-collector_id-)

### Performance considerations

The SurveyMonkey API applies API quotas for private apps. The following are the default limits:

- 125 requests per minute
- 500 requests per day

To cover more data from this source, Airbyte uses caching.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                          |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------- |
| 0.3.5   | 2024-06-07 | [39329](https://github.com/airbytehq/airbyte/pull/39329) | Add `CheckpointMixin` for state management                                       |
| 0.3.4   | 2024-06-06 | [39244](https://github.com/airbytehq/airbyte/pull/39244) | [autopull] Upgrade base image to v1.2.2                                          |
| 0.3.3   | 2024-05-22 | [38559](https://github.com/airbytehq/airbyte/pull/38559) | Migrate Python stream authenticator to `requests_native_auth` package            |
| 0.3.2   | 2024-05-20 | [38244](https://github.com/airbytehq/airbyte/pull/38244) | Replace AirbyteLogger with logging.Logger and upgrade base image                 |
| 0.3.1   | 2024-04-24 | [36664](https://github.com/airbytehq/airbyte/pull/36664) | Schema descriptions and CDK 0.80.0                                               |
| 0.3.0   | 2024-02-22 | [35561](https://github.com/airbytehq/airbyte/pull/35561) | Migrate connector to low-code                                                    |
| 0.2.4   | 2024-02-12 | [35168](https://github.com/airbytehq/airbyte/pull/35168) | Manage dependencies with Poetry                                                  |
| 0.2.3   | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove Dockerfile and use the python-connector-base image  |
| 0.2.2   | 2023-05-12 | [26024](https://github.com/airbytehq/airbyte/pull/26024) | Fix dependencies conflict                                                        |
| 0.2.1   | 2023-04-27 | [25109](https://github.com/airbytehq/airbyte/pull/25109) | Fix add missing params to stream `SurveyResponses`                               |
| 0.2.0   | 2023-04-18 | [23721](https://github.com/airbytehq/airbyte/pull/23721) | Add `SurveyCollectors` and `Collectors` stream                                   |
| 0.1.16  | 2023-04-13 | [25080](https://github.com/airbytehq/airbyte/pull/25080) | Fix spec.json required fields and update schema for surveys and survey_responses |
| 0.1.15  | 2023-02-11 | [22865](https://github.com/airbytehq/airbyte/pull/22865) | Specified date formatting in specification                                       |
| 0.1.14  | 2023-01-27 | [22024](https://github.com/airbytehq/airbyte/pull/22024) | Set `AvailabilityStrategy` for streams explicitly to `None`                      |
| 0.1.13  | 2022-11-29 | [19868](https://github.com/airbytehq/airbyte/pull/19868) | Fix OAuth flow urls                                                              |
| 0.1.12  | 2022-10-13 | [17964](https://github.com/airbytehq/airbyte/pull/17964) | Add OAuth for Eu and Ca                                                          |
| 0.1.11  | 2022-09-28 | [17326](https://github.com/airbytehq/airbyte/pull/17326) | Migrate to per-stream states                                                     |
| 0.1.10  | 2022-09-14 | [16706](https://github.com/airbytehq/airbyte/pull/16706) | Fix 404 error when handling nonexistent surveys                                  |
| 0.1.9   | 2022-07-28 | [13046](https://github.com/airbytehq/airbyte/pull/14998) | Fix state for response stream, fixed backoff behaviour, added unittest           |
| 0.1.8   | 2022-05-20 | [13046](https://github.com/airbytehq/airbyte/pull/13046) | Fix incremental streams                                                          |
| 0.1.7   | 2022-02-24 | [8768](https://github.com/airbytehq/airbyte/pull/8768)   | Add custom survey IDs to limit API calls                                         |
| 0.1.6   | 2022-01-14 | [9508](https://github.com/airbytehq/airbyte/pull/9508)   | Scopes change                                                                    |
| 0.1.5   | 2021-12-28 | [8628](https://github.com/airbytehq/airbyte/pull/8628)   | Update fields in source-connectors specifications                                |
| 0.1.4   | 2021-11-11 | [7868](https://github.com/airbytehq/airbyte/pull/7868)   | Improve 'check' using '/users/me' API call                                       |
| 0.1.3   | 2021-11-01 | [7433](https://github.com/airbytehq/airbyte/pull/7433)   | Remove unsused oAuth flow parameters                                             |
| 0.1.2   | 2021-10-27 | [7433](https://github.com/airbytehq/airbyte/pull/7433)   | Add OAuth support                                                                |
| 0.1.1   | 2021-09-10 | [5983](https://github.com/airbytehq/airbyte/pull/5983)   | Fix caching for gzip compressed http response                                    |
| 0.1.0   | 2021-07-06 | [4097](https://github.com/airbytehq/airbyte/pull/4097)   | Initial Release                                                                  |

</details>
