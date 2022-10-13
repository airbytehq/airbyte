# SurveyMonkey

This page guides you through the process of setting up the SurveyMonkey source connector.

## Prerequisites 

 ### For Airbyte Open Source:
* Access Token

## Setup guide
### Step 1: Set up SurveyMonkey
Please read this [docs](https://developer.surveymonkey.com/api/v3/#getting-started). Register your application [here](https://developer.surveymonkey.com/apps/) Then go to Settings and copy your access token

## Step 2: Set up the source connector in Airbyte

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **SurveyMonkey** from the Source type dropdown and enter a name for this connector.
4. lick `Authenticate your account`.
5. Log in and Authorize to the SurveyMonkey account
6. Choose required Start date
7. click `Set up source`.

**For Airbyte Open Source:**

1. Go to local Airbyte page.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**. 
3. On the source setup page, select **SurveyMonkey** from the Source type dropdown and enter a name for this connector.
4. Add **Access Token**
5. Choose required Start date
6. Click `Set up source`.

## Supported streams and sync modes

* [Surveys](https://developer.surveymonkey.com/api/v3/#surveys) \(Incremental\)
* [SurveyPages](https://developer.surveymonkey.com/api/v3/#surveys-id-pages)
* [SurveyQuestions](https://developer.surveymonkey.com/api/v3/#surveys-id-pages-id-questions)
* [SurveyResponses](https://developer.surveymonkey.com/api/v3/#survey-responses) \(Incremental\)

### Performance considerations

The SurveyMonkey API applies heavy API quotas for default private apps, which have the following limits:

* 125 requests per minute
* 500 requests per day

To cover more data from this source we use caching.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                  |
|:--------|:-----------|:---------------------------------------------------------|:-------------------------------------------------------------------------|
| 0.1.9   | 2022-07-28 | [13046](https://github.com/airbytehq/airbyte/pull/14998) | fixed state for response stream, fixed backoff behaviour, added unittest |
| 0.1.8   | 2022-05-20 | [13046](https://github.com/airbytehq/airbyte/pull/13046) | Fix incremental streams                                                  |
| 0.1.7   | 2022-02-24 | [8768](https://github.com/airbytehq/airbyte/pull/8768)   | Add custom survey IDs to limit API calls                                 |
| 0.1.6   | 2022-01-14 | [9508](https://github.com/airbytehq/airbyte/pull/9508)   | Scopes change                                                            |
| 0.1.5   | 2021-12-28 | [8628](https://github.com/airbytehq/airbyte/pull/8628)   | Update fields in source-connectors specifications                        |
| 0.1.4   | 2021-11-11 | [7868](https://github.com/airbytehq/airbyte/pull/7868)   | Improve 'check' using '/users/me' API call                               |
| 0.1.3   | 2021-11-01 | [7433](https://github.com/airbytehq/airbyte/pull/7433)   | Remove unsused oAuth flow parameters                                     |
| 0.1.2   | 2021-10-27 | [7433](https://github.com/airbytehq/airbyte/pull/7433)   | Add OAuth support                                                        |
| 0.1.1   | 2021-09-10 | [5983](https://github.com/airbytehq/airbyte/pull/5983)   | Fix caching for gzip compressed http response                            |
| 0.1.0   | 2021-07-06 | [4097](https://github.com/airbytehq/airbyte/pull/4097)   | Initial Release                                                          |

