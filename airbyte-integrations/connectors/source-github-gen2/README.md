# GitHub (Beta, Gen-2) Source

This is the repository for the GitHub (Beta, Gen-2) source connector, written in the manifest-only (declarative YAML) format.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.com/integrations/sources/github-gen2).

## Local development

### Prerequisites

- Python 3.10+
- [Airbyte CDK](https://github.com/airbytehq/airbyte-python-cdk)

### Building

This connector is manifest-only and does not require a build step. The manifest is interpreted by the `source-declarative-manifest` base image at runtime.

### Testing

Acceptance tests can be run with:

```bash
cd airbyte-integrations/connectors/source-github-gen2
acceptance-test-docker.sh
```

### Configuration

The connector requires the following configuration:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `access_token` | string | Yes | GitHub Personal Access Token with `repo` scope |
| `repositories` | array[string] | Yes | List of repositories in `owner/repo` format |
| `start_date` | string | No | ISO 8601 start date for incremental streams (default: 2010-01-01) |
| `api_url` | string | No | GitHub API URL (default: api.github.com, override for GHE) |

### Streams

| Stream | Sync Mode | Primary Key | Cursor |
|--------|-----------|-------------|--------|
| repositories | Full Refresh | id | - |
| pull_requests | Incremental | id | updated_at |
| issues | Incremental | id | updated_at |
| commits | Incremental | sha | commit_committer_date |
| comments | Incremental | id | updated_at |
| review_comments | Incremental | id | updated_at |
| reviews | Full Refresh (sub-resource) | id | - |
| stargazers | Full Refresh | user_id, repository | - |
| branches | Full Refresh | name, repository | - |
| tags | Full Refresh | name, repository | - |
| releases | Full Refresh | id | - |
| workflow_runs | Incremental | id | updated_at |
