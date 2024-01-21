# SurveyMonkey

<HideInUI>

This page contains the setup guide for the SurveyMonkey source connector.

</HideInUI>

:::note

<!-- TODO: Confirm new wording with PM or Eng -->

This connector only supports US-based SurveyMonkey accounts. We're testing how to enable the
connector for EU-based accounts. If you run into issues, contact us at
[product@airbyte.io](mailto:product@airbyte.io).

:::

<!-- env:oss -->

## Prerequisites

<HideInUI>

**For Airbyte Open Source:**

</HideInUI>

<!-- TODO: Talk to PM or Support to see if we should expand these steps. -->

-   Access token for a SurveyMonkey app. The app must have the following scopes marked as **Optional** or **Required**:

      - View Surveys
      - View Responses
      - View Response Details
      - View Users

    For more information, see [Registering an App](https://developer.surveymonkey.com/api/v3/#registering-an-app) in the SurveyMonkey developer docs.

<!-- /env:oss -->

## Setup guide

<!-- env:cloud -->

<HideInUI>

**For Airbyte Cloud:**

</HideInUI>

<!-- NIT: I'd typically capitalize "Sources page," but I'm leaving as is since this seems to be Airbyte style. -->

1.  Log in to [Airbyte Cloud](https://cloud.airbyte.com/login).
1.  In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
1.  On the sources page, click **SurveyMonkey**.
1.  Click **Authenticate your SurveyMonkey account**.
1.  Log in to SurveyMonkey and authorize the connection.
1.  In **Start Date**, enter a UTC date and time in the following format: `2099-01-25T00:00:00Z`.
    The connector won't replicate data before this date.
1.  (Optional) Click **Optional fields** to specify:
    - **Origin datacenter of the SurveyMonkey account**: For US-based SurveyMonkey accounts, leave
      this value as `USA`.
    - **Survey Monkey survey IDs**: If specified, the connector will only replicate data for these
      surveys. If left blank, the connector replicates data for any survey you can access.
1.  Click **Set up source**.

<!-- /env:cloud -->

<!-- env:oss -->

<HideInUI>

**For Airbyte Open Source:**

</HideInUI>

<!-- TODO: Talk to PM or UI team about fixing "Survey Monkey survey IDs" typo in app -->
<!-- I'm using the text with typo here for clarity. -->

<!-- TODO: Confirm that US-based accounts should leave "Origin datacenter" as is -->

1.  In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
1.  On the sources page, click **SurveyMonkey**.
1.  Enter your SurveyMonkey access token in **Access Token**.
1.  (Optional) Under **Access Token**, click **Optional fields** to specify:
    - **Client ID**: Client ID for your SurveyMonkey app.
    - **Client Secret**: Client secret for your SurveyMonkey app.
1.  In **Start Date**, enter a UTC date and time in the following format: `2099-01-25T00:00:00Z`.
    The connector won't replicate data before this date.
1.  (Optional) Under **Start Date**, click **Optional fields** to specify:
    - **Origin datacenter of the SurveyMonkey account**: For US-based SurveyMonkey accounts, leave
      this value as `USA`.
    - **Survey Monkey survey IDs**: If specified, the connector will only replicate data for these
      surveys. If left blank, the connector replicates data for any survey you can access.
1.  Click **Set up source**.
<!-- /env:oss -->

## Supported streams and sync modes

<!-- TODO: Confirm new links with PM or Eng -->

- [Surveys](https://developer.surveymonkey.com/api/v3/#api-endpoints-get-surveys) (Incremental)
- [SurveyPages](https://developer.surveymonkey.com/api/v3/#api-endpoints-get-surveys-survey_id-pages)
- [SurveyQuestions](https://developer.surveymonkey.com/api/v3/#api-endpoints-get-surveys-survey_id-pages-page_id-questions)
- [SurveyResponses](https://developer.surveymonkey.com/api/v3/#api-endpoints-get-surveys-id-responses) (Incremental)
- [SurveyCollectors](https://developer.surveymonkey.com/api/v3/#api-endpoints-get-surveys-survey_id-collectors)

<!-- env:oss -->

## Performance considerations

<!-- TODO: Confirm with PM or Eng -->

<HideInUI>

**For Airbyte Open Source:**

</HideInUI>

SurveyMonkey has [API request limits](https://api.surveymonkey.com/v3/docs?shell#request-and-response-limits) for
private apps. This connector uses caching to avoid these limits.

<!-- /env:oss -->

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                          |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------- |
| 0.2.3   | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove Dockerfile and use the python-connector-base image  |
| 0.2.2   | 2023-05-12 | [26024](https://github.com/airbytehq/airbyte/pull/26024) | Fix dependencies conflict                                                        |
| 0.2.1   | 2023-04-27 | [25109](https://github.com/airbytehq/airbyte/pull/25109) | Fix add missing params to stream `SurveyResponses`                               |
| 0.2.0   | 2023-04-18 | [23721](https://github.com/airbytehq/airbyte/pull/23721) | Add `SurveyCollectors` and `Collectors` stream                                   |
| 0.1.16  | 2023-04-13 | [25080](https://github.com/airbytehq/airbyte/pull/25080) | Fix spec.json required fields and update schema for surveys and survey_responses |
| 0.1.15  | 2023-02-11 | [22865](https://github.com/airbytehq/airbyte/pull/22865) | Specified date formatting in specification                                       |
| 0.1.14  | 2023-01-27 | [22024](https://github.com/airbytehq/airbyte/pull/22024) | Set `AvailabilityStrategy` for streams explicitly to `None`                      |
| 0.1.13  | 2022-11-29 | [19868](https://github.com/airbytehq/airbyte/pull/19868) | Fix OAuth flow urls                                                              |
| 0.1.12  | 2022-10-13 | [17964](https://github.com/airbytehq/airbyte/pull/17964) | Add OAuth for Eu and Ca                                                          |
| 0.1.11  | 2022-09-28 | [17326](https://github.com/airbytehq/airbyte/pull/17326) | Migrate to per-stream states.                                                    |
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
