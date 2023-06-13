## Prerequisites

- Access to a Github repository

## Setup guide

1. Name your source.
2. Click `Authenticate your GitHub account` or use a [Personal Access Token](https://github.com/settings/tokens) for Authentication. For Personal Access Tokens, refer to the list of required [permissions and scopes](https://docs.airbyte.com/integrations/sources/github#permissions-and-scopes).
3. **Start date** Enter the date you'd like to replicate data from. 

These streams will only sync records generated on or after the **Start Date**: 

`comments`, `commit_comment_reactions`, `commit_comments`, `commits`, `deployments`, `events`, `issue_comment_reactions`, `issue_events`, `issue_milestones`, `issue_reactions`, `issues`, `project_cards`, `project_columns`, `projects`, `pull_request_comment_reactions`, `pull_requests`, `pull_requeststats`, `releases`, `review_comments`, `reviews`, `stargazers`, `workflow_runs`, `workflows`.

The **Start Date** does not apply to the streams below and all data will be synced for these streams:

`assignees`, `branches`, `collaborators`, `issue_labels`, `organizations`, `pull_request_commits`, `pull_request_stats`, `repositories`,  `tags`,  `teams`, `users`

4. **GitHub Repositories** - Enter a space-delimited list of GitHub organizations or repositories.

Example of a single repository:
```
airbytehq/airbyte
```
Example of multiple repositories:
```
airbytehq/airbyte airbytehq/another-repo
```
Example of an organization to receive data from all of its repositories: 
```
airbytehq/*
```
Repositories which have a misspelled name, do not exist, or have the wrong name format will return an error.

5. (Optional) **Branch** - Enter a space-delimited list of GitHub repository branches to pull commits for, e.g. `airbytehq/airbyte/master`. If no branches are specified for a repository, the default branch will be pulled. (e.g. `airbytehq/airbyte/master airbytehq/airbyte/my-branch`).
6. (Optional) **Max requests per hour** - The GitHub API allows for a maximum of 5000 requests per hour (15,000 for Github Enterprise). You can specify a lower value to limit your use of the API quota.

### Incremental Sync Methods
Incremental sync is offered for most streams, with some differences in sync behavior.

1. `comments`, `commits`, `issues` and `review comments` only syncs new records. Only new records will be synced.

2. `workflow_runs` and `worflow_jobs` syncs new records and any records run in the [last 30 days](https://docs.github.com/en/actions/managing-workflow-runs/re-running-workflows-and-jobs)

3. All other incremental streams sync all historical records and output any updated or new records.

For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [GitHub](https://docs.airbyte.com/integrations/sources/github/).
