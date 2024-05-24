# SurveyMonkey

Learn how to set up SurveyMonkey connectors with Airbyte Cloud and Airbyte OSS. With this connector, you can pull data from or push data to SurveyMonkey. 

Need help? [Contact us](mailto:product@airbyte.io).

# At a Glance

|     |       |
|-----|-------|
| Availability | Airbyte Cloud, Airybyte OSS, PyAirbyte |
| Support Level | [Certified](https://docs.airbyte.com/integrations/connector-support-levels/) |
|Latest Version | [0.3.2](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-surveymonkey) |
| Performance | Maximums: </br> * 125 requests per minute </br> * 500 requests per day |
| Supported Streams |[Surveys](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys) \(Incremental\) </br> [SurveyPages](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys-survey_id-pages) </br>  [SurveyQuestions](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys-survey_id-pages-page_id-questions) </br>  [SurveyResponses](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys-id-responses-bulk) \(Incremental\) </br>  [SurveyCollectors](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys-survey_id-collectors) </br>  [Collectors](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-collectors-collector_id-) |


:::
**NOTE**: 
We support OAuth for SurveyMonkey in the United States. We have plans to enable it in the EU at a later date. 
:::

<!-- env:oss -->

## Prerequisites
* For Airbyte Open Source and Airbyte Cloud: [Register your application with SurveyMonkey](https://developer.surveymonkey.com/apps/). Login credentials required.
* For Airbyte Open Source only: Get your access token from the Settings of your SurveyMonkey account. 
For more information about the SurveyMonkey APIs, check out their [Getting Started  Overview](https://developer.surveymonkey.com/api/v3/#getting-started).

## Steps
1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account  or go to a local Airbyte page.
2. From the left navigation bar, click **Sources**. 
3. Click the **SurveyMonkey** tile. </br> You can start typing *SurveyMonkey* in the **Search** field to find the tile. 
4. For **Source name**, enter a name that will help you identify this connector in Airbyte. 
5. Authenticate your SurveyMonkey account: 
    * For Airbyte Cloud: Click **Authenticate your SurveyMonkey account**. </br>Follow the prompts from SurveyMonkey to complete the authentication process. 
    * For Airbyte Open Source: Enter your Access Token. </br>Find your Access Token in the **Settings** of your SurveyMonkey account.
6. Enter a **Start Date**. </br>To open the calendar picker, click the **Start Date** field and pick the date and time. </br> You can also enter the start date, including a continental time stamp. </br> We use the UTC time zone. </br> 
    * Format: yyyy-mm-ddThh:mm:ssZ 
    * Example Date and Time: May 5, 2024 at 7:15 p.m. UTC 
    * Example Formatted Date and Time: 2024-05-15T19:15:00Z 
7. Optional. To display more fields, click **Optional Fields**.
8. Optional. Select the origin of the data center. </br>Data centers from different countries might have different access URLs.
9. Optional. To pull the data from specific surveys, enter the survey IDs. </br> Use commas to separate many surveys. </br> Leave blank to include all owned and shared surveys.
10. Click **Set up source**.

## Next Steps
* Set Up Destinations (link to topic)
* Configure MonkeySurvey Connections (link to topic)

## Reference: Configuration Fields
\* Required field.

| Field | Type | Property Name | Description |
|----------------- | ---------- |----------------- |--------------------------------------- |
| SurveyMonkey Authorization Method* | Object | credentials | The authorization method you need to retrieve data from SurveyMonkey. |
| auth_method* | “oath2.0” | auth_method | You must enter oath2.0. |
| Access Token* | string | access_token | A token generated from your SurveyMonkey account. |
| Client ID | string | client_id | Identification for the SurveyMonkey developer application. |
| Client Secret | string | client_secret | Secret for the SurveyMonkey developer application. |
| Start Date* | string | start_date | The date and time to start pulling data. Use continental time. </br>Format: yyyy-mm-ddThh:mm:ssZ|
| Origin datacenter of the SurveyMonkey account | string | origin | Default: USA. </br> Options: Canada, EU, USA </br> The access URL might be different for different origins. |
|SurveyMonkey survey IDs | string | survey_ids | Specify surveys to include in the call, separated by commas. </br> Leave blank to include all your owned and shared surveys. |

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                          |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------- |
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
