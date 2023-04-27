# SurveyMonkey

This page guides you through the process of setting up the SurveyMonkey source connector.

:::note

OAuth for Survey Monkey is officially supported only for the US. We are testing how to enable it in the EU at the moment. If you run into any issues, please [reach out to us](mailto:product@airbyte.io) so we can promptly assist you.

:::

<!-- env:oss -->
## Prerequisites

**For Airbyte Open Source:**

* Access Token
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

* [Surveys](https://developer.surveymonkey.com/api/v3/#surveys) \(Incremental\)
* [SurveyPages](https://developer.surveymonkey.com/api/v3/#surveys-id-pages)
* [SurveyQuestions](https://developer.surveymonkey.com/api/v3/#surveys-id-pages-id-questions)
* [SurveyResponses](https://developer.surveymonkey.com/api/v3/#survey-responses) \(Incremental\)
* [SurveyCollectors](https://developer.surveymonkey.com/api/v3/#api-endpoints-get-surveys-id-collectors)

### Performance considerations

The SurveyMonkey API applies heavy API quotas for default private apps, which have the following limits:

* 125 requests per minute
* 500 requests per day

To cover more data from this source we use caching.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                |
|:--------| :--------- | :------------------------------------------------------- | :--------------------------------------------------------------------- |
| 0.2.1   | 2023-04-27 | [25109](https://github.com/airbytehq/airbyte/pull/25109) | Fix add missing params to stream `SurveyResponses`                                |
| 0.2.0   | 2023-04-18 | [23721](https://github.com/airbytehq/airbyte/pull/23721) |  Add `SurveyCollectors` and `Collectors` stream                                              |
| 0.1.16  | 2023-04-13 | [25080](https://github.com/airbytehq/airbyte/pull/25080) |  Fix spec.json required fields and update schema for surveys and survey_responses                    |
| 0.1.15  | 2023-02-11 | [22865](https://github.com/airbytehq/airbyte/pull/22865) | Specified date formatting in specification                                                     |
| 0.1.14  | 2023-01-27 | [22024](https://github.com/airbytehq/airbyte/pull/22024) | Set `AvailabilityStrategy` for streams explicitly to `None`                                                     |
| 0.1.13  | 2022-11-29 | [19868](https://github.com/airbytehq/airbyte/pull/19868) | Fix OAuth flow urls                                                    |
| 0.1.12  | 2022-10-13 | [17964](https://github.com/airbytehq/airbyte/pull/17964) | Add OAuth for Eu and Ca                                                |
| 0.1.11  | 2022-09-28 | [17326](https://github.com/airbytehq/airbyte/pull/17326) | Migrate to per-stream states.                                          |
| 0.1.10  | 2022-09-14 | [16706](https://github.com/airbytehq/airbyte/pull/16706) | Fix 404 error when handling nonexistent surveys                        |
| 0.1.9   | 2022-07-28 | [13046](https://github.com/airbytehq/airbyte/pull/14998) | Fix state for response stream, fixed backoff behaviour, added unittest |
| 0.1.8   | 2022-05-20 | [13046](https://github.com/airbytehq/airbyte/pull/13046) | Fix incremental streams                                                |
| 0.1.7   | 2022-02-24 | [8768](https://github.com/airbytehq/airbyte/pull/8768)   | Add custom survey IDs to limit API calls                               |
| 0.1.6   | 2022-01-14 | [9508](https://github.com/airbytehq/airbyte/pull/9508)   | Scopes change                                                          |
| 0.1.5   | 2021-12-28 | [8628](https://github.com/airbytehq/airbyte/pull/8628)   | Update fields in source-connectors specifications                      |
| 0.1.4   | 2021-11-11 | [7868](https://github.com/airbytehq/airbyte/pull/7868)   | Improve 'check' using '/users/me' API call                             |
| 0.1.3   | 2021-11-01 | [7433](https://github.com/airbytehq/airbyte/pull/7433)   | Remove unsused oAuth flow parameters                                   |
| 0.1.2   | 2021-10-27 | [7433](https://github.com/airbytehq/airbyte/pull/7433)   | Add OAuth support                                                      |
| 0.1.1   | 2021-09-10 | [5983](https://github.com/airbytehq/airbyte/pull/5983)   | Fix caching for gzip compressed http response                          |
| 0.1.0   | 2021-07-06 | [4097](https://github.com/airbytehq/airbyte/pull/4097)   | Initial Release                                                        |
