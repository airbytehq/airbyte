# Github full reference

This is the full reference documentation for the Github agent connector.

## Supported entities and actions

The Github connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Repositories | [Get](#repositories-get), [List](#repositories-list), [API Search](#repositories-api-search) |
| Org Repositories | [List](#org-repositories-list) |
| Branches | [List](#branches-list), [Get](#branches-get) |
| Commits | [List](#commits-list), [Get](#commits-get) |
| Releases | [List](#releases-list), [Get](#releases-get) |
| Issues | [List](#issues-list), [Get](#issues-get), [API Search](#issues-api-search) |
| Pull Requests | [List](#pull-requests-list), [Get](#pull-requests-get), [API Search](#pull-requests-api-search) |
| Reviews | [List](#reviews-list) |
| Comments | [List](#comments-list), [Get](#comments-get) |
| Pr Comments | [List](#pr-comments-list), [Get](#pr-comments-get) |
| Labels | [List](#labels-list), [Get](#labels-get) |
| Milestones | [List](#milestones-list), [Get](#milestones-get) |
| Organizations | [Get](#organizations-get), [List](#organizations-list) |
| Users | [Get](#users-get), [List](#users-list), [API Search](#users-api-search) |
| Teams | [List](#teams-list), [Get](#teams-get) |
| Tags | [List](#tags-list), [Get](#tags-get) |
| Stargazers | [List](#stargazers-list) |
| Viewer | [Get](#viewer-get) |
| Viewer Repositories | [List](#viewer-repositories-list) |
| Projects | [List](#projects-list), [Get](#projects-get) |
| Project Items | [List](#project-items-list) |

## Repositories

### Repositories Get

Gets information about a specific GitHub repository using GraphQL

#### Python SDK

```python
await github.repositories.get(
    owner="<str>",
    repo="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "repositories",
    "action": "get",
    "params": {
        "owner": "<str>",
        "repo": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository (username or organization) |
| `repo` | `string` | Yes | The name of the repository |
| `fields` | `array<string>` | No | Optional array of field names to select.
If not provided, uses default fields.
 |


### Repositories List

Returns a list of repositories for the specified user using GraphQL

#### Python SDK

```python
await github.repositories.list(
    username="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "repositories",
    "action": "list",
    "params": {
        "username": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `username` | `string` | Yes | The username of the user whose repositories to list |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination (from previous response's endCursor) |
| `fields` | `array<string>` | No | Optional array of field names to select.
If not provided, uses default fields.
 |


### Repositories API Search

Search for GitHub repositories using GitHub's powerful search syntax.
Examples: "language:python stars:>1000", "topic:machine-learning", "org:facebook is:public"


#### Python SDK

```python
await github.repositories.api_search(
    query="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "repositories",
    "action": "api_search",
    "params": {
        "query": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | Yes | GitHub repository search query using GitHub's search syntax |
| `limit` | `integer` | No | Number of results to return |
| `after` | `string` | No | Cursor for pagination (from previous response's endCursor) |
| `fields` | `array<string>` | No | Optional array of field names to select.
If not provided, uses default fields.
 |


## Org Repositories

### Org Repositories List

Returns a list of repositories for the specified organization using GraphQL

#### Python SDK

```python
await github.org_repositories.list(
    org="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "org_repositories",
    "action": "list",
    "params": {
        "org": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `org` | `string` | Yes | The organization login/username |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


## Branches

### Branches List

Returns a list of branches for the specified repository using GraphQL

#### Python SDK

```python
await github.branches.list(
    owner="<str>",
    repo="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "branches",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Branches Get

Gets information about a specific branch using GraphQL

#### Python SDK

```python
await github.branches.get(
    owner="<str>",
    repo="<str>",
    branch="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "branches",
    "action": "get",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "branch": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `branch` | `string` | Yes | The branch name |
| `fields` | `array<string>` | No | Optional array of field names to select |


## Commits

### Commits List

Returns a list of commits for the default branch using GraphQL

#### Python SDK

```python
await github.commits.list(
    owner="<str>",
    repo="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "commits",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Commits Get

Gets information about a specific commit by SHA using GraphQL

#### Python SDK

```python
await github.commits.get(
    owner="<str>",
    repo="<str>",
    sha="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "commits",
    "action": "get",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "sha": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `sha` | `string` | Yes | The commit SHA |
| `fields` | `array<string>` | No | Optional array of field names to select |


## Releases

### Releases List

Returns a list of releases for the specified repository using GraphQL

#### Python SDK

```python
await github.releases.list(
    owner="<str>",
    repo="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "releases",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Releases Get

Gets information about a specific release by tag name using GraphQL

#### Python SDK

```python
await github.releases.get(
    owner="<str>",
    repo="<str>",
    tag="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "releases",
    "action": "get",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "tag": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `tag` | `string` | Yes | The release tag name |
| `fields` | `array<string>` | No | Optional array of field names to select |


## Issues

### Issues List

Returns a list of issues for the specified repository using GraphQL

#### Python SDK

```python
await github.issues.list(
    owner="<str>",
    repo="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `states` | `array<"OPEN" \| "CLOSED">` | No | Filter by issue state |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Issues Get

Gets information about a specific issue using GraphQL

#### Python SDK

```python
await github.issues.get(
    owner="<str>",
    repo="<str>",
    number=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "get",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "number": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `number` | `integer` | Yes | The issue number |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Issues API Search

Search for issues using GitHub's search syntax

#### Python SDK

```python
await github.issues.api_search(
    query="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "api_search",
    "params": {
        "query": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | Yes | GitHub issue search query using GitHub's search syntax |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


## Pull Requests

### Pull Requests List

Returns a list of pull requests for the specified repository using GraphQL

#### Python SDK

```python
await github.pull_requests.list(
    owner="<str>",
    repo="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "pull_requests",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `states` | `array<"OPEN" \| "CLOSED" \| "MERGED">` | No | Filter by pull request state |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Pull Requests Get

Gets information about a specific pull request using GraphQL

#### Python SDK

```python
await github.pull_requests.get(
    owner="<str>",
    repo="<str>",
    number=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "pull_requests",
    "action": "get",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "number": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `number` | `integer` | Yes | The pull request number |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Pull Requests API Search

Search for pull requests using GitHub's search syntax

#### Python SDK

```python
await github.pull_requests.api_search(
    query="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "pull_requests",
    "action": "api_search",
    "params": {
        "query": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | Yes | GitHub pull request search query using GitHub's search syntax |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


## Reviews

### Reviews List

Returns a list of reviews for the specified pull request using GraphQL

#### Python SDK

```python
await github.reviews.list(
    owner="<str>",
    repo="<str>",
    number=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "reviews",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "number": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `number` | `integer` | Yes | The pull request number |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


## Comments

### Comments List

Returns a list of comments for the specified issue using GraphQL

#### Python SDK

```python
await github.comments.list(
    owner="<str>",
    repo="<str>",
    number=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "comments",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "number": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `number` | `integer` | Yes | The issue number |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Comments Get

Gets information about a specific issue comment by its GraphQL node ID.

Note: This endpoint requires a GraphQL node ID (e.g., 'IC_kwDOBZtLds6YWTMj'),
not a numeric database ID. You can obtain node IDs from the Comments_List response,
where each comment includes both 'id' (node ID) and 'databaseId' (numeric ID).


#### Python SDK

```python
await github.comments.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "comments",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The GraphQL node ID of the comment |
| `fields` | `array<string>` | No | Optional array of field names to select |


## Pr Comments

### Pr Comments List

Returns a list of comments for the specified pull request using GraphQL

#### Python SDK

```python
await github.pr_comments.list(
    owner="<str>",
    repo="<str>",
    number=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "pr_comments",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "number": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `number` | `integer` | Yes | The pull request number |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Pr Comments Get

Gets information about a specific pull request comment by its GraphQL node ID.

Note: This endpoint requires a GraphQL node ID (e.g., 'IC_kwDOBZtLds6YWTMj'),
not a numeric database ID. You can obtain node IDs from the PRComments_List response,
where each comment includes both 'id' (node ID) and 'databaseId' (numeric ID).


#### Python SDK

```python
await github.pr_comments.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "pr_comments",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The GraphQL node ID of the comment |
| `fields` | `array<string>` | No | Optional array of field names to select |


## Labels

### Labels List

Returns a list of labels for the specified repository using GraphQL

#### Python SDK

```python
await github.labels.list(
    owner="<str>",
    repo="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "labels",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Labels Get

Gets information about a specific label by name using GraphQL

#### Python SDK

```python
await github.labels.get(
    owner="<str>",
    repo="<str>",
    name="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "labels",
    "action": "get",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "name": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `name` | `string` | Yes | The label name |
| `fields` | `array<string>` | No | Optional array of field names to select |


## Milestones

### Milestones List

Returns a list of milestones for the specified repository using GraphQL

#### Python SDK

```python
await github.milestones.list(
    owner="<str>",
    repo="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "milestones",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `states` | `array<"OPEN" \| "CLOSED">` | No | Filter by milestone state |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Milestones Get

Gets information about a specific milestone by number using GraphQL

#### Python SDK

```python
await github.milestones.get(
    owner="<str>",
    repo="<str>",
    number=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "milestones",
    "action": "get",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "number": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `number` | `integer` | Yes | The milestone number |
| `fields` | `array<string>` | No | Optional array of field names to select |


## Organizations

### Organizations Get

Gets information about a specific organization using GraphQL

#### Python SDK

```python
await github.organizations.get(
    org="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "organizations",
    "action": "get",
    "params": {
        "org": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `org` | `string` | Yes | The organization login/username |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Organizations List

Returns a list of organizations the user belongs to using GraphQL

#### Python SDK

```python
await github.organizations.list(
    username="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "organizations",
    "action": "list",
    "params": {
        "username": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `username` | `string` | Yes | The username of the user |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


## Users

### Users Get

Gets information about a specific user using GraphQL

#### Python SDK

```python
await github.users.get(
    username="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "get",
    "params": {
        "username": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `username` | `string` | Yes | The username of the user |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Users List

Returns a list of members for the specified organization using GraphQL

#### Python SDK

```python
await github.users.list(
    org="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "list",
    "params": {
        "org": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `org` | `string` | Yes | The organization login/username |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Users API Search

Search for GitHub users using search syntax

#### Python SDK

```python
await github.users.api_search(
    query="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "api_search",
    "params": {
        "query": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | Yes | GitHub user search query using GitHub's search syntax |
| `limit` | `integer` | No | Number of results to return |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


## Teams

### Teams List

Returns a list of teams for the specified organization using GraphQL

#### Python SDK

```python
await github.teams.list(
    org="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "teams",
    "action": "list",
    "params": {
        "org": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `org` | `string` | Yes | The organization login/username |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Teams Get

Gets information about a specific team using GraphQL

#### Python SDK

```python
await github.teams.get(
    org="<str>",
    team_slug="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "teams",
    "action": "get",
    "params": {
        "org": "<str>",
        "team_slug": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `org` | `string` | Yes | The organization login/username |
| `team_slug` | `string` | Yes | The team slug |
| `fields` | `array<string>` | No | Optional array of field names to select |


## Tags

### Tags List

Returns a list of tags for the specified repository using GraphQL

#### Python SDK

```python
await github.tags.list(
    owner="<str>",
    repo="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Tags Get

Gets information about a specific tag by name using GraphQL

#### Python SDK

```python
await github.tags.get(
    owner="<str>",
    repo="<str>",
    tag="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "get",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "tag": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `tag` | `string` | Yes | The tag name |
| `fields` | `array<string>` | No | Optional array of field names to select |


## Stargazers

### Stargazers List

Returns a list of users who have starred the repository using GraphQL

#### Python SDK

```python
await github.stargazers.list(
    owner="<str>",
    repo="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "stargazers",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


## Viewer

### Viewer Get

Gets information about the currently authenticated user.
This is useful when you don't know the username but need to access
the current user's profile, permissions, or associated resources.


#### Python SDK

```python
await github.viewer.get()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "viewer",
    "action": "get"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `fields` | `array<string>` | No | Optional array of field names to select |


## Viewer Repositories

### Viewer Repositories List

Returns a list of repositories owned by the authenticated user.
Unlike Repositories_List which requires a username, this endpoint
automatically lists repositories for the current authenticated user.


#### Python SDK

```python
await github.viewer_repositories.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "viewer_repositories",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination (from previous response's endCursor) |
| `fields` | `array<string>` | No | Optional array of field names to select |


## Projects

### Projects List

Returns a list of GitHub Projects V2 for the specified organization.
Projects V2 are the new project boards that replaced classic projects.


#### Python SDK

```python
await github.projects.list(
    org="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "list",
    "params": {
        "org": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `org` | `string` | Yes | The organization login/username |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination (from previous response's endCursor) |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Projects Get

Gets information about a specific GitHub Project V2 by number

#### Python SDK

```python
await github.projects.get(
    org="<str>",
    project_number=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "get",
    "params": {
        "org": "<str>",
        "project_number": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `org` | `string` | Yes | The organization login/username |
| `project_number` | `integer` | Yes | The project number |
| `fields` | `array<string>` | No | Optional array of field names to select |


## Project Items

### Project Items List

Returns a list of items (issues, pull requests, draft issues) in a GitHub Project V2.
Each item includes its field values like Status, Priority, etc.


#### Python SDK

```python
await github.project_items.list(
    org="<str>",
    project_number=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "project_items",
    "action": "list",
    "params": {
        "org": "<str>",
        "project_number": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `org` | `string` | Yes | The organization login/username |
| `project_number` | `integer` | Yes | The project number |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination (from previous response's endCursor) |
| `fields` | `array<string>` | No | Optional array of field names to select |


