# Setting up the SurveyMonkey connector

Airbyte uses the SurveyMonkey source connector to ingest data from a SurveyMonkey instance.

:::note

Official support for authentication to SurveyMonkey using OAuth is only supported within the United States. For support with any issues, [send Airbyte an email message](mailto:product@airbyte.io).

<!---
PEcheverri comment: Forward-looking statements like "We're testing EU support and will have it in the future" aren't usually a good fit for tech doc. Absent strong customer pressure to acknowledge that it's upcoming, I would advocate for its removal, as I have done here.
--->

:::

<!-- env:oss -->
## Before you start

Make sure you have all the prerequisites in place before beginning the setup process.

**For Airbyte Open Source:**

* Verify that you have access to a valid Access Token.
<!-- /env:oss -->

<!---
PEcheverri comment: How is this Airbyte Open Source token acquired? Ideally there is a link to such a procedure here.
--->

<!---
## Setup guide

Unnecessary title, we're already in the 'this is how you set up surveymonkey' area; setting the subsequent headers to one level higher
--->

## Part 1: Setting up SurveyMonkey

<!---

I've renamed these to parts, because they each have several steps, so they can't be steps themselves.

--->

SurveyMonkey provides details on getting started in their [documentation](https://developer.surveymonkey.com/api/v3/#getting-started).

1. Log in to the SurveyMonkey [developer site](https://developer.surveymonkey.com/apps/).
	The SurveyMonkey developer dashboard appears.
	<!---
	PEcheverri comment: find out if that's the name for it, would need a SM test account
	--->
2. Register your app.
	<!---
	Needs full clickpath to exactly how that happens and the flow
	--->
3. From *Settings*, copy your access token.
	<!---
	Needs full clickpath to Settings pane
	--->

## Part 2: Setting up the source connector in Airbyte

<!-- env:cloud -->
**For Airbyte Cloud:**

1. [Log in](https://cloud.airbyte.com/workspaces) to your Airbyte Cloud account.
2. In the left navigation bar, click **Sources**.
	<!---
	Needs a result sentence here describing the expected result of the action
	--->
3. In the top-right corner, click **+ new source**.
	<!---
	Needs a result sentence here describing the expected result of the action
	--->
4. From the Source type drop-down in the source setup page, select **SurveyMonkey** and type a name for the connector.
5. Click `Authenticate your account`.
6. Log in and authorize to the SurveyMonkey account.
	<!---
	Are 'log in' and 'authorize' actually distinct things? if not, just 'log in'
	--->
7. Choose a start date.
	<!---
	Is that entered in a particular field? If so, name it specifically. If it's picked from a calendar-picker thing, say that.
	--->
8. click `Set up source`.

The SurveyMonkey source connector is now set up in Airbyte Cloud.
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

1. Go to the local Airbyte page.
2. In the left navigation bar, click **Sources**.
3. In the top-right corner, click **+ new source**.
4. From the Source type drop-down in the source setup page, select **SurveyMonkey** and type a name for the connector.
5. Add **Access Token**.
	<!---
	Add it where? Name the field or other UI element.
	--->
6. Choose a start date.
	<!---
	Is that entered in a particular field? If so, name it specifically. If it's picked from a calendar-picker thing, say that.
	--->
7. Click `Set up source`.

The SurveyMonkey source connector is now set up in Airbyte Open Source.
<!-- /env:oss -->

## Supported streams and sync modes

* [Surveys](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys) \(Incremental\)
* [SurveyPages](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys-survey_id-pages)
* [SurveyQuestions](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys-survey_id-pages-page_id-questions)
* [SurveyResponses](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys-id-responses-bulk) \(Incremental\)
* [SurveyCollectors](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys-survey_id-collectors)
* [Collectors](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-collectors-collector_id-)

## Performance considerations

<!---
Doesn't really feel like a subset of 'Supported streams and sync nodes', but rather a peer-level heading. Amended accordingly.
--->

The SurveyMonkey API sets the following request quotas for default private apps:

* 125 requests per minute
* 500 requests per day

Airbyte uses caching to ingest more data from this source.

<!---
Confirm 'ingest' is the right verb here, working off context
--->

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                          |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------------------------------------------------------------|
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
