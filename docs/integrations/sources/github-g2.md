# GitHub (Experimental, Gen 2)

:::warning Experimental connector
This connector is experimental and intended for internal Airbyte use only. It is not publicly listed and may be removed or folded into the main GitHub source in the future.
:::

<HideInUI>

This page contains the setup guide and reference information for the [GitHub (Experimental, Gen 2)](https://www.github.com) source connector.

</HideInUI>

## Prerequisites

- List of GitHub Repositories (and access for them in case they are private)

<!-- env:cloud -->

**For Airbyte Cloud:**

- OAuth
- Personal Access Token (see [Permissions and scopes](https://docs.airbyte.com/integrations/sources/github-g2#permissions-and-scopes))
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

- Personal Access Token (see [Permissions and scopes](https://docs.airbyte.com/integrations/sources/github-g2#permissions-and-scopes))
<!-- /env:oss -->

## Setup guide

### Step 1: Set up GitHub

Create a [GitHub Account](https://github.com).

<!-- env:oss -->

#### Airbyte Open Source additional setup steps

Log into [GitHub](https://github.com) and then generate a [personal access token](https://github.com/settings/tokens). To load balance your API quota consumption across multiple API tokens, input multiple tokens separated with `,`.

<!-- /env:oss -->

### Step 2: Set up the GitHub connector in Airbyte

<!-- env:cloud -->

#### For Airbyte Cloud

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click Sources and then click + New source.
3. On the Set up the source page, select GitHub from the Source type dropdown.
4. Enter a name for the GitHub connector.
5. To authenticate:
   <!-- env:cloud -->

   - **For Airbyte Cloud:** **Authenticate your GitHub account** to authorize your GitHub account. Airbyte will authenticate the GitHub account you are already logged in to. Please make sure you are logged into the right account.
   <!-- /env:cloud -->
   <!-- env:oss -->

   - **For Airbyte Open Source:** Authenticate with **Personal Access Token**. To generate a personal access token, log into [GitHub](https://github.com) and then generate a [personal access token](https://github.com/settings/tokens). Enter your GitHub personal access token. To load balance your API quota consumption across multiple API tokens, input multiple tokens separated with `,`.
   <!-- /env:oss -->

6. **GitHub Repositories** - Enter a list of GitHub organizations/repositories, e.g. `airbytehq/airbyte` for single repository, `airbytehq/airbyte airbytehq/another-repo` for multiple repositories. If you want to specify the organization to receive data from all its repositories, then you should specify it according to the following example: `airbytehq/*`.

   :::caution
   Repositories with the wrong name or repositories that do not exist or have the wrong name format will be skipped with `WARN` message in the logs.
   :::

7. **Start date (Optional)** - The date from which you'd like to replicate data for streams. For streams which support this configuration, only data generated on or after the start date will be replicated.

   - These streams will only sync records generated on or after the **Start Date**: `comments`, `commit_comment_reactions`, `commit_comments`, `commits`, `deployments`, `events`, `issue_comment_reactions`, `issue_events`, `issue_milestones`, `issue_reactions`, `issues`, `project_cards`, `project_columns`, `projects`, `pull_request_comment_reactions`, `pull_requests`, `pull_request_stats`, `releases`, `review_comments`, `reviews`, `stargazers`, `workflow_runs`, `workflows`.

   - The **Start Date** does not apply to the streams below and all data will be synced for these streams: `assignees`, `branches`, `collaborators`, `issue_labels`, `organizations`, `pull_request_commits`, `repositories`, `tags`, `teams`, `users`

8. **Branch (Optional)** - List of GitHub repository branches to pull commits from, e.g. `airbytehq/airbyte/master`. If no branches are specified for a repository, the default branch will be pulled. (e.g. `airbytehq/airbyte/master airbytehq/airbyte/my-branch`).
9. **API URL (Optional)** - If you use a self-hosted GitHub instance, enter its API URL, for example `https://github.company.org`. Leave empty to use `https://api.github.com/`.
10. **Max Waiting Time (in minutes) (Optional)** - Maximum time the connector waits when every configured API token is rate-limited before it fails the sync. The default is 120 minutes, which covers GitHub's 60-minute rate limit reset window plus margin. You can set any value between 1 and 240 minutes. If you provide multiple personal access tokens, the connector rotates through them first, and only waits after every token is exhausted.

11. **Number of Concurrent Threads (Optional)** - How many partitions the connector reads in parallel. The default is 4 and the maximum is 25. All streams use the declarative manifest; raising this value may speed up syncs but increases the risk of hitting GitHub's secondary rate limits.

### For Airbyte Open Source

1. Navigate to the Airbyte Open Source dashboard.
2. Click Sources and then click + New source.
3. On the Set up the source page, select GitHub from the Source type dropdown.
4. Enter a name for the GitHub connector.

## Output shape

All streams emit flat records with deterministic scalar columns and arrays of scalars. Embedded GitHub identities use prefixed identity columns. Child streams are used only when their members require a separate API call; none of the current streams needs a child stream for an array available in its parent response. `events.payload` and `deployments.payload` remain opaque JSON fields under approved exemptions.

`workflow_jobs` keeps job-level `status`, `conclusion`, `started_at`, `completed_at`, and `created_at`; step names and per-step timing are not emitted. `releases.asset_download_urls` contains up to 100 asset download URLs per release; other per-asset metadata is not emitted. `contributor_activity` emits `author_id`, `author_login`, `author_type`, `repository`, and `total`, but not per-week additions, deletions, or commits.

Every field is strongly typed; values without a stable shape are opaque JSON (`payload`), never partially described objects. Every stream root uses `additionalProperties: false`; a future need for fields beyond declared columns requires a dedicated opaque JSON column kept separate from declared columns, never root `additionalProperties`, and human approval recorded in `FLATTEN_EXEMPTIONS`.

<HideInUI>

## Supported sync modes

The GitHub source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental Sync - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

This connector outputs the following full refresh streams:

- [Assignees](https://docs.github.com/en/rest/issues/assignees?apiVersion=2022-11-28#list-assignees)
- [Branches](https://docs.github.com/en/rest/branches/branches?apiVersion=2022-11-28#list-branches)
- [Contributor Activity](https://docs.github.com/en/rest/metrics/statistics?apiVersion=2022-11-28#get-all-contributor-commit-activity)
- [Collaborators](https://docs.github.com/en/rest/collaborators/collaborators?apiVersion=2022-11-28#list-repository-collaborators)
- [Issue labels](https://docs.github.com/en/rest/issues/labels?apiVersion=2022-11-28#list-labels-for-a-repository)
- [Organizations](https://docs.github.com/en/rest/orgs/orgs?apiVersion=2022-11-28#list-organizations)
- [Pull request commits](https://docs.github.com/en/rest/pulls/pulls?apiVersion=2022-11-28#list-commits-on-a-pull-request)
- [Tags](https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-repository-tags)
- [TeamMembers](https://docs.github.com/en/rest/teams/members?apiVersion=2022-11-28#list-team-members)
- [TeamMemberships](https://docs.github.com/en/rest/teams/members?apiVersion=2022-11-28#get-team-membership-for-a-user)
- [Teams](https://docs.github.com/en/rest/teams/teams?apiVersion=2022-11-28#list-teams)
- [Users](https://docs.github.com/en/rest/orgs/members?apiVersion=2022-11-28#list-organization-members)
- [Issue timeline events](https://docs.github.com/en/rest/issues/timeline?apiVersion=2022-11-28#list-timeline-events-for-an-issue)

This connector outputs the following incremental streams:

- [Comments](https://docs.github.com/en/rest/issues/comments?apiVersion=2022-11-28#list-issue-comments-for-a-repository)
- [Commit comment reactions](https://docs.github.com/en/rest/reference/reactions?apiVersion=2022-11-28#list-reactions-for-a-commit-comment)
- [Commit comments](https://docs.github.com/en/rest/commits/comments?apiVersion=2022-11-28#list-commit-comments-for-a-repository)
- [Commits](https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#list-commits)
- [Deployments](https://docs.github.com/en/rest/deployments/deployments?apiVersion=2022-11-28#list-deployments)
- [Events](https://docs.github.com/en/rest/activity/events?apiVersion=2022-11-28#list-repository-events)
- [Issue comment reactions](https://docs.github.com/en/rest/reactions/reactions?apiVersion=2022-11-28#list-reactions-for-an-issue-comment)
- [Issue events](https://docs.github.com/en/rest/issues/events?apiVersion=2022-11-28#list-issue-events-for-a-repository)
- [Issue milestones](https://docs.github.com/en/rest/issues/milestones?apiVersion=2022-11-28#list-milestones)
- [Issue reactions](https://docs.github.com/en/rest/reactions/reactions?apiVersion=2022-11-28#list-reactions-for-an-issue)
- [Issues](https://docs.github.com/en/rest/issues/issues?apiVersion=2022-11-28#list-repository-issues)
- [Project (Classic) cards](https://docs.github.com/en/rest/projects/cards?apiVersion=2022-11-28#list-project-cards)
- [Project (Classic) columns](https://docs.github.com/en/rest/projects/columns?apiVersion=2022-11-28#list-project-columns)
- [Projects (Classic)](https://docs.github.com/en/rest/projects/projects?apiVersion=2022-11-28#list-repository-projects)
- [ProjectsV2](https://docs.github.com/en/graphql/reference/objects#projectv2)
- [Pull request comment reactions](https://docs.github.com/en/rest/reactions/reactions?apiVersion=2022-11-28#list-reactions-for-a-pull-request-review-comment)
- [Pull request stats](https://docs.github.com/en/graphql/reference/objects#pullrequest)
- [Pull requests](https://docs.github.com/en/rest/pulls/pulls?apiVersion=2022-11-28#list-pull-requests)
- [Releases](https://docs.github.com/en/graphql/reference/objects#release)
- [Repositories](https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-organization-repositories)
- [Review comments](https://docs.github.com/en/rest/pulls/comments?apiVersion=2022-11-28#list-review-comments-in-a-repository)
- [Reviews](https://docs.github.com/en/rest/pulls/reviews?apiVersion=2022-11-28#list-reviews-for-a-pull-request)
- [Stargazers](https://docs.github.com/en/rest/activity/starring?apiVersion=2022-11-28#list-stargazers)
- [WorkflowJobs](https://docs.github.com/en/rest/actions/workflow-jobs?apiVersion=2022-11-28#list-jobs-for-a-workflow-run)
- [WorkflowRuns](https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28#list-workflow-runs-for-a-repository)
- [Workflows](https://docs.github.com/en/rest/actions/workflows?apiVersion=2022-11-28#list-repository-workflows)

### Entity-Relationship Diagram (ERD)

<EntityRelationshipDiagram></EntityRelationshipDiagram>

### Notes

1. Only 4 streams \(`comments`, `commits`, `issues` and `review comments`\) from the listed above streams are pure incremental meaning that they:

   - read only new records;
   - output only new records.

2. Streams `workflow_runs` and `workflow_jobs` are almost pure incremental:

   - read new records and some portion of old records (in past 30 days) [docs](https://docs.github.com/en/actions/managing-workflow-runs/re-running-workflows-and-jobs);
   - the `workflow_jobs` depends on the `workflow_runs` to read the data, so they both follow the same logic [docs](https://docs.github.com/en/rest/actions/workflow-jobs#list-jobs-for-a-workflow-run);
   - output only new records.

3. Other 19 incremental streams are also incremental but with one difference, they:

   - read all records;
   - output only new records.

   Consider this behavior when using these incremental streams, because it may affect your API call limits.

4. Sometimes for large streams specifying very distant `start_date` in the past may result in keep on getting error from GitHub instead of records \(respective `WARN` log message will be outputted\). In this case Specifying more recent `start_date` may help.
   **The "Start date" configuration option does not apply to the streams below, because the GitHub API does not include dates which can be used for filtering:**

   - `assignees`
   - `branches`
   - `collaborators`
   - `issue_labels`
   - `organizations`
   - `pull_request_commits`
   - `tags`
   - `teams`
   - `users`

5. Adding a repository or organization to a connection that has already synced does not backfill its history. See [Adding repositories or organizations to an existing connection](#adding-repositories-or-organizations-to-an-existing-connection).

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Limitations & Troubleshooting

<details>
<summary>
Expand to see details about GitHub connector limitations and troubleshooting.
</summary>

### Connector limitations

#### Rate limiting

You can use a personal access token to make API requests. Additionally, you can authorize a GitHub App or OAuth app, which can then make API requests on your behalf.
All of these requests count towards your personal rate limit of 5,000 requests per hour (15,000 requests per hour if the app is owned by a GitHub Enterprise Cloud organization).

:::info
`REST API` and `GraphQL API` rate limits are counted separately. The REST API uses a request-based limit, while the GraphQL API uses a [point-based limit](https://docs.github.com/en/graphql/overview/rate-limits-and-node-limits-for-the-graphql-api) where each query costs a calculated number of points. Streams that use the GraphQL API include `pull_request_stats`, `reviews`, `pull_request_comment_reactions`, `issue_reactions`, `releases`, and `projects_v2`.
:::

:::tip
In the event that limits are reached before all streams have been read, it is recommended to take the following actions:

1. Utilize Incremental sync mode.
2. Set a higher sync interval.
3. Divide the sync into separate connections with a smaller number of streams.
4. Provide multiple personal access tokens in the **Personal Access Tokens** field, separated by commas. The connector rotates through all tokens and only waits once every token's rate limit is exhausted.

:::

When every configured token is rate-limited, the connector waits for the limit to reset rather than failing immediately. The wait is capped by the **Max Waiting Time (in minutes)** configuration option (default: 120 minutes, maximum: 240 minutes), and that cap applies both when the connector already knows its tokens are spent and when GitHub rejects a request and asks it to wait. Rate-limit exhaustion is classified as a transient error, so Airbyte will retry the sync according to your connection's retry behavior if the connector does exceed this wait. If you supply several tokens, a rate-limited request switches to another token instead of waiting, whatever this setting is.

**Test connection** is exempt from the wait: it answers within seconds with the rate-limit message instead of sleeping, so a rate-limited token never leaves the connection setup page hanging.

Refer to GitHub article [Rate limits for the REST API](https://docs.github.com/en/rest/overview/rate-limits-for-the-rest-api).

#### Adding repositories or organizations to an existing connection

Widening the **GitHub Repositories** field on a connection that has already synced does not backfill what the new repositories or organizations did in the past. The connector keeps one sync position per repository or organization, and a newly added one starts from the connection's current overall position instead of from your configured **Start date**. Anything created or last updated before that position is never emitted, and the sync reports no warning or error.

For example, a connection syncing `docker/*` since 2026-01-01 that you widen to `docker/*, airbytehq/*` will pick up the `airbytehq` repositories updated after 2026-01-01, but not the ones whose last update is older than that.

To pull the full history of a newly added repository or organization, clear the affected streams (or refresh the connection) after saving the new value, then sync. Each stream then re-reads from the beginning of the range it supports — your configured **Start date** for streams that honor it, and everything available for the streams listed above that do not.

This currently affects the `repositories` stream. Other streams still fall back to the **Start date** for a repository they have not seen before; they will follow the rule above as they move to the connector's declarative implementation.

#### GitHub Enterprise Server with rate limiting disabled

GitHub Enterprise Server ships with HTTP API rate limiting turned off, and an instance in that state answers `GET /rate_limit` with `404 Rate limiting is not enabled.`. The connector reads that as "this instance does not track quotas" and continues without quota tracking — it no longer treats it as a failed connection. Requests are still authenticated, multiple tokens are still used in turn, and any rate limiting the instance *does* enforce (secondary rate limits are a separate GHES setting) is still honored through the usual retry and backoff.

#### Release assets

The `releases.asset_download_urls` array contains up to 100 download URLs per release. If a release has more than 100 assets, the remaining URLs are truncated and the connector logs a warning. Other asset metadata (`id`, `name`, `size`, `download_count`, `content_type`, `digest`, `label`, `state`, and uploader) is no longer emitted; keep the existing `release_assets` table if you need those values.

#### Stargazers stream requires admin or collaborator access

Since July 2026, GitHub only lists a repository's stargazers to the repository's admins and collaborators ([GitHub changelog](https://github.blog/changelog/2026-06-30-upcoming-access-restrictions-to-public-api-endpoints-and-ui-views/)). For a repository where the authenticated user or app is neither, GitHub answers the stargazers listing with `404` or `403`. The connector skips that repository for the `stargazers` stream only, logs a message naming the repository and this restriction, and the sync still succeeds; the other streams for that repository are unaffected. Expect the `stargazers` stream to be empty for public or third-party repositories you do not collaborate on. The aggregate star count is still available in the `stargazers_count` field of the `repositories` stream.

#### Unreadable repositories and repeated server errors

When a repository cannot be read for a reason that is specific to that repository, the connector logs a message and moves on to the next one, so a single bad repository does not fail the whole stream. This covers a repository that was deleted or renamed (`404`), one your token cannot access (`403`), one with no commits yet (`409`), and one where the feature backing the stream is turned off — for example the `issue_labels` stream on a repository with Issues disabled (`410`).

Repeated server errors are treated differently as of version 2.2.0. If GitHub keeps answering `502 Bad Gateway` or `504 Gateway Timeout` after the connector has retried, the stream now fails instead of skipping the affected repository or organization and continuing. Earlier versions logged a warning, skipped it, and reported the sync as successful — which meant a sync could complete with records silently missing. Affected streams so far: `repositories` (since 2.2.0), `assignees`, `branches`, `collaborators`, `issue_labels`, `tags`, `organizations`, `teams`, `users` (since 2.3.0), `events`, `pull_requests`, `commit_comments`, `issue_milestones`, `stargazers`, `projects`, `issue_events`, `deployments`, `workflows`, `comments`, `issues`, `review_comments` (since 2.4.0), `pull_request_commits`, `project_columns`, `project_cards`, `team_members`, `team_memberships`, `issue_timeline_events`, `commit_comment_reactions`, `issue_comment_reactions` (since 2.5.0), and `commits`, `contributor_activity`, `workflow_runs`, `workflow_jobs` (since 2.6.0). If a sync starts failing on one of these after upgrading, it is worth checking whether that repository or organization was already being skipped before.

The same streams also stopped resuming mid-stream. A failed attempt used to pick up from the repository or organization it stopped at; it now restarts the stream from the first one. Nothing is lost — the retry re-reads what it already read — but a stream that fails late costs its earlier partitions' requests again against your rate limit. Same versions as above. For `issues` this also means state is now saved once per repository rather than once per page, so an interrupted sync restarts the repository it was reading instead of resuming part-way through it.

#### `contributor_activity` fails after five 202 answers

GitHub answers `202 Accepted` on the contributor statistics endpoint while it computes the statistics. The connector retries five times, 90 seconds apart, as before. As of version 2.6.0 it fails the stream when GitHub is still computing after that, where earlier versions logged a message and skipped the repository with the sync reported as successful.

#### One repeated record per parent on `project_columns`, `project_cards`, `commit_comment_reactions` and `issue_comment_reactions`

As of version 2.5.0 these four streams keep their cursor per parent record (per project, column or comment) and re-emit, on each incremental sync, the one record per parent whose cursor equals the saved value, for the same reason as above. Existing connections keep their saved cursors: the nested state the previous versions wrote is converted on the first sync after upgrading. As of version 2.6.0 the same applies to `commits` (one cursor per branch), `workflow_runs` and `workflow_jobs`.

#### One repeated record per repository on `comments`, `issues` and `review_comments`

As of version 2.4.0, each incremental sync of these three streams re-emits the single record whose `updated_at` is exactly the timestamp the previous sync stopped at. GitHub's `since` filter is inclusive, so that record is always on the first page, and the connector no longer filters it out locally. The record is unchanged, and destinations using **Incremental | Append + Deduped** collapse it on the primary key; on **Incremental | Append** you will see one extra row per repository per sync.

#### One repeated record per repository on the semi-incremental streams

As of version 2.4.0, each incremental sync of `events`, `pull_requests`, `commit_comments`, `issue_milestones`, `stargazers`, `projects`, `issue_events`, `deployments`, `workflows` re-emits the single record per repository whose cursor value (`updated_at`, `created_at` or `starred_at`) is exactly the timestamp the previous sync stopped at. These streams read GitHub's listing and filter it locally; the connector used to keep only records strictly newer than the saved cursor and now keeps the boundary record too. The record is unchanged, and destinations using **Incremental | Append + Deduped** collapse it on the primary key; on **Incremental | Append** you will see one extra row per repository per sync.

Two smaller changes in the same release:

- `pull_requests` now fills `base.repo_id` with the id of the base repository. Earlier versions always emitted `null` there because of a bug in the record transformation; `head.repo_id` is unchanged.
- `pull_requests` always lists a repository newest-first. Earlier versions listed it oldest-first on the very first sync of a connection, which let a failed first sync resume part-way through a repository; a failed attempt now restarts the repository, as it already did on every later sync.

#### Permissions and scopes

If you use OAuth authentication method, the OAuth2.0 application requests the next list of [scopes](https://docs.github.com/en/developers/apps/building-oauth-apps/scopes-for-oauth-apps#available-scopes): **repo**, **read:org**, **read:repo_hook**, **read:user**, **read:discussion**, **read:project**, **workflow**. For [personal access token](https://github.com/settings/tokens) you need to manually select needed scopes.

Your token should have at least the `repo` scope. Depending on which streams you want to sync, the user generating the token needs more permissions:

- For syncing Collaborators, the user which generates the personal access token must be a collaborator. To become a collaborator, they must be invited by an owner. If there are no collaborators, no records will be synced. Read more about [GitHub access permissions](https://docs.github.com/en/get-started/learning-about-github/access-permissions-on-github).
- Syncing [Teams](https://docs.github.com/en/organizations/organizing-members-into-teams/about-teams) is only available to authenticated members of a team's [organization](https://docs.github.com/en/rest/orgs). [Personal user accounts](https://docs.github.com/en/get-started/learning-about-github/types-of-github-accounts) and repositories belonging to them don't have access to Teams features. In this case no records will be synced.
- To sync the Projects stream, the repository must have the Projects feature enabled.

### Troubleshooting

- Check out common troubleshooting issues for the GitHub source connector on our [Airbyte Forum](https://github.com/airbytehq/airbyte/discussions)

</details>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :----------- | :----------- | :------------------------------------------------------------------------------------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0.2.1 | 2026-10-27 | [89909](https://github.com/airbytehq/airbyte/pull/89909) | Update dependencies |
| 0.2.0 | 2026-10-24 | [89750](https://github.com/airbytehq/airbyte/pull/89750) | Drop workflow_job_steps and contributor_activity_weeks data; replace release_assets with download URLs |
| 0.1.2 | 2026-10-24 | [89749](https://github.com/airbytehq/airbyte/pull/89749) | Declare `workflow_runs.pull_request_ids` and `pull_request_numbers` items as integers |
| 0.1.1 | 2026-10-20 | [89588](https://github.com/airbytehq/airbyte/pull/89588) | Rename display name to GitHub (Experimental, Gen 2) |
| 0.1.0 | 2026-10-20 | - | Initial release, forked from source-github 2.7.9 |

</details>

</HideInUI>
