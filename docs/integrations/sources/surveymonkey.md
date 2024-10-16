# SurveyMonkey

This page guides you through the process of setting up the SurveyMonkey source connector.

:::note

OAuth for Survey Monkey is officially supported only for the US. We are testing how to enable it in the EU at the moment. If you run into any issues, please [reach out to us](mailto:product@airbyte.io) so we can promptly assist you.

:::

<!-- env:oss -->

## Prerequisites

**For Airbyte Open Source:**

- Access Token
<!-- /env:oss -->

## Setup guide

### Step 1: Set up SurveyMonkey

Please read this [docs](https://developer.surveymonkey.com/api/v3/#getting-started). Register your application [here](https://developer.surveymonkey.com/apps/) Then go to Settings and copy your access token

### Step 2: Set up the source connector in Airbyte

<!-- env:cloud -->

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **SurveyMonkey** from the Source type dropdown and enter a name for this connector.
4. lick `Authenticate your account`.
5. Log in and Authorize to the SurveyMonkey account
6. Choose required Start date
7. click `Set up source`.
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Go to local Airbyte page.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **SurveyMonkey** from the Source type dropdown and enter a name for this connector.
4. Add **Access Token**
5. Choose required Start date
6. Click `Set up source`.
<!-- /env:oss -->

## Supported streams and sync modes

- [Surveys](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys) \(Incremental\)
- [SurveyPages](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys-survey_id-pages)
- [SurveyQuestions](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys-survey_id-pages-page_id-questions)
- [SurveyResponses](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys-id-responses-bulk) \(Incremental\)
- [SurveyCollectors](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys-survey_id-collectors)
- [Collectors](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-collectors-collector_id-)

### Performance considerations

The SurveyMonkey API applies heavy API quotas for default private apps, which have the following limits:

- 125 requests per minute
- 500 requests per day

To cover more data from this source we use caching.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                          |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------- |
| 0.3.26 | 2024-10-12 | [46801](https://github.com/airbytehq/airbyte/pull/46801) | Update dependencies |
| 0.3.25 | 2024-10-05 | [46448](https://github.com/airbytehq/airbyte/pull/46448) | Update dependencies |
| 0.3.24 | 2024-09-28 | [46129](https://github.com/airbytehq/airbyte/pull/46129) | Update dependencies |
| 0.3.23 | 2024-09-21 | [45770](https://github.com/airbytehq/airbyte/pull/45770) | Update dependencies |
| 0.3.22 | 2024-09-14 | [45519](https://github.com/airbytehq/airbyte/pull/45519) | Update dependencies |
| 0.3.21 | 2024-09-07 | [45316](https://github.com/airbytehq/airbyte/pull/45316) | Update dependencies |
| 0.3.20 | 2024-08-31 | [45002](https://github.com/airbytehq/airbyte/pull/45002) | Update dependencies |
| 0.3.19 | 2024-08-24 | [44629](https://github.com/airbytehq/airbyte/pull/44629) | Update dependencies |
| 0.3.18 | 2024-08-17 | [44343](https://github.com/airbytehq/airbyte/pull/44343) | Update dependencies |
| 0.3.17 | 2024-08-12 | [43759](https://github.com/airbytehq/airbyte/pull/43759) | Update dependencies |
| 0.3.16 | 2024-08-10 | [43698](https://github.com/airbytehq/airbyte/pull/43698) | Update dependencies |
| 0.3.15 | 2024-08-03 | [43107](https://github.com/airbytehq/airbyte/pull/43107) | Update dependencies |
| 0.3.14 | 2024-07-27 | [42752](https://github.com/airbytehq/airbyte/pull/42752) | Update dependencies |
| 0.3.13 | 2024-07-20 | [42308](https://github.com/airbytehq/airbyte/pull/42308) | Update dependencies |
| 0.3.12 | 2024-07-13 | [41701](https://github.com/airbytehq/airbyte/pull/41701) | Update dependencies |
| 0.3.11 | 2024-07-10 | [41352](https://github.com/airbytehq/airbyte/pull/41352) | Update dependencies |
| 0.3.10 | 2024-07-09 | [41258](https://github.com/airbytehq/airbyte/pull/41258) | Update dependencies |
| 0.3.9 | 2024-07-06 | [40958](https://github.com/airbytehq/airbyte/pull/40958) | Update dependencies |
| 0.3.8 | 2024-06-26 | [40549](https://github.com/airbytehq/airbyte/pull/40549) | Migrate off deprecated auth package |
| 0.3.7 | 2024-06-25 | [40298](https://github.com/airbytehq/airbyte/pull/40298) | Update dependencies |
| 0.3.6 | 2024-06-22 | [40031](https://github.com/airbytehq/airbyte/pull/40031) | Update dependencies |
| 0.3.5 | 2024-06-07 | [39329](https://github.com/airbytehq/airbyte/pull/39329) | Add `CheckpointMixin` for state management |
| 0.3.4 | 2024-06-06 | [39244](https://github.com/airbytehq/airbyte/pull/39244) | [autopull] Upgrade base image to v1.2.2 |
| 0.3.3 | 2024-05-22 | [38559](https://github.com/airbytehq/airbyte/pull/38559) | Migrate Python stream authenticator to `requests_native_auth` package |
| 0.3.2 | 2024-05-20 | [38244](https://github.com/airbytehq/airbyte/pull/38244) | Replace AirbyteLogger with logging.Logger and upgrade base image |
| 0.3.1 | 2024-04-24 | [36664](https://github.com/airbytehq/airbyte/pull/36664) | Schema descriptions and CDK 0.80.0 |
| 0.3.0 | 2024-02-22 | [35561](https://github.com/airbytehq/airbyte/pull/35561) | Migrate connector to low-code |
| 0.2.4 | 2024-02-12 | [35168](https://github.com/airbytehq/airbyte/pull/35168) | Manage dependencies with Poetry |
| 0.2.3 | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.2 | 2023-05-12 | [26024](https://github.com/airbytehq/airbyte/pull/26024) | Fix dependencies conflict |
| 0.2.1 | 2023-04-27 | [25109](https://github.com/airbytehq/airbyte/pull/25109) | Fix add missing params to stream `SurveyResponses` |
| 0.2.0 | 2023-04-18 | [23721](https://github.com/airbytehq/airbyte/pull/23721) | Add `SurveyCollectors` and `Collectors` stream |
| 0.1.16 | 2023-04-13 | [25080](https://github.com/airbytehq/airbyte/pull/25080) | Fix spec.json required fields and update schema for surveys and survey_responses |
| 0.1.15 | 2023-02-11 | [22865](https://github.com/airbytehq/airbyte/pull/22865) | Specified date formatting in specification |
| 0.1.14 | 2023-01-27 | [22024](https://github.com/airbytehq/airbyte/pull/22024) | Set `AvailabilityStrategy` for streams explicitly to `None` |
| 0.1.13 | 2022-11-29 | [19868](https://github.com/airbytehq/airbyte/pull/19868) | Fix OAuth flow urls |
| 0.1.12 | 2022-10-13 | [17964](https://github.com/airbytehq/airbyte/pull/17964) | Add OAuth for Eu and Ca |
| 0.1.11 | 2022-09-28 | [17326](https://github.com/airbytehq/airbyte/pull/17326) | Migrate to per-stream states |
| 0.1.10 | 2022-09-14 | [16706](https://github.com/airbytehq/airbyte/pull/16706) | Fix 404 error when handling nonexistent surveys |
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
