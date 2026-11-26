# CircleCI

This page contains the setup guide and reference information for the [CircleCI](https://circleci.com/) source connector.

The connector reads data about your CircleCI organization, a single project in that organization, and the pipelines, workflows, and jobs in that project. It uses the [CircleCI API v2](https://circleci.com/docs/api/v2/index.html) for most streams and the [CircleCI API v1.1](https://circleci.com/docs/api/v1/index.html) for the `me` and `projects` streams.

## Prerequisites

- A CircleCI account with access to the organization and project you want to sync.
- A CircleCI personal API token.
- An organization and project that use the `circleci` project slug format, `circleci/<organization ID>/<project ID>`. CircleCI uses this format for organizations connected through the GitHub App, GitLab, or Bitbucket Data Center. The connector builds every organization- and project-scoped request with this prefix, so projects identified by `gh/<org>/<repo>` or `bb/<org>/<repo>` slugs aren't supported.

## Setup guide

### Step 1: Create a CircleCI personal API token

1. In CircleCI, open **User Settings** > [**Personal API Tokens**](https://app.circleci.com/settings/user/tokens).
2. Click **Create New Token**, give the token a name, and click **Add API Token**.
3. Copy the token. CircleCI shows it only once.

The token has the same access as the user who created it. For details, see [Managing API tokens](https://circleci.com/docs/managing-api-tokens/).

### Step 2: Find your organization ID and project ID

1. In CircleCI, open **Organization Settings** > **Overview**. Copy the **Organization ID**. The URL of this page has the form `https://app.circleci.com/settings/organization/circleci/<organization ID>/overview`.
2. Open the project, then click **Project Settings** > **Overview**. Copy the **Project ID**. The URL of this page has the form `https://app.circleci.com/settings/project/circleci/<organization ID>/<project ID>`.

### Step 3: Optional: Find workflow IDs

The `workflow`, `workflow_jobs`, and `jobs` streams read only the workflows you list in the **Workflow ID** field. To find a workflow ID, open a pipeline run in CircleCI and click a workflow. The ID is the last segment of the URL, for example `https://app.circleci.com/pipelines/circleci/<organization ID>/<project ID>/2/workflows/<workflow ID>`.

### Step 4: Set up the connector in Airbyte

1. In Airbyte, go to **Sources** and click **New source**.
2. Select **CircleCI**.
3. Enter the following values:
   - **API Key**: The personal API token from Step 1.
   - **Organization ID**: The organization ID from Step 2.
   - **Start date**: The earliest record creation date to sync, in the format `YYYY-MM-DDTHH:MM:SSZ`. Incremental streams don't sync records created before this date.
   - **Project ID**: The project ID from Step 2.
   - **Workflow ID**: Optional. One or more workflow IDs from Step 3. If you leave this empty, the `workflow`, `workflow_jobs`, and `jobs` streams return no records.
   - **Job Number**: Optional. A job number in the project to read in the `jobs` stream. The field is pre-filled with `2`. If you clear it, the connector reads every job returned by the `workflow_jobs` stream instead.
4. Click **Set up source**.

## Supported sync modes

The CircleCI source connector supports the following sync modes:

- [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite)
- [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped)

## Supported streams

| Stream | Description | Primary key | Incremental (cursor) |
|--------|-------------|-------------|----------------------|
| `context` | Contexts in the organization. | `id` | Yes (`created_at`) |
| `self_ids` | Information about the user who owns the API token. | `id` | No |
| `self_collaborations` | Organizations the token owner is a member of. | `id` | No |
| `me` | Information about the token owner from API v1.1. | `analytics_id` | Yes (`created_at`) |
| `projects` | Projects the token owner follows, from API v1.1. | `vcs_url` | No |
| `pipelines` | Pipelines in the organization. | `id` | Yes (`created_at`) |
| `specific_project` | Details of the configured project. | `id` | No |
| `workflow` | Details of each configured workflow. | `id` | Yes (`created_at`) |
| `workflow_jobs` | Jobs in each configured workflow. | `id` | Yes (`started_at`) |
| `jobs` | Details of a job in the configured project. | `number` | No |
| `insights_metrics` | Summary Insights metrics for the configured project. | `project_id` | No |
| `insights_branches` | Branches of the configured project that have Insights data. | `project_id` | No |

## Limitations and troubleshooting

- **Rate limits**: CircleCI rate limits API requests. When CircleCI returns HTTP `429`, the connector retries the request with exponential backoff.
- **Single project**: Each source reads one project. To sync more projects, create one source per project.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       |PR| Subject        |
|------------------|------------|---|----------------|
| 0.1.2 | 2026-11-11 |[91328](https://github.com/airbytehq/airbyte/pull/91328)| Upgrade base image to source-declarative-manifest 7.47.0 |
| 0.1.0 | 2024-10-11 |[46729](https://github.com/airbytehq/airbyte/pull/46729)| Remove unwanted optional config parameters |
| 0.0.1 | 2024-09-29 |[46249](https://github.com/airbytehq/airbyte/pull/46249)| Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>
