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
8. **Trello Board IDs (Optional)** - IDs of the boards to replicate data from. If left empty, data from all boards to which you have access will be replicated.
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

1. Authenticate with **API Key** and **API Token** pair.
<!-- /env:oss -->

## Supported sync modes

The Trello source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)

## Supported Streams

This connector outputs the following streams:

* [Boards](https://developer.atlassian.com/cloud/trello/rest/api-group-members/#api-members-id-boards-get) \(Full Refresh\)
  * [Actions](https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-boardid-actions-get) \(Incremental\)
  * [Cards](https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-cards-get) \(Full Refresh\)
  * [Checklists](https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-checklists-get) \(Full Refresh\)
  * [Lists](https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-lists-get) \(Full Refresh\)
  * [Users](https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-members-get) \(Full Refresh\)
  * [Organizations](https://developer.atlassian.com/cloud/trello/rest/api-group-members/#api-members-id-organizations-get) \(Full Refresh\)

### Performance considerations

The connector is restricted by normal Trello [requests limitation](https://developer.atlassian.com/cloud/trello/guides/rest-api/rate-limits/).

The Trello connector should not run into Trello API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.3.2 | 2023-05-05 | [25870](https://github.com/airbytehq/airbyte/pull/25870) | Added `CDK typeTransformer` to guarantee JSON schema types |
| 0.3.1 | 2023-03-21 | [24266](https://github.com/airbytehq/airbyte/pull/24266) | Get board ids also from organizations |
| 0.3.0 | 2023-03-17 | [24141](https://github.com/airbytehq/airbyte/pull/24141) | Certify to Beta |
| 0.2.0 | 2023-03-15 | [24045](https://github.com/airbytehq/airbyte/pull/24045) | Fix schema for boards and cards streams |
| 0.1.6 | 2021-12-28 | [8628](https://github.com/airbytehq/airbyte/pull/8628) | Updated fields in source-connector specifications |
| 0.1.3 | 2021-11-25 | [8183](https://github.com/airbytehq/airbyte/pull/8183) | Enable specifying board ids in configuration |
| 0.1.2 | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499) | Remove base-python dependencies |
| 0.1.1 | 2021-10-12 | [6968](https://github.com/airbytehq/airbyte/pull/6968) | Add oAuth flow support |
| 0.1.0 | 2021-08-18 | [5501](https://github.com/airbytehq/airbyte/pull/5501) | Release Trello CDK Connector |
