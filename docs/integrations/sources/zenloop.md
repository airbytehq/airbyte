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

- [Answers](https://docs.zenloop.com/reference#get-answers) \(Incremental\)
- [Surveys](https://docs.zenloop.com/reference#get-list-of-surveys)
- [AnswersSurveyGroup](https://docs.zenloop.com/reference#get-answers-for-survey-group) \(Incremental\)
- [SurveyGroups](https://docs.zenloop.com/reference#get-list-of-survey-groups)
- [Properties](https://docs.zenloop.com/reference#get-list-of-properties)

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

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.1.15 | 2024-06-04 | [38961](https://github.com/airbytehq/airbyte/pull/38961) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.14 | 2024-04-19 | [37304](https://github.com/airbytehq/airbyte/pull/37304) | Updating to 0.80.0 CDK |
| 0.1.13 | 2024-04-18 | [37304](https://github.com/airbytehq/airbyte/pull/37304) | Manage dependencies with Poetry. |
| 0.1.12 | 2024-04-15 | [37304](https://github.com/airbytehq/airbyte/pull/37304) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.11 | 2024-04-12 | [37304](https://github.com/airbytehq/airbyte/pull/37304) | schema descriptions |
| 0.1.10 | 2023-06-29 | [27838](https://github.com/airbytehq/airbyte/pull/27838) | Update CDK version to avoid bug introduced during data feed release |
| 0.1.9 | 2023-06-28 | [27761](https://github.com/airbytehq/airbyte/pull/27761) | Update following state breaking changes |
| 0.1.8 | 2023-06-22 | [27243](https://github.com/airbytehq/airbyte/pull/27243) | Improving error message on state discrepancy |
| 0.1.7 | 2023-06-22 | [27243](https://github.com/airbytehq/airbyte/pull/27243) | State per partition (breaking change - require reset) |
| 0.1.6 | 2023-03-06 | [23231](https://github.com/airbytehq/airbyte/pull/23231) | Publish using low-code CDK Beta version |
| 0.1.5 | 2023-02-08 | [0](https://github.com/airbytehq/airbyte/pull/0) | Fix unhashable type in ZenloopSubstreamSlicer component |
| 0.1.4 | 2022-11-18 | [19624](https://github.com/airbytehq/airbyte/pull/19624) | Migrate to low code |
| 0.1.3 | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/pull/17304) | Migrate to per-stream states |
| 0.1.2 | 2022-08-22 | [15843](https://github.com/airbytehq/airbyte/pull/15843) | Adds Properties stream |
| 0.1.1 | 2021-10-26 | [8299](https://github.com/airbytehq/airbyte/pull/8299) | Fix missing seed files |
| 0.1.0 | 2021-10-26 | [7380](https://github.com/airbytehq/airbyte/pull/7380) | Initial Release |

</details>
