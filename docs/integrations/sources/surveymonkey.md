# SurveyMonkey

Learn how to set up the SurveyMonkey source connector. A source connector extracts data from SurveyMonkey and transfers the data to a destination. Learn more about connectors [here](/using-airbyte/core-concepts/).

:::note

OAuth for SurveyMonkey is available in the US only. We are testing how to enable OAuth in the EU. [Reach out to us](mailto:product@airbyte.io) if you run into any issues with authentication.

:::

<!-- env:oss -->
## Know before you begin

You need a SurveyMonkey access token if you're using Airbyte Open Source to set up the connector. Use this token to authenticate your SurveyMonkey account with Airbyte Open Source.
<!-- /env:oss -->

## Set up the SurveyMonkey connector in Airbyte

### Step 1: Set up SurveyMonkey

1. Create or log in to your [SurveyMonkey account](https://developer.surveymonkey.com/apps/).
2. In My Apps, click **Add a New App**. The App Creation screen displays.
3. Enter an **App Nickname** and **App Creator** email address.
4. Select a public or private app type depending on your use case.
5. Click **Create App**. The app overview page displays.
6. Click **Settings**.
7. In the Credentials section, copy your access token. You will use this token later in the guide.

**Step result:** You registered a new SurveyMonkey app and access token.
For more information about SurveyMonkey apps, read their [docs](https://developer.surveymonkey.com/api/v3/#SurveyMonkey-Api).

### Step 2: Set up the source connector in Airbyte

<!-- env:cloud -->
**For Airbyte Cloud:**

1. Log into your [Airbyte Cloud account](https://cloud.airbyte.com/workspaces).
2. Select an existing workspace or create a new one by clicking **+ New Workspace**.
3. In the navigation menu, click **Sources**. A new page displays all available Airbyte sources.
4. Find and select the **SurveyMonkey** source. The Create a source page displays.
5. For **Source name**, enter a name for this connector.
6. Click **Authenticate your SurveyMonkey account**.
7. Log in to Airbyte Cloud and authorize the SurveyMonkey account.
8. Choose the required **Start date**.
9. Click **Set up source**.

Step result: You created a source connector in Airbyte Cloud.
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

1. Go to your local Airbyte page.
2. In the navigation menu, click **Sources**. A new page displays all available Airbyte sources.
3. Find and select the **SurveyMonkey** source. The Create a source page displays.
5. For **Source name**, enter a name for this connector.
4. Add your SurveyMonkey access token.
8. Choose the required **Start date**.
9. Click **Set up source**.

Step result: You created a source connector in Airbyte Cloud.
<!-- /env:oss -->

## Supported streams and sync modes

* [Surveys](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys) \(Incremental\)
* [SurveyPages](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys-survey_id-pages)
* [SurveyQuestions](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys-survey_id-pages-page_id-questions)
* [SurveyResponses](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys-id-responses-bulk) \(Incremental\)
* [SurveyCollectors](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys-survey_id-collectors)
* [Collectors](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-collectors-collector_id-)

### Performance considerations

The SurveyMonkey API applies heavy API quotas for default private apps, which have the following limits:

* 125 requests per minute.
* 500 requests per day.

Use caching to cover more data from this source.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                          |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------------------------------------------------------------|
| 0.3.1   | 2024-05-04 | [37831](https://github.com/airbytehq/airbyte/pull/37831) | Apply editorial review.                                                          |
| 0.3.0   | 2024-02-22 | [35561](https://github.com/airbytehq/airbyte/pull/35561) | Migrate connector to low-code.                                                   |
| 0.2.4   | 2024-02-12 | [35168](https://github.com/airbytehq/airbyte/pull/35168) | Manage dependencies with Poetry.                                                 |
| 0.2.3   | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove the Dockerfile and use the python-connector-base image. |
| 0.2.2   | 2023-05-12 | [26024](https://github.com/airbytehq/airbyte/pull/26024) | Fix dependencies conflict.                                                       |
| 0.2.1   | 2023-04-27 | [25109](https://github.com/airbytehq/airbyte/pull/25109) | Fix add missing params to stream `SurveyResponses`.                              |
| 0.2.0   | 2023-04-18 | [23721](https://github.com/airbytehq/airbyte/pull/23721) | Add `SurveyCollectors` and `Collectors` stream.                                  |
| 0.1.16  | 2023-04-13 | [25080](https://github.com/airbytehq/airbyte/pull/25080) | Fix spec.json required fields and update schema for surveys and survey_responses.|
| 0.1.15  | 2023-02-11 | [22865](https://github.com/airbytehq/airbyte/pull/22865) | Specified date formatting in the specification.                                  |
| 0.1.14  | 2023-01-27 | [22024](https://github.com/airbytehq/airbyte/pull/22024) | Set `AvailabilityStrategy` for streams explicitly to `None`.                     |
| 0.1.13  | 2022-11-29 | [19868](https://github.com/airbytehq/airbyte/pull/19868) | Fix OAuth flow URLs.                                                             |
| 0.1.12  | 2022-10-13 | [17964](https://github.com/airbytehq/airbyte/pull/17964) | Add OAuth for EU and CA.                                                         |
| 0.1.11  | 2022-09-28 | [17326](https://github.com/airbytehq/airbyte/pull/17326) | Migrate to per-stream states.                                                    |
| 0.1.10  | 2022-09-14 | [16706](https://github.com/airbytehq/airbyte/pull/16706) | Fix 404 error when handling nonexistent surveys.                                 |
| 0.1.9   | 2022-07-28 | [13046](https://github.com/airbytehq/airbyte/pull/14998) | Fix state for response stream. Fixed backoff behavior. Added unit test.          |
| 0.1.8   | 2022-05-20 | [13046](https://github.com/airbytehq/airbyte/pull/13046) | Fix incremental streams.                                                         |
| 0.1.7   | 2022-02-24 | [8768](https://github.com/airbytehq/airbyte/pull/8768)   | Add custom survey IDs to limit API calls.                                        |
| 0.1.6   | 2022-01-14 | [9508](https://github.com/airbytehq/airbyte/pull/9508)   | Scopes change.                                                                   |
| 0.1.5   | 2021-12-28 | [8628](https://github.com/airbytehq/airbyte/pull/8628)   | Update fields in source-connectors specifications.                               |
| 0.1.4   | 2021-11-11 | [7868](https://github.com/airbytehq/airbyte/pull/7868)   | Improve 'check' using '/users/me' API call.                                      |
| 0.1.3   | 2021-11-01 | [7433](https://github.com/airbytehq/airbyte/pull/7433)   | Remove unused oAuth flow parameters.                                             |
| 0.1.2   | 2021-10-27 | [7433](https://github.com/airbytehq/airbyte/pull/7433)   | Add OAuth support.                                                               |
| 0.1.1   | 2021-09-10 | [5983](https://github.com/airbytehq/airbyte/pull/5983)   | Fix caching for gzip-compressed HTTP response.                                   |
| 0.1.0   | 2021-07-06 | [4097](https://github.com/airbytehq/airbyte/pull/4097)   | Initial Release.                                                                 |
