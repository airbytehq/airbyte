# Github

## Overview

The GitHub source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This Github source wraps the [Singer Github Tap](https://github.com/singer-io/tap-github).

### Output schema

This connector outputs the following streams: 
  * [Assignees](https://developer.github.com/v3/issues/assignees/#list-assignees)
  * [Collaborators](https://developer.github.com/v3/repos/collaborators/#list-collaborators)
  * [Comments](https://developer.github.com/v3/issues/comments/#list-comments-in-a-repository)
  * [Commits](https://developer.github.com/v3/repos/commits/#list-commits-on-a-repository)
  * [Commit comments](https://docs.github.com/en/free-pro-team@latest/rest/reference/repos#list-commit-comments-for-a-repository)
  * [Events](https://docs.github.com/en/free-pro-team@latest/rest/reference/activity#list-repository-events)  
  * [Issues](https://developer.github.com/v3/issues/#list-issues-for-a-repository)
  * [Issue events](https://docs.github.com/en/free-pro-team@latest/rest/reference/issues#list-issue-events-for-a-repository) 
  * [Issue labels](https://docs.github.com/en/free-pro-team@latest/rest/reference/issues#list-labels-for-a-repository)
  * [Issue milestones](https://docs.github.com/en/free-pro-team@latest/rest/reference/issues#list-milestones)
  * [Projects](https://docs.github.com/en/free-pro-team@latest/rest/reference/projects#list-repository-projects) 
  * [Project cards](https://docs.github.com/en/free-pro-team@latest/rest/reference/projects#list-project-cards) 
  * [Project columns](https://docs.github.com/en/free-pro-team@latest/rest/reference/projects#list-project-columns)
  * [Pull requests](https://developer.github.com/v3/pulls/#list-pull-requests)
  * [PR commits](https://docs.github.com/en/free-pro-team@latest/rest/reference/pulls#list-commits-on-a-pull-request)  
  * [Pull request reviews](https://docs.github.com/en/free-pro-team@latest/rest/reference/pulls#reviews)
  * [Releases](https://docs.github.com/en/free-pro-team@latest/rest/reference/repos#list-releases)  
  * [Reviews](https://developer.github.com/v3/pulls/reviews/#list-reviews-on-a-pull-request)
  * [Review comments](https://developer.github.com/v3/pulls/comments)
  * [Stargazers](https://developer.github.com/v3/activity/starring/#list-stargazers)
  * [Teams](https://docs.github.com/en/free-pro-team@latest/rest/reference/teams#list-teams)
  * [Team members](https://docs.github.com/en/free-pro-team@latest/rest/reference/teams#list-team-members) 
  * [Team memberships](https://docs.github.com/en/free-pro-team@latest/rest/reference/teams#get-team-membership-for-a-user)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | yes |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |

### Performance considerations

The Github connector should not run into Github API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Github Account
* Github Personal Access Token.

### Setup guide

Log into Github and then generate a [personal access token](https://github.com/settings/tokens).

We recommend creating a restricted key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access.

### Scopes for OAuth Apps

[Scopes](https://docs.github.com/en/free-pro-team@latest/developers/apps/scopes-for-oauth-apps) let you specify exactly what type of access you need. Scopes limit access for OAuth tokens. They do not grant any additional permission beyond that which the user already has.

When setting up an OAuth App on GitHub, requested scopes are displayed to the user on the authorization form.

Full list of available scopes is presented [here](https://docs.github.com/en/free-pro-team@latest/developers/apps/scopes-for-oauth-apps#available-scopes).

For syncing streams it are required at least public_repo and read:org scopes.

Syncing of some streams has particulars:
* For calling Collaborators API user has to be one of them. In another case API will return 403 error. To become one of the collaborators, it is needed user to be invited by an owner. More about access permission you can read [here](https://docs.github.com/en/free-pro-team@latest/github/getting-started-with-github/access-permissions-on-github)
* [Teams](https://docs.github.com/en/free-pro-team@latest/github/setting-up-and-managing-organizations-and-teams/about-teams) are groups of organization members, therefore Teams API is only available to authenticated members of the team's [organization](https://docs.github.com/en/free-pro-team@latest/rest/reference/orgs), in another case it will return 404 error. [Personal user accounts](https://docs.github.com/en/free-pro-team@latest/github/getting-started-with-github/types-of-github-accounts) don't have access to Teams features. If user doesn't have permission, it will return 401 error.
* Project API returns a 404 Not Found status if projects are disabled in the repository. If user does not have sufficient privileges to perform this action, a 401 Unauthorized or 410 Gone status is returned.


