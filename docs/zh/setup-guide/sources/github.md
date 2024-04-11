# GitHub

This page contains the setup guide and reference information for GitHub.

## Prerequisites

* List of GitHub repositories
* GitHub personal access token

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh Overwrite | Yes |
| Full Refresh Append | Yes |
| Incremental Sync Append | Yes |
| Incremental Sync Append + Deduped | Yes |

## Setup guide

### Step 1: Obtain GitHub personal access token

1. Sign in to your GitHub account.

2. Go to Settings -> Developer settings -> [Personal access tokens](https://github.com/settings/tokens) page.

3. Click **Generate new token**, select **scopes** which define the access for the token, and click **Generate token**.
![GitHub personal access token](/docs/setup-guide/assets/images/github-generate-new-token.jpg "GitHub personal access token")

  > NOTE: Your token should have at least the `repo` scope. Depending on which streams you want to sync, the user generating the token needs more permissions:

  > * For syncing Collaborators, the user which generates the personal access token must be a collaborator. To become a collaborator, they must be invited by an owner. If there are no collaborators, no records will be synced. Read more about access permissions [here](https://docs.github.com/en/get-started/learning-about-github/access-permissions-on-github).
  > * For syncing [Teams](https://docs.github.com/en/organizations/organizing-members-into-teams/about-teams) is only available to authenticated members of a team's organization. Personal user accounts and repositories belonging to them don't have access to Teams features. In this case no records will be synced.
  > * For syncing Projects, the repository must have the Projects feature enabled.

4. Save your access token for later use.

### Step 2: Set up GitHub in Daspire

1. Select **GitHub** from the Source list.

2. Enter a **Source Name**.

3. Authenticate with **Personal Access Token**. To load balance your API quota consumption across multiple API tokens, input multiple tokens separated with `,`.

4. **GitHub Repositories** - Enter a list of GitHub organizations/repositories, e.g. `daspirehq/daspire` for single repository, `daspirehq/daspire` `daspirehq/daspire2` for multiple repositories. If you want to specify the organization to receive data from all its repositories, then you should specify it according to the following example: `daspirehq/*`.

  > CAUTION: Repositories with the wrong name or repositories that do not exist or have the wrong name format will be skipped.

5. **Start date (Optional)** - The date from which you'd like to replicate data for streams. For streams which support this configuration, only data generated on or after the start date will be replicated.

  > * These streams will only sync records generated on or after the Start Date: `comments`, `commit_comment_reactions`, `commit_comments`, `commits`, `deployments`, `events`, `issue_comment_reactions`, `issue_events`, `issue_milestones`, `issue_reactions`, `issues`, `project_cards`, `project_columns`, `projects`, `pull_request_comment_reactions`, `pull_requests`, `pull_requeststats`, `releases`, `review_comments`, `reviews`, `stargazers`, `workflow_runs`, `workflows`.

  > * The Start Date does not apply to the streams below and all data will be synced for these streams: `assignees`, `branches`, `collaborators`, `issue_labels`, `organizations`, `pull_request_commits`, `pull_request_stats`, `repositories`, `tags`, `teams`, `users`

6. **Branch (Optional)** - List of GitHub repository branches to pull commits from, e.g. `daspirehq/daspire/main`. If no branches are specified for a repository, the default branch will be pulled.

7. **Max requests per hour (Optional)** - The GitHub API allows for a maximum of 5,000 requests per hour (15,000 for Github Enterprise). You can specify a lower value to limit your use of the API quota. Refer to GitHub article [Rate limits for the REST API](https://docs.github.com/en/rest/overview/rate-limits-for-the-rest-api).

8. Click **Save & Test**.

## Supported streams

This source outputs the following **full refresh streams**:

* [Assignees](https://docs.github.com/en/rest/issues/assignees?apiVersion=2022-11-28#list-assignees)
* [Branches](https://docs.github.com/en/rest/branches/branches?apiVersion=2022-11-28#list-branches)
* [Contributor Activity](https://docs.github.com/en/rest/metrics/statistics?apiVersion=2022-11-28#get-all-contributor-commit-activity)
* [Collaborators](https://docs.github.com/en/rest/collaborators/collaborators?apiVersion=2022-11-28#list-repository-collaborators)
* [Issue labels](https://docs.github.com/en/rest/issues/labels?apiVersion=2022-11-28#list-labels-for-a-repository)
* [Organizations](https://docs.github.com/en/rest/orgs/orgs?apiVersion=2022-11-28#list-organizations)
* [Pull request commits](https://docs.github.com/en/rest/pulls/pulls?apiVersion=2022-11-28#list-commits-on-a-pull-request)
* [Tags](https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-repository-tags)
* [TeamMembers](https://docs.github.com/en/rest/teams/members?apiVersion=2022-11-28#list-team-members)
* [TeamMemberships](https://docs.github.com/en/rest/teams/members?apiVersion=2022-11-28#get-team-membership-for-a-user)
* [Teams](https://docs.github.com/en/rest/teams/teams?apiVersion=2022-11-28#list-teams)
* [Users](https://docs.github.com/en/rest/orgs/members?apiVersion=2022-11-28#list-organization-members)
* [Issue timeline events](https://docs.github.com/en/rest/issues/timeline?apiVersion=2022-11-28#list-timeline-events-for-an-issue)

This source outputs the following **incremental streams**:

* [Comments](https://docs.github.com/en/rest/issues/comments?apiVersion=2022-11-28#list-issue-comments-for-a-repository)
* [Commit comment reactions](https://docs.github.com/en/rest/reference/reactions?apiVersion=2022-11-28#list-reactions-for-a-commit-comment)
* [Commit comments](https://docs.github.com/en/rest/commits/comments?apiVersion=2022-11-28#list-commit-comments-for-a-repository)
* [Commits](https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#list-commits)
* [Deployments](https://docs.github.com/en/rest/deployments/deployments?apiVersion=2022-11-28#list-deployments)
* [Events](https://docs.github.com/en/rest/activity/events?apiVersion=2022-11-28#list-repository-events)
* [Issue comment reactions](https://docs.github.com/en/rest/reactions/reactions?apiVersion=2022-11-28#list-reactions-for-an-issue-comment)
* [Issue events](https://docs.github.com/en/rest/issues/events?apiVersion=2022-11-28#list-issue-events-for-a-repository)
* [Issue milestones](https://docs.github.com/en/rest/issues/milestones?apiVersion=2022-11-28#list-milestones)
* [Issue reactions](https://docs.github.com/en/rest/reactions/reactions?apiVersion=2022-11-28#list-reactions-for-an-issue)
* [Issues](https://docs.github.com/en/rest/issues/issues?apiVersion=2022-11-28#list-repository-issues)
* [Project (Classic) cards](https://docs.github.com/en/rest/projects/cards?apiVersion=2022-11-28#list-project-cards)
* [Project (Classic) columns](https://docs.github.com/en/rest/projects/columns?apiVersion=2022-11-28#list-project-columns)
* [Projects (Classic)](https://docs.github.com/en/rest/projects/projects?apiVersion=2022-11-28#list-repository-projects)
* [ProjectsV2](https://docs.github.com/en/graphql/reference/objects#projectv2)
* [Pull request comment reactions](https://docs.github.com/en/rest/reactions/reactions?apiVersion=2022-11-28#list-reactions-for-a-pull-request-review-comment)
* [Pull request stats](https://docs.github.com/en/graphql/reference/objects#pullrequest)
* [Pull requests](https://docs.github.com/en/rest/pulls/pulls?apiVersion=2022-11-28#list-pull-requests)
* [Releases](https://docs.github.com/en/rest/releases/releases?apiVersion=2022-11-28#list-releases)
* [Repositories](https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-organization-repositories)
* [Review comments](https://docs.github.com/en/rest/pulls/comments?apiVersion=2022-11-28#list-review-comments-in-a-repository)
* [Reviews](https://docs.github.com/en/rest/pulls/reviews?apiVersion=2022-11-28#list-reviews-for-a-pull-request)
* [Stargazers](https://docs.github.com/en/rest/activity/starring?apiVersion=2022-11-28#list-stargazers)
* [WorkflowJobs](https://docs.github.com/pt/rest/actions/workflow-jobs?apiVersion=2022-11-28#list-jobs-for-a-workflow-run)
* [WorkflowRuns](https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28#list-workflow-runs-for-a-repository)
* [Workflows](https://docs.github.com/en/rest/actions/workflows?apiVersion=2022-11-28#list-repository-workflows)

### Notes

1. Only 4 streams (`comments`, `commits`, `issues` and `review comments`) from the listed above streams are pure incremental meaning that they:

  > * read only new records;
  > * output only new records.

2. Streams `workflow_runs` and `worflow_jobs` is almost pure incremental:

  > * read new records and some portion of old records (in past 30 days);
  > * the `workflow_jobs` depends on the `workflow_runs` to read the data, so they both follow the same logic docs;
  > * output only new records.

3. Other 19 incremental streams are also incremental but with one difference, they:

  > * read all records;
  > * output only new records. Please, consider this behaviour when using those 19 incremental streams because it may affect you API call limits.

4. Sometimes for large streams specifying very distant `start_date` in the past may result in keep on getting error from GitHub instead of records. In this case Specifying more recent `start_date` may help. The "Start date" configuration option does not apply to the streams below, because the GitHub API does not include dates which can be used for filtering:

  > * `assignees`
  > * `branches`
  > * `collaborators`
  > * `issue_labels`
  > * `organizations`
  > * `pull_request_commits`
  > * `pull_request_stats`
  > * `repositories`
  > * `tags`
  > * `teams`
  > * `users`

## Performance consideration

The GitHub integration should not run into GitHub API limitations under normal usage. Refer to GitHub article [Rate limits for the REST API](https://docs.github.com/en/rest/overview/rate-limits-for-the-rest-api).

## Troubleshooting

Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.
