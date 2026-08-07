# GitHub (Beta, Gen-2) Source

This is the repository for the GitHub (Beta, Gen-2) source connector, written in the manifest-only (declarative YAML) format.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.com/integrations/sources/github-gen2).

Before changing a stream or a field, read [CONTRIBUTING.md](./CONTRIBUTING.md): it documents the normalization, typing and URL rules this connector is designed around.

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
| `api_url` | string | No | Base URL of the GitHub REST API (default: `https://api.github.com`, override for GitHub Enterprise Server) |

### Streams

| Stream | Sync Mode | Primary Key | Cursor |
|--------|-----------|-------------|--------|
| repositories | Full Refresh | id | - |
| pull_requests | Incremental | id | updated_at |
| issues | Incremental | id | updated_at |
| commits | Incremental | sha | commit_committer_date |
| comments | Incremental | id | updated_at |
| review_comments | Incremental | id | updated_at |
| reviews | Full Refresh (substream of pull_requests) | id | - |
| stargazers | Incremental (client-side) | user_id, repository | starred_at |
| branches | Full Refresh | name, repository | - |
| tags | Full Refresh | name, repository | - |
| releases | Incremental (client-side) | id | updated_at |
| workflows | Incremental (client-side) | id | updated_at |
| workflow_runs | Incremental (client-side) | id | updated_at |
| workflow_jobs | Full Refresh (substream of workflow_runs) | id | - |
