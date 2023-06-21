# Zenloop

This page contains the setup guide and reference information for the Zenloop source connector.

## Prerequisites
<!-- env:cloud -->
**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces).
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Zenloop** from the Source type dropdown.
4. Enter the name for the Zenloop connector.
5. Enter your **API token**
6. For **Date from**, enter the date in YYYY-MM-DDTHH:mm:ssZ format. The data added on and after this date will be replicated. 
7. Enter your **Survey ID**. Zenloop Survey ID. Can be found <a href="https://app.zenloop.com/settings/api">here</a>. Leave empty to pull answers from all surveys. (Optional)
8. Enter your **Survey Group ID**. Zenloop Survey Group ID. Can be found by pulling All Survey Groups via SurveyGroups stream. Leave empty to pull answers from all survey groups. (Optional)
9. Click **Set up source**.
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Zenloop** from the Source type dropdown.
4. Enter the name for the Zenloop connector.
5. Enter your **API token**
6. For **Date from**, enter the date in YYYY-MM-DDTHH:mm:ssZ format. The data added on and after this date will be replicated. 
7. Enter your **Survey ID**. Zenloop Survey ID. Can be found <a href="https://app.zenloop.com/settings/api">here</a>. Leave empty to pull answers from all surveys. (Optional)
8. Enter your **Survey Group ID**. Zenloop Survey Group ID. Can be found by pulling All Survey Groups via SurveyGroups stream. Leave empty to pull answers from all survey groups. (Optional)
9. Click **Set up source**.
<!-- /env:oss -->

## Supported sync modes

The Zenloop source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported?\(Yes/No\) |
| :---------------- | :------------------- |
| Full Refresh Sync | Yes                  |
| Incremental Sync  | Yes                  |
| Namespaces        | No                   | 

## Supported Streams

This Source is capable of syncing the following core Streams:

* [Answers](https://docs.zenloop.com/reference#get-answers) \(Incremental\)
* [Surveys](https://docs.zenloop.com/reference#get-list-of-surveys)
* [AnswersSurveyGroup](https://docs.zenloop.com/reference#get-answers-for-survey-group) \(Incremental\)
* [SurveyGroups](https://docs.zenloop.com/reference#get-list-of-survey-groups)
* [Properties](https://docs.zenloop.com/reference#get-list-of-properties)

The `Answers`, `AnswersSurveyGroup` and `Properties` stream respectively have an optional survey_id parameter that can be set by filling the `public_hash_id` field of the connector configuration. If not provided answers for all surveys (groups) will be pulled.

## Performance considerations

The Zenloop connector should not run into Zenloop API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Data type map

| Integration Type | Airbyte Type |
| :--------------- | :----------- |
| `string`         | `string`     |
| `integer`        | `integer`    |
| `number`         | `number`     |
| `array`          | `array`      |
| `object`         | `object`     |

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                 |
|:--------| :--------- | :------------------------------------------------------- |:--------------------------------------------------------|
| 0.1.6   | 2023-03-06 | [23231](https://github.com/airbytehq/airbyte/pull/23231) | Publish using low-code CDK Beta version                 |
| 0.1.5   | 2023-02-08 | [00000](https://github.com/airbytehq/airbyte/pull/00000) | Fix unhashable type in ZenloopSubstreamSlicer component |
| 0.1.4   | 2022-11-18 | [19624](https://github.com/airbytehq/airbyte/pull/19624) | Migrate to low code                                     |
| 0.1.3   | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/pull/17304) | Migrate to per-stream states                            |
| 0.1.2   | 2022-08-22 | [15843](https://github.com/airbytehq/airbyte/pull/15843) | Adds Properties stream                                  |
| 0.1.1   | 2021-10-26 | [8299](https://github.com/airbytehq/airbyte/pull/8299)   | Fix missing seed files                                  |
| 0.1.0   | 2021-10-26 | [7380](https://github.com/airbytehq/airbyte/pull/7380)   | Initial Release                                         |
