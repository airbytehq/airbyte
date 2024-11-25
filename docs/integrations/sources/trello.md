# Trello

This page contains the setup guide and reference information for the Trello source connector.

## Prerequisites

- Start Date
- Trello Board IDs (Optional)

<!-- env:cloud -->

**For Airbyte Cloud:**

- OAuth 1.0
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

- API Key (see [Authorizing A Client](https://developer.atlassian.com/cloud/trello/guides/rest-api/authorization/#authorizing-a-client))
- API Token (see [Authorizing A Client](https://developer.atlassian.com/cloud/trello/guides/rest-api/authorization/#authorizing-a-client))
<!-- /env:oss -->

## Setup guide

### Step 1: Set up Trello

Create a [Trello Account](https://trello.com).

<!-- env:cloud -->

### Step 2: Set up the Trello connector in Airbyte

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Trello** from the Source type dropdown and enter a name for this connector.
4. Click `Authenticate your Trello account`.
5. Log in and `Allow` access.
6. **Start date** - The date from which you'd like to replicate data for streams.
7. **Trello Board IDs (Optional)** - IDs of the boards to replicate data from. If left empty, data from all boards to which you have access will be replicated.
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Authenticate with **API Key** and **API Token** pair.
<!-- /env:oss -->

## Supported sync modes

The Trello source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)

## Supported Streams

This connector outputs the following streams:

- [Boards](https://developer.atlassian.com/cloud/trello/rest/api-group-members/#api-members-id-boards-get) \(Full Refresh\)
  - [Actions](https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-boardid-actions-get) \(Incremental\)
  - [Cards](https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-cards-get) \(Full Refresh\)
  - [Checklists](https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-checklists-get) \(Full Refresh\)
  - [Lists](https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-lists-get) \(Full Refresh\)
  - [Users](https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-members-get) \(Full Refresh\)
  - [Organizations](https://developer.atlassian.com/cloud/trello/rest/api-group-members/#api-members-id-organizations-get) \(Full Refresh\)

### Performance considerations

The connector is restricted by normal Trello [requests limitation](https://developer.atlassian.com/cloud/trello/guides/rest-api/rate-limits/).

The Trello connector should not run into Trello API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                            |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------------------------------------- |
| 1.2.1 | 2024-10-29 | [43914](https://github.com/airbytehq/airbyte/pull/43914) | Update dependencies |
| 1.2.0 | 2024-10-22 | [47257](https://github.com/airbytehq/airbyte/pull/47257) | Migrate to Manifest-only |
| 1.1.0 | 2024-07-17 | [42019](https://github.com/airbytehq/airbyte/pull/42019) | Migrate to CDK v3.5.3 |
| 1.0.10 | 2024-07-13 | [41774](https://github.com/airbytehq/airbyte/pull/41774) | Update dependencies |
| 1.0.9 | 2024-07-10 | [41601](https://github.com/airbytehq/airbyte/pull/41601) | Update dependencies |
| 1.0.8 | 2024-07-09 | [41099](https://github.com/airbytehq/airbyte/pull/41099) | Update dependencies |
| 1.0.7 | 2024-07-06 | [40825](https://github.com/airbytehq/airbyte/pull/40825) | Update dependencies |
| 1.0.6 | 2024-06-27 | [40592](https://github.com/airbytehq/airbyte/pull/40592) | Updated to use latest `CDK` version, fixed `cursor pagination` logic |
| 1.0.5 | 2024-06-29 | [39999](https://github.com/airbytehq/airbyte/pull/39999) | Update dependencies |
| 1.0.4 | 2024-06-06 | [39263](https://github.com/airbytehq/airbyte/pull/39263) | [autopull] Upgrade base image to v1.2.2 |
| 1.0.3 | 2024-04-30 | [37598](https://github.com/airbytehq/airbyte/pull/37598) | Changed last records to last record |
| 1.0.2 | 2023-10-13 | [31205](https://github.com/airbytehq/airbyte/pull/31205) | Improve spec description for board ids |
| 1.0.1 | 2023-10-13 | [31168](https://github.com/airbytehq/airbyte/pull/31168) | Fix `cards` schema |
| 1.0.0 | 2023-09-08 | [29876](https://github.com/airbytehq/airbyte/pull/29876) | Migrate to Low Code CDK |
| 0.3.4 | 2023-07-31 | [28734](https://github.com/airbytehq/airbyte/pull/28734) | Updated `expected records` for CAT test and fixed `advancedAuth` broken references |
| 0.3.3 | 2023-06-19 | [27470](https://github.com/airbytehq/airbyte/pull/27470) | Update Organizations schema |
| 0.3.2 | 2023-05-05 | [25870](https://github.com/airbytehq/airbyte/pull/25870) | Added `CDK typeTransformer` to guarantee JSON schema types |
| 0.3.1 | 2023-03-21 | [24266](https://github.com/airbytehq/airbyte/pull/24266) | Get board ids also from organizations |
| 0.3.0 | 2023-03-17 | [24141](https://github.com/airbytehq/airbyte/pull/24141) | Certify to Beta |
| 0.2.0 | 2023-03-15 | [24045](https://github.com/airbytehq/airbyte/pull/24045) | Fix schema for boards and cards streams |
| 0.1.6 | 2021-12-28 | [8628](https://github.com/airbytehq/airbyte/pull/8628) | Updated fields in source-connector specifications |
| 0.1.3 | 2021-11-25 | [8183](https://github.com/airbytehq/airbyte/pull/8183) | Enable specifying board ids in configuration |
| 0.1.2 | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499) | Remove base-python dependencies |
| 0.1.1 | 2021-10-12 | [6968](https://github.com/airbytehq/airbyte/pull/6968) | Add oAuth flow support |
| 0.1.0 | 2021-08-18 | [5501](https://github.com/airbytehq/airbyte/pull/5501) | Release Trello CDK Connector |

</details>
