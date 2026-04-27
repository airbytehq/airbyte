# Contributing to source-github

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The GitHub REST and GraphQL APIs support `since` parameter on some list endpoints (e.g., `/issues`, `/comments`, `/commits`) and `updated` sorting on others. The connector is a Python CDK connector with stream classes extending `GithubStream`.

**Connector type:** Python CDK

**Analysis status:** Complete stream-by-stream analysis performed. All high-volume streams already use `SemiIncrementalMixin` (client-side cursor filtering) or `IncrementalMixin` (server-side `since` parameter). Remaining full-refresh streams are either small reference datasets, deprecated endpoints, child streams without independent filtering, or computed statistics.

### Already Incremental Streams

| Stream | Sync Mode | Cursor Field | Mixin | Notes |
|--------|-----------|-------------|-------|-------|
| Repositories | semi-incremental | updated_at | SemiIncrementalMixin | Sorted by `updated` descending |
| Events | semi-incremental | created_at | SemiIncrementalMixin | |
| PullRequests | semi-incremental | updated_at | SemiIncrementalMixin | Switches sort direction based on state |
| CommitComments | semi-incremental | updated_at | SemiIncrementalMixin | |
| IssueMilestones | semi-incremental | updated_at | SemiIncrementalMixin | |
| Stargazers | semi-incremental | starred_at | SemiIncrementalMixin | |
| Projects | semi-incremental | updated_at | SemiIncrementalMixin | Classic projects |
| IssueEvents | semi-incremental | created_at | SemiIncrementalMixin | |
| Comments | incremental | updated_at | IncrementalMixin | Server-side `since` parameter |
| Commits | incremental | created_at | IncrementalMixin | Server-side `since` parameter |
| Issues | incremental | updated_at | IncrementalMixin | Server-side `since` parameter |
| ReviewComments | incremental | updated_at | IncrementalMixin | Server-side `since` parameter |
| Releases | semi-incremental | created_at | SemiIncrementalMixin | GraphQL |
| PullRequestStats | semi-incremental | updated_at | SemiIncrementalMixin | GraphQL |
| Reviews | semi-incremental | updated_at | SemiIncrementalMixin | GraphQL |
| ProjectsV2 | semi-incremental | updatedAt | SemiIncrementalMixin | GraphQL |
| IssueReactions | semi-incremental | created_at | SemiIncrementalMixin | GraphQL |
| PullRequestCommentReactions | semi-incremental | created_at | SemiIncrementalMixin | GraphQL |
| Deployments | semi-incremental | updated_at | SemiIncrementalMixin | |
| Workflows | semi-incremental | updated_at | SemiIncrementalMixin | |
| WorkflowRuns | semi-incremental | updated_at | SemiIncrementalMixin | |
| WorkflowJobs | semi-incremental | completed_at | SemiIncrementalMixin | |

### Full-Refresh Streams (Not Actionable)

| Stream | Reason | API Endpoint | Evidence |
|--------|--------|-------------|----------|
| RepositoryStats | Technical/connection check | `GET /repos/{owner}/{repo}` | Single record per repo; used for connection validation only |
| Assignees | No timestamp field; small dataset | `GET /repos/{owner}/{repo}/assignees` | GitHub API returns user objects without modification timestamps |
| Branches | No timestamp field; small dataset | `GET /repos/{owner}/{repo}/branches` | Branch objects have no `updated_at`; no `since` parameter |
| Collaborators | No timestamp field; small dataset | `GET /repos/{owner}/{repo}/collaborators` | User objects without modification timestamps |
| IssueLabels | No timestamp field; small dataset | `GET /repos/{owner}/{repo}/labels` | Label objects have no `updated_at`; no `since` parameter |
| Tags | No timestamp field; small dataset | `GET /repos/{owner}/{repo}/tags` | Tag objects have no timestamps; append-only by nature |
| Organizations | Single record per org | `GET /orgs/{org}` | Single record fetch; no filtering benefit |
| Teams | No timestamp field; small dataset | `GET /orgs/{org}/teams` | Team objects lack `updated_at`; no `since` parameter |
| Users | No timestamp field; small dataset | `GET /orgs/{org}/members` | Member list endpoint has no date filtering |
| PullRequestCommits | Child stream; no independent filtering | `GET /repos/{owner}/{repo}/pulls/{pull_number}/commits` | Per-PR endpoint; no `since` param; must re-fetch per parent |
| ProjectColumns | Deprecated; no filtering | `GET /projects/{project_id}/columns` | Classic projects deprecated in favor of ProjectsV2 |
| ProjectCards | Deprecated; no filtering | `GET /projects/columns/{column_id}/cards` | Classic projects deprecated; `updated_at` exists but no API filter |
| TeamMembers | Child stream; no timestamp | `GET /orgs/{org}/teams/{team_slug}/members` | Per-team endpoint; no date filtering |
| TeamMemberships | Child of child; no timestamp | `GET /orgs/{org}/teams/{team_slug}/memberships/{username}` | Per-member endpoint; no date filtering |
| ContributorActivity | Computed statistics; no filtering | `GET /repos/{owner}/{repo}/stats/contributors` | GitHub computes weekly commit stats server-side; no cursor field |
| IssueTimelineEvents | Child stream; no filtering | `GET /repos/{owner}/{repo}/issues/{issue_number}/timeline` | Per-issue endpoint; no `since` parameter |
| CommitCommentReactions | Child stream; no filtering | Per-comment reaction endpoint | Reactions lack timestamps; no date-based API filtering |
| IssueCommentReactions | Child stream; no filtering | Per-comment reaction endpoint | Reactions lack timestamps; no date-based API filtering |
