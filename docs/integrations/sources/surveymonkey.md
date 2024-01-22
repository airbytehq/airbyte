import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";

# SurveyMonkey

This page guides you through the process of setting up the [SurveyMonkey](https://www.surveymonkey.com/) source connector to sync data from the [SurveyMonkey API](https://developer.surveymonkey.com/api/v3/#SurveyMonkey-Api).

:::note

Support for OAuth in Survey Monkey is currently available only for the US. We are actively testing the enablement of OAuth in the EU. If you encounter any issues, please **[reach out](mailto:product@airbyte.io)** to us for assistance.

:::

<!-- env:oss -->
## Prerequisites

For Airbyte Open Source, a SurveyMonkey **Access Token** is required.

<!-- /env:oss -->

## 1. Set up SurveyMonkey

<Tabs>
<TabItem value="setup-sm-cloud" label="Airbyte Cloud">

1. Create a [SurveyMonkey](https://www.surveymonkey.com/) account.

</TabItem>
<TabItem value="setup-sm-oss" label="Airbyte Open Source">

1. Create a [SurveyMonkey](https://www.surveymonkey.com/) account.
2. Register an [application](https://developer.surveymonkey.com/apps/) to your SurveyMonkey account. Registering creates a draft application with an **Access Token** you can use to make API queries against your account.
3. Navigate to the **Settings** tab of your application, and in the **Scopes** section, set the scope requirements for your application. Airbyte requires the following scopes marked as **Optional** or **Required**: 
    * View Users
    * View Surveys
    * View Responses
    * View Response Details
4. From the **Credentials** section of the **Settings** page, copy your **Access Token**.

</TabItem>
</Tabs>

## 2. Set up the source connector in Airbyte

<!-- env:cloud -->
<Tabs>
<TabItem value="setup-sc-cloud" label="Airbyte Cloud">
1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/login) account. If you’re new to Airbyte Cloud, you can [try it](https://cloud.airbyte.com/signup) for free.
2. Using the left-hand menu, navigate to the **Sources** page.
3. Use the search bar to find and select the certified SurveyMonkey source.
4. In the **Source name** field, pick a name to help you identify this source in Airbyte.
5. To authorize your SurveyMonkey account, click **Authenticate your SurveyMonkey account**. Airbyte will authenticate the SurveyMonkey account you are already logged in to. Be sure to authenticate to the correct account.
6. For the **Start Date** field, use the provided date picker or enter the date in [UTC](https://www.utctime.net/) date and time format: `YYYY-MM-DDTHH:MM:SSZ`. Any data before this date will not be replicated.
7. (Optional) Under **Optional fields**, target specific data from your SurveyMonkey account by providing the **Origin data center** and **Survey IDs** of your choice. If no fields are specified, Airbyte will replicate all data.
8. Click **Set up source** and wait for the tests to complete.
</TabItem>
<!-- /env:cloud -->
<!-- env:oss -->
<TabItem value="setup-sc-oss" label="Airbyte Open Source">

1. Navigate to your Airbyte Open Source dashboard. If you’re new to Airbyte Open Source, see our [Getting Started](https://docs.airbyte.com/using-airbyte/getting-started/) guide. 
2. Using the left-hand menu, navigate to the **Sources** page.
3. Use the search bar to find and select the certified SurveyMonkey source.
4. In the **Source name** field, pick a name to help you identify this source in Airbyte.
5. To make authenticated requests to your SurveyMonkey account, add your **Access Token**. For instructions on how to generate this token, see [SurveyMonkey Authentication](https://api.surveymonkey.com/v3/docs#authentication).
6. (Optional) Under **Access Token**, click **Optional fields** to add the **Client ID** and **Client Secret** of your SurveyMonkey application.
7. For the **Start Date** field, use the provided date picker or enter the date in [UTC](https://www.utctime.net/) date and time format: `YYYY-MM-DDTHH:MM:SSZ`. Any data before this date will not be replicated.
8. (Optional) Under **Optional fields**, target specific data from your SurveyMonkey account by providing the **Origin data center** and **Survey IDs** of your choice. If no fields are specified, Airbyte will replicate all data.
9. Click **Set up source** and wait for the tests to complete.
</TabItem>
</Tabs>
<!-- /env:oss -->


## Supported streams and sync modes

The SurveyMonkey source connector supports the following streams and [sync modes](https://docs.airbyte.com/using-airbyte/core-concepts/#sync-mode):

* [Surveys](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys) \(Incremental\)
* [SurveyPages](https://developer.surveymonkey.com/api/v3/#api-endpoints-survey-pages-and-questions)
* [SurveyQuestions](https://developer.surveymonkey.com/api/v3/#api-endpoints-survey-pages-and-questions)
* [SurveyResponses](https://developer.surveymonkey.com/api/v3/#api-endpoints-survey-responses) \(Incremental\)
* [SurveyCollectors](https://developer.surveymonkey.com/api/v3/#api-endpoints-collectors-and-invite-messages)

## Performance considerations

The SurveyMonkey API applies the following rate limits to their **Draft** and **Private** apps:

| Max Requests Per Minute | Max Requests Per Day |
|-------------------------|-----------------------|
|          120            |          500          |

To cover more data from this source we use caching. For more information, see [SurveyMonkey API Request and Response Limits](https://api.surveymonkey.com/v3/docs?shell#request-and-response-limits).

## Troubleshooting

* If you encounter access errors while authenticating to SurveyMonkey, please see the [SurveyMonkey Authentication](https://api.surveymonkey.com/v3/docs?shell#authentication) guide.
* Check out common troubleshooting issues for the SurveyMonkey source connector on our [Airbyte Forum](https://github.com/airbytehq/airbyte/discussions).

## Tutorials

Maximize your SurveyMonkey integration on Airbyte with the following tutorials:

* [How to Load Data from SurveyMonkey to Convex](https://airbyte.com/how-to-sync/surveymonkey-to-convex)
* [How to Move Data from SurveyMonkey to MeiliSearch in Minutes](https://airbyte.com/how-to-sync/surveymonkey-to-meilisearch)
* [Use Airbyte to Synchronize your SurveyMonkey Data Into Weaviate](https://airbyte.com/how-to-sync/surveymonkey-to-weaviate)

## Resources

For more on SurveyMonkey, see the resources below:

* [SurveyMonkey API Documentation](https://developer.surveymonkey.com/api/v3/#SurveyMonkey-Api)
* [SurveyMonkey Developer FAQ](https://developer.surveymonkey.com/faq/)
* [SurveyMonkey Support](https://help.surveymonkey.com/en/contact/)

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                          |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------------------------------------------------------------|
| 0.2.3 | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.2   | 2023-05-12 | [26024](https://github.com/airbytehq/airbyte/pull/26024) | Fix dependencies conflict                                                        |
| 0.2.1   | 2023-04-27 | [25109](https://github.com/airbytehq/airbyte/pull/25109) | Fix add missing params to stream `SurveyResponses`                               |
| 0.2.0   | 2023-04-18 | [23721](https://github.com/airbytehq/airbyte/pull/23721) | Add `SurveyCollectors` and `Collectors` stream                                   |
| 0.1.16  | 2023-04-13 | [25080](https://github.com/airbytehq/airbyte/pull/25080) | Fix spec.json required fields and update schema for `surveys` and `survey_responses` |
| 0.1.15  | 2023-02-11 | [22865](https://github.com/airbytehq/airbyte/pull/22865) | Specified date formatting in specification                                       |
| 0.1.14  | 2023-01-27 | [22024](https://github.com/airbytehq/airbyte/pull/22024) | Set `AvailabilityStrategy` for streams explicitly to `None`                      |
| 0.1.13  | 2022-11-29 | [19868](https://github.com/airbytehq/airbyte/pull/19868) | Fix OAuth flow URLs                                                              |
| 0.1.12  | 2022-10-13 | [17964](https://github.com/airbytehq/airbyte/pull/17964) | Add OAuth for EU and CA                                                          |
| 0.1.11  | 2022-09-28 | [17326](https://github.com/airbytehq/airbyte/pull/17326) | Migrate to per-stream states                                                    |
| 0.1.10  | 2022-09-14 | [16706](https://github.com/airbytehq/airbyte/pull/16706) | Fix 404 error when handling non-existent surveys                                  |
| 0.1.9   | 2022-07-28 | [13046](https://github.com/airbytehq/airbyte/pull/14998) | Fix state for response stream, fixed backoff behavior, added unit test           |
| 0.1.8   | 2022-05-20 | [13046](https://github.com/airbytehq/airbyte/pull/13046) | Fix incremental streams                                                          |
| 0.1.7   | 2022-02-24 | [8768](https://github.com/airbytehq/airbyte/pull/8768)   | Add custom Survey IDs to limit API calls                                         |
| 0.1.6   | 2022-01-14 | [9508](https://github.com/airbytehq/airbyte/pull/9508)   | Scopes change                                                                    |
| 0.1.5   | 2021-12-28 | [8628](https://github.com/airbytehq/airbyte/pull/8628)   | Update fields in source-connectors specifications                                |
| 0.1.4   | 2021-11-11 | [7868](https://github.com/airbytehq/airbyte/pull/7868)   | Improve `check` using `/users/me` API call                                       |
| 0.1.3   | 2021-11-01 | [7433](https://github.com/airbytehq/airbyte/pull/7433)   | Remove unsused OAuth flow parameters                                             |
| 0.1.2   | 2021-10-27 | [7433](https://github.com/airbytehq/airbyte/pull/7433)   | Add OAuth support                                                                |
| 0.1.1   | 2021-09-10 | [5983](https://github.com/airbytehq/airbyte/pull/5983)   | Fix caching for gzip compressed HTTP response                                    |
| 0.1.0   | 2021-07-06 | [4097](https://github.com/airbytehq/airbyte/pull/4097)   | Initial Release                                                                  |
                                                          |
