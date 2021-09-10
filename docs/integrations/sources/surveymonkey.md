# SurveyMonkey

## Sync overview

This source can sync data for the [SurveyMonkey API](https://developer.surveymonkey.com/api/v3/). It supports both Full Refresh and Incremental syncs.
You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

This Source is capable of syncing the following core Streams:

* [Surveys](https://developer.surveymonkey.com/api/v3/#surveys) (Incremental)
* [SurveyPages](https://developer.surveymonkey.com/api/v3/#surveys-id-pages)
* [SurveyQuestions](https://developer.surveymonkey.com/api/v3/#surveys-id-pages-id-questions)
* [SurveyResponses](https://developer.surveymonkey.com/api/v3/#survey-responses)

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `number` | `number` |  |
| `array` | `array` |  |
| `object` | `object` |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Yes |  |
| Namespaces | No |  |

### Performance considerations

The SurveyMonkey API applies heavy API quotas for default private apps, which have the following limits:
* 125 requests per minute
* 500 requests per day

To cover more data from this source we use caching.

Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* SurveyMonkey API Key

### Setup guide

Please read this [docs](https://developer.surveymonkey.com/api/v3/#getting-started).
Register your application [here](https://developer.surveymonkey.com/apps/)
Then go to Settings and copy your access token 

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.1   | 2021-09-10 | [5983](https://github.com/airbytehq/airbyte/pull/5983) | Fix caching for gzip compressed http response |
| 0.1.0   | 2021-07-06 | [4097](https://github.com/airbytehq/airbyte/pull/4097) | Initial Release |
