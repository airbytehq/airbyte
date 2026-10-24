# GitHub (Experimental, Gen 2)

:::warning Experimental connector
This connector is experimental and intended for internal Airbyte use only. It's available only in Airbyte Cloud workspaces that have been explicitly granted access, and it isn't available in Airbyte Open Source. It may be removed or folded into the main [GitHub](https://docs.airbyte.com/integrations/sources/github) source in the future.
:::

<HideInUI>

This page contains the setup guide and reference information for the [GitHub (Experimental, Gen 2)](https://www.github.com) source connector. GitHub (Experimental, Gen 2) is a fork of the GitHub source connector that emits flat, strongly typed columns instead of nested objects. See [Output shape](#output-shape).

</HideInUI>

## Prerequisites

- A list of the GitHub repositories or organizations you want to sync, and access to them if they're private.
- One of the following authentication methods:
  - OAuth: sign in to the GitHub account that has access to those repositories.
  - One or more [personal access tokens](https://github.com/settings/tokens). See [Permissions and scopes](#permissions-and-scopes).

## Setup guide

1. In Airbyte Cloud, click **Sources**, then click **+ New source**.
2. Select **GitHub (Experimental, Gen 2)**.
3. Enter a name for the connector.
4. To authenticate, choose one of the following:
   - **OAuth**: Click **Authenticate your GitHub account**. Airbyte authenticates the GitHub account you're signed in to in your browser, so make sure it's the right account.
   - **Personal Access Token**: Enter a GitHub personal access token. To spread API quota consumption across multiple tokens, enter several tokens separated by commas (`,`).
5. **GitHub Repositories**: Add one entry per repository or organization:
   - `airbytehq/airbyte` syncs a single repository.
   - `airbytehq/*` syncs every repository in the `airbytehq` organization.
   - `airbytehq/a*` syncs every repository in the `airbytehq` organization whose name starts with `a`.

   :::caution
   A repository that doesn't exist, has the wrong name, or that your credentials can't access is skipped, and the connector logs a message. If none of the configured entries resolve to a repository, the connection test fails.
   :::

6. **Start date** (optional): The date from which to replicate data, in the format `YYYY-MM-DDTHH:mm:ssZ`, for example `2021-03-01T00:00:00Z`. If you leave it empty, the connector syncs all available data.

   - These streams only sync records generated on or after the start date: `comments`, `commit_comment_reactions`, `commit_comments`, `commits`, `deployments`, `events`, `issue_comment_reactions`, `issue_events`, `issue_milestones`, `issue_reactions`, `issues`, `project_cards`, `project_columns`, `projects`, `projects_v2`, `pull_request_comment_reactions`, `pull_request_stats`, `pull_requests`, `releases`, `repositories`, `review_comments`, `reviews`, `stargazers`, `workflow_jobs`, `workflow_runs`, `workflows`.
   - The start date doesn't filter these streams, because the GitHub API doesn't return a date the connector can filter on: `assignees`, `branches`, `collaborators`, `contributor_activity`, `issue_labels`, `issue_timeline_events`, `organizations`, `pull_request_commits`, `tags`, `team_members`, `team_memberships`, `teams`, `users`.
   - `pull_request_commits` and `issue_timeline_events` are read for each pull request or issue returned by the `pull_requests` or `issues` stream, so they only cover pull requests and issues updated on or after the start date.

7. **Branches** (optional): The repository branches to pull commits from, one entry per branch, in the format `owner/repository/branch`, for example `airbytehq/airbyte/master`. For a repository with no branches listed, or whose listed branches don't exist, the connector pulls commits from the default branch.
8. **API URL** (optional): If you use GitHub Enterprise Server, enter its URL, for example `https://github.company.org` or `https://github.company.org/api/v3/`. The URL must use `https`. Leave it empty to use `https://api.github.com/`.
9. **Max Waiting Time (in minutes)** (optional): The maximum time the connector waits when every configured token is rate-limited before it fails the sync. The default is 120 minutes, which covers GitHub's 60-minute rate limit reset window plus margin. You can set any value between 1 and 240 minutes. If you provide multiple personal access tokens, the connector rotates through them first and only waits after every token is exhausted.
10. **Number of Concurrent Threads** (optional): How many partitions the connector reads in parallel. The default is 4 and the maximum is 25. Raising this value may speed up syncs, but increases the risk of hitting GitHub's secondary rate limits.
11. Click **Set up source**.

## Output shape

Every stream emits flat records. Each column is a scalar or an array of scalars, and the connector drops any field the stream's schema doesn't declare.

- Nested value objects become prefixed columns. For example, the pull request's `head.sha` becomes `head_sha`.
- Embedded GitHub entities become identity columns. For example, the pull request author becomes `user_id`, `user_login`, and `user_type`, and the base repository becomes `base_repo_id` and `base_repo_full_name`.
- Lists of references become arrays of scalars, for example `label_ids`, `label_names`, and `assignee_logins`.
- The connector doesn't emit arrays of multi-field objects. Version 0.2.0 removed the `release_assets`, `workflow_job_steps`, and `contributor_activity_weeks` child streams that earlier versions used for them:
  - `releases` emits asset download URLs in `asset_download_urls`, but no other asset metadata. See [Release assets](#release-assets).
  - `workflow_jobs` emits job-level columns such as `status`, `conclusion`, `started_at`, and `completed_at`, but not the job's steps.
  - `contributor_activity` emits each contributor's `total` commit count, but not weekly additions, deletions, or commit counts.
- `issue_timeline_events` emits one flat record per timeline event.
- `events.payload` and `deployments.payload` are the only columns that contain opaque JSON, because GitHub doesn't return those fields in a stable shape.

<HideInUI>

## Supported sync modes

The GitHub (Experimental, Gen 2) source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental Sync - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported streams

This connector outputs the following full refresh streams:

- [Assignees](https://docs.github.com/en/rest/issues/assignees?apiVersion=2022-11-28#list-assignees)
- [Branches](https://docs.github.com/en/rest/branches/branches?apiVersion=2022-11-28#list-branches)
- [Collaborators](https://docs.github.com/en/rest/collaborators/collaborators?apiVersion=2022-11-28#list-repository-collaborators)
- [Contributor activity](https://docs.github.com/en/rest/metrics/statistics?apiVersion=2022-11-28#get-all-contributor-commit-activity)
- [Issue labels](https://docs.github.com/en/rest/issues/labels?apiVersion=2022-11-28#list-labels-for-a-repository)
- [Issue timeline events](https://docs.github.com/en/rest/issues/timeline?apiVersion=2022-11-28#list-timeline-events-for-an-issue)
- [Organizations](https://docs.github.com/en/rest/orgs/orgs?apiVersion=2022-11-28#get-an-organization)
- [Pull request commits](https://docs.github.com/en/rest/pulls/pulls?apiVersion=2022-11-28#list-commits-on-a-pull-request)
- [Tags](https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-repository-tags)
- [Team members](https://docs.github.com/en/rest/teams/members?apiVersion=2022-11-28#list-team-members)
- [Team memberships](https://docs.github.com/en/rest/teams/members?apiVersion=2022-11-28#get-team-membership-for-a-user)
- [Teams](https://docs.github.com/en/rest/teams/teams?apiVersion=2022-11-28#list-teams)
- [Users](https://docs.github.com/en/rest/orgs/members?apiVersion=2022-11-28#list-organization-members)

This connector outputs the following incremental streams:

- [Comments](https://docs.github.com/en/rest/issues/comments?apiVersion=2022-11-28#list-issue-comments-for-a-repository)
- [Commit comment reactions](https://docs.github.com/en/rest/reactions/reactions?apiVersion=2022-11-28#list-reactions-for-a-commit-comment)
- [Commit comments](https://docs.github.com/en/rest/commits/comments?apiVersion=2022-11-28#list-commit-comments-for-a-repository)
- [Commits](https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#list-commits)
- [Deployments](https://docs.github.com/en/rest/deployments/deployments?apiVersion=2022-11-28#list-deployments)
- [Events](https://docs.github.com/en/rest/activity/events?apiVersion=2022-11-28#list-repository-events)
- [Issue comment reactions](https://docs.github.com/en/rest/reactions/reactions?apiVersion=2022-11-28#list-reactions-for-an-issue-comment)
- [Issue events](https://docs.github.com/en/rest/issues/events?apiVersion=2022-11-28#list-issue-events-for-a-repository)
- [Issue milestones](https://docs.github.com/en/rest/issues/milestones?apiVersion=2022-11-28#list-milestones)
- [Issue reactions](https://docs.github.com/en/graphql/reference/objects#reaction)
- [Issues](https://docs.github.com/en/rest/issues/issues?apiVersion=2022-11-28#list-repository-issues)
- [Project (Classic) cards](https://docs.github.com/en/rest/projects/cards?apiVersion=2022-11-28#list-project-cards)
- [Project (Classic) columns](https://docs.github.com/en/rest/projects/columns?apiVersion=2022-11-28#list-project-columns)
- [Projects (Classic)](https://docs.github.com/en/rest/projects/projects?apiVersion=2022-11-28#list-repository-projects)
- [Projects V2](https://docs.github.com/en/graphql/reference/objects#projectv2)
- [Pull request comment reactions](https://docs.github.com/en/graphql/reference/objects#reaction)
- [Pull request stats](https://docs.github.com/en/graphql/reference/objects#pullrequest)
- [Pull requests](https://docs.github.com/en/rest/pulls/pulls?apiVersion=2022-11-28#list-pull-requests)
- [Releases](https://docs.github.com/en/graphql/reference/objects#release)
- [Repositories](https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-organization-repositories)
- [Review comments](https://docs.github.com/en/rest/pulls/comments?apiVersion=2022-11-28#list-review-comments-in-a-repository)
- [Reviews](https://docs.github.com/en/graphql/reference/objects#pullrequestreview)
- [Stargazers](https://docs.github.com/en/rest/activity/starring?apiVersion=2022-11-28#list-stargazers)
- [Workflow jobs](https://docs.github.com/en/rest/actions/workflow-jobs?apiVersion=2022-11-28#list-jobs-for-a-workflow-run)
- [Workflow runs](https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28#list-workflow-runs-for-a-repository)
- [Workflows](https://docs.github.com/en/rest/actions/workflows?apiVersion=2022-11-28#list-repository-workflows)

### How incremental streams read data

Incremental streams differ in how much data they request from GitHub on each sync, which affects your API rate limit consumption:

- `comments`, `commits`, `issues`, and `review_comments` ask GitHub only for records updated since the last sync.
- `repositories`, `pull_requests`, `issue_milestones`, `pull_request_stats`, and `releases` read records newest first and stop paginating at the first record older than the last sync.
- `workflow_runs` reads runs newest first and stops at the first run created more than 32 days before the last sync. GitHub lets you [re-run a workflow](https://docs.github.com/en/actions/managing-workflow-runs/re-running-workflows-and-jobs) up to 30 days after the initial run, so older runs can still change. `workflow_jobs` is read for each run that `workflow_runs` returns.
- The remaining incremental streams read every record on each sync and emit only the records that are new since the last sync.

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Limitations and troubleshooting

<details>
<summary>
Expand to see details about GitHub (Experimental, Gen 2) connector limitations and troubleshooting.
</summary>

### Connector limitations

#### Rate limiting

Requests made with a personal access token or an OAuth app count toward your personal rate limit of 5,000 requests per hour, or 15,000 requests per hour if the app is owned by a GitHub Enterprise Cloud organization.

:::info
REST API and GraphQL API rate limits are counted separately. The REST API uses a request-based limit, while the GraphQL API uses a [point-based limit](https://docs.github.com/en/graphql/overview/rate-limits-and-node-limits-for-the-graphql-api) where each query costs a calculated number of points. These streams use the GraphQL API: `issue_reactions`, `projects_v2`, `pull_request_comment_reactions`, `pull_request_stats`, `releases`, and `reviews`.
:::

:::tip
If you reach the limits before all streams have been read, try the following:

1. Use an incremental sync mode.
2. Sync less often.
3. Split the sync into separate connections with fewer streams each.
4. Provide multiple personal access tokens, separated by commas. The connector rotates through all tokens and only waits once every token's rate limit is exhausted.

:::

When every configured token is rate-limited, the connector waits for the limit to reset instead of failing immediately. The **Max Waiting Time (in minutes)** option caps the wait, both when the connector already knows its tokens are spent and when GitHub rejects a request and asks it to wait. If the connector exceeds this wait, it reports a transient error, and Airbyte retries the sync according to your connection's retry behavior. If you supply several tokens, a rate-limited request switches to another token instead of waiting.

**Test connection** caps the wait at 1 minute regardless of your **Max Waiting Time** setting, so a rate-limited token fails the test quickly instead of leaving the setup page waiting.

Refer to GitHub article [Rate limits for the REST API](https://docs.github.com/en/rest/overview/rate-limits-for-the-rest-api).

#### Adding repositories or organizations to an existing connection

Adding entries to the **GitHub Repositories** field on a connection that has already synced doesn't backfill the history of the new repositories or organizations. Incremental streams keep one sync position per repository, organization, or parent record, and a newly added one starts from the stream's current overall position instead of from your configured **Start date**. Records created or last updated before that position aren't emitted, and the sync reports no warning or error.

For example, if a connection has synced `docker/*` since 2026-01-01 and you add `airbytehq/*`, the next sync picks up `airbytehq` records updated after the stream's current position, but not older ones.

To pull the full history of a newly added repository or organization, clear the affected streams, or refresh the connection, after saving the new value, then sync.

#### GitHub Enterprise Server with rate limiting disabled

GitHub Enterprise Server ships with HTTP API rate limiting turned off, and an instance in that state answers `GET /rate_limit` with `404 Rate limiting is not enabled.`. The connector treats this as an instance that doesn't track quotas and continues without quota tracking. Requests are still authenticated, multiple tokens are still used in turn, and the connector still honors any rate limiting the instance does enforce, such as secondary rate limits, through its usual retry and backoff.

#### Release assets

The `releases.asset_download_urls` column contains up to 100 asset download URLs per release. If a release has more than 100 assets, the connector emits the first 100 and logs a warning naming the release. The connector doesn't emit other asset metadata, such as asset name, size, content type, or download count.

#### Stargazers stream requires admin or collaborator access

Since July 2026, GitHub only lists a repository's stargazers to the repository's admins and collaborators ([GitHub changelog](https://github.blog/changelog/2026-06-30-upcoming-access-restrictions-to-public-api-endpoints-and-ui-views/)). For a repository where the authenticated user or app is neither, GitHub answers the stargazers listing with `404` or `403`. The connector skips that repository for the `stargazers` stream only and logs a message naming the repository and this restriction. The sync still succeeds, and the other streams for that repository are unaffected. Expect the `stargazers` stream to be empty for public or third-party repositories you don't collaborate on. The aggregate star count is still available in the `stargazers_count` column of the `repositories` stream.

#### Unreadable repositories and repeated server errors

When a repository can't be read for a reason specific to that repository, the connector logs a message and moves on to the next one, so a single bad repository doesn't fail the whole stream. This covers a repository that was deleted or renamed (`404`), one your token can't access (`403`), one with no commits yet (`409`), and one where the feature backing the stream is turned off, for example the `issue_labels` stream on a repository with Issues disabled (`410`). A `404` or `409` is skipped on the first response, without a retry.

If GitHub keeps answering `502 Bad Gateway` or `504 Gateway Timeout` after the connector has retried, the stream fails instead of skipping the affected repository or organization.

A failed attempt doesn't resume part-way through a stream. The retry restarts the stream from the first repository or organization. Nothing is lost, but a stream that fails late uses its earlier partitions' requests against your rate limit again.

#### `contributor_activity` fails after five `202` responses

GitHub answers `202 Accepted` on the contributor statistics endpoint while it computes the statistics. The connector retries five times, 90 seconds apart. If GitHub is still computing after that, the stream fails.

#### Incremental syncs re-emit one boundary record

Each incremental sync re-emits the record whose cursor value equals the position the previous sync stopped at, once per repository or parent record. The record is unchanged. Destinations using **Incremental | Append + Deduped** collapse it on the primary key. With **Incremental | Append**, expect one duplicate row per repository or parent record per sync.

#### Permissions and scopes

If you use OAuth, the OAuth app requests these [scopes](https://docs.github.com/en/developers/apps/building-oauth-apps/scopes-for-oauth-apps#available-scopes): `repo`, `read:org`, `read:repo_hook`, `read:user`, `read:discussion`, `read:project`, and `workflow`. For a [personal access token](https://github.com/settings/tokens), select the scopes yourself.

Your token needs at least the `repo` scope. Depending on which streams you sync, the user who generates the token needs more permissions:

- To sync `collaborators`, the user who generates the personal access token must be a collaborator on the repository. To become a collaborator, an owner must invite them. If there are no collaborators, no records are synced. Read more about [GitHub access permissions](https://docs.github.com/en/get-started/learning-about-github/access-permissions-on-github).
- [Teams](https://docs.github.com/en/organizations/organizing-members-into-teams/about-teams) are only available to authenticated members of the team's [organization](https://docs.github.com/en/rest/orgs). [Personal user accounts](https://docs.github.com/en/get-started/learning-about-github/types-of-github-accounts) and repositories that belong to them don't have Teams, so the `teams` stream syncs no records for them.
- To sync the `projects` stream, the repository must have the Projects feature enabled.

### Troubleshooting

- See common troubleshooting issues for the GitHub source connector in [GitHub Discussions](https://github.com/airbytehq/airbyte/discussions).

</details>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :----------- | :----------- | :------------------------------------------------------------------------------------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0.2.0 | 2026-10-24 | [89750](https://github.com/airbytehq/airbyte/pull/89750) | Remove the `workflow_job_steps`, `release_assets`, and `contributor_activity_weeks` streams; add `releases.asset_download_urls` |
| 0.1.2 | 2026-10-24 | [89749](https://github.com/airbytehq/airbyte/pull/89749) | Declare `workflow_runs.pull_request_ids` and `pull_request_numbers` items as integers |
| 0.1.1 | 2026-10-20 | [89588](https://github.com/airbytehq/airbyte/pull/89588) | Rename display name to GitHub (Experimental, Gen 2) |
| 0.1.0 | 2026-10-20 | [89566](https://github.com/airbytehq/airbyte/pull/89566) | Initial release, forked from source-github 2.7.9 |

</details>

</HideInUI>
