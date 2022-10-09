# Zenloop

## Sync overview

This source can sync data for the [Zenloop API](https://docs.zenloop.com/reference). It supports both Full Refresh and Incremental syncs for Answer endpoints. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

This Source is capable of syncing the following core Streams:

* [Answers](https://docs.zenloop.com/reference#get-answers) \(Incremental\)
* [Surveys](https://docs.zenloop.com/reference#get-list-of-surveys)
* [AnswersSurveyGroup](https://docs.zenloop.com/reference#get-answers-for-survey-group) \(Incremental\)
* [SurveyGroups](https://docs.zenloop.com/reference#get-list-of-survey-groups)
* [Properties](https://docs.zenloop.com/reference#get-list-of-properties)

The `Answers`, `AnswersSurveyGroup` and `Properties` stream respectively have an optional survey_id parameter that can be set by filling the `public_hash_id` field of the connector configuration. If not provided answers for all surveys (groups) will be pulled.

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `integer`        | `integer`    |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | Yes                  |       |
| Namespaces        | No                   |       |

### Performance considerations

The Zenloop connector should not run into Zenloop API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Zenloop account
* Zenloop API token

### Setup guide

Please register on Zenloop and retrieve your API token [here](https://app.zenloop.com/settings/api).

## Changelog

| Version | Date       | Pull Request                                             | Subject                       |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------- |
| 0.1.3   | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/pull/17304) | Migrate to per-stream states. |
| 0.1.2   | 2022-08-22 | [15843](https://github.com/airbytehq/airbyte/pull/15843) | Adds Properties stream        |
| 0.1.1   | 2021-10-26 | [8299](https://github.com/airbytehq/airbyte/pull/8299)   | Fix missing seed files        |
| 0.1.0   | 2021-10-26 | [7380](https://github.com/airbytehq/airbyte/pull/7380)   | Initial Release               |
