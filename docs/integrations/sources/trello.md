# Trello

This page contains the setup guide and reference information for the [Trello](https://trello.com) source connector.

## Prerequisites

- A [Trello account](https://trello.com) with access to the boards you want to sync.
- A start date for the data you want to replicate.
- (Optional) The IDs of the specific boards you want to sync.

<!-- env:cloud -->

**For Airbyte Cloud:**

- Permission to authorize Airbyte to access your Trello account through OAuth.
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

- A Trello API key and API token. To generate an API key, you must first create a Trello Power-Up. See [Obtain an API key and token](#obtain-an-api-key-and-token-airbyte-open-source).
<!-- /env:oss -->

## Setup guide

<!-- env:oss -->

### Obtain an API key and token (Airbyte Open Source)

1. If you don't have a Trello Power-Up yet, create one. See Trello's [Managing your API key](https://developer.atlassian.com/cloud/trello/guides/rest-api/api-introduction/#managing-your-api-key) documentation.
2. Go to the [Power-Up admin page](https://trello.com/apps/admin) and select your Power-Up.
3. Open the **Trello Auth** tab and click **Generate a new API key**. Copy the API key.
4. On the same page, click the **Token** link next to your API key. Review the permissions and click **Allow**.
5. Copy the API token from the page Trello redirects you to. Treat this token as a secret, because it grants access to your Trello account.

<!-- /env:oss -->

### Find your board IDs (optional)

The **Trello Board IDs** field requires the 24-character board ID that the Trello API returns. It doesn't accept the 8-character short ID that appears in a board's URL. To list the IDs of all boards your account can access, call the Trello API with your API key and token:

```bash
curl 'https://api.trello.com/1/members/me/boards?fields=name,id&key={yourKey}&token={yourToken}'
```

### Set up the Trello connector in Airbyte

<!-- env:cloud -->

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Select **Trello** from the list of sources and enter a name for this connector.
4. Click **Authenticate your Trello account**.
5. Log in to Trello and click **Allow**.
6. For **Start Date**, enter the UTC date and time in the format `YYYY-MM-DDTHH:MM:SSZ`, for example `2021-03-01T00:00:00Z`.
7. (Optional) For **Trello Board IDs**, enter the IDs of the boards you want to sync. If you leave this field empty, the connector syncs all boards you have access to.
8. Click **Set up source**.
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
2. Select **Trello** from the list of sources and enter a name for this connector.
3. For **API key** and **API token**, enter the values you obtained from Trello.
4. For **Start Date**, enter the UTC date and time in the format `YYYY-MM-DDTHH:MM:SSZ`, for example `2021-03-01T00:00:00Z`.
5. (Optional) For **Trello Board IDs**, enter the IDs of the boards you want to sync. If you leave this field empty, the connector syncs all boards you have access to.
6. Click **Set up source**.
<!-- /env:oss -->

## Supported sync modes

The Trello source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)

## Supported streams

| Stream | Endpoint | Sync modes |
| :----- | :------- | :--------- |
| Boards | [`GET /members/me/boards`](https://developer.atlassian.com/cloud/trello/rest/api-group-members/#api-members-id-boards-get) | Full Refresh |
| Organizations | [`GET /members/me/organizations`](https://developer.atlassian.com/cloud/trello/rest/api-group-members/#api-members-id-organizations-get) | Full Refresh |
| Actions | [`GET /boards/{id}/actions`](https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-boardid-actions-get) | Full Refresh, Incremental |
| Cards | [`GET /boards/{id}/cards/all`](https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-cards-filter-get) | Full Refresh |
| Checklists | [`GET /boards/{id}/checklists`](https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-checklists-get) | Full Refresh |
| Lists | [`GET /boards/{id}/lists`](https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-lists-get) | Full Refresh |
| Users | [`GET /boards/{id}/members`](https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-members-get) | Full Refresh |

The Actions stream syncs incrementally using the `date` cursor field, starting from the configured start date.

### Board selection

The Actions, Cards, Checklists, Lists, and Users streams read data board by board. The connector determines which boards to read as follows:

- If you set **Trello Board IDs**, the connector reads only those boards. The Boards stream also only returns those boards. The Organizations stream isn't filtered and returns all Workspaces you belong to.
- If you leave **Trello Board IDs** empty, the connector reads every board returned by the Boards stream, plus every board listed in the Workspaces returned by the Organizations stream. Each board is read once, even if it appears in both.

## Limitations and troubleshooting

Trello [limits API requests](https://developer.atlassian.com/cloud/trello/guides/rest-api/rate-limits/) to 300 requests per 10 seconds for each API key and 100 requests per 10 seconds for each token. Requests to `/1/members/` endpoints are limited to 100 requests per 900 seconds. When Trello returns a rate limit error, the connector waits 10 seconds and retries the request.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                            |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------------------------------------- |
| 1.3.11 | 2026-11-13 | [91444](https://github.com/airbytehq/airbyte/pull/91444) | Upgrade to CDK 7 and update the board partition router to read parent streams through the CDK 7 partition API |
| 1.3.10 | 2025-08-24 | [65474](https://github.com/airbytehq/airbyte/pull/65474) | Update dependencies |
| 1.3.9 | 2025-08-10 | [64813](https://github.com/airbytehq/airbyte/pull/64813) | Update dependencies |
| 1.3.8 | 2025-08-02 | [64394](https://github.com/airbytehq/airbyte/pull/64394) | Update dependencies |
| 1.3.7 | 2025-07-27 | [64086](https://github.com/airbytehq/airbyte/pull/64086) | Update dependencies |
| 1.3.6 | 2025-07-20 | [63680](https://github.com/airbytehq/airbyte/pull/63680) | Update dependencies |
| 1.3.5 | 2025-07-12 | [63204](https://github.com/airbytehq/airbyte/pull/63204) | Update dependencies |
| 1.3.4 | 2025-07-05 | [62668](https://github.com/airbytehq/airbyte/pull/62668) | Update dependencies |
| 1.3.3 | 2025-06-28 | [62283](https://github.com/airbytehq/airbyte/pull/62283) | Update dependencies |
| 1.3.2 | 2025-06-21 | [61828](https://github.com/airbytehq/airbyte/pull/61828) | Update dependencies |
| 1.3.1 | 2025-06-14 | [48153](https://github.com/airbytehq/airbyte/pull/48153) | Update dependencies |
| 1.3.0 | 2024-01-02 | [50853](https://github.com/airbytehq/airbyte/pull/50853) | Restrore unit tests |
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
