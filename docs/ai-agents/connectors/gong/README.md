# Gong agent connector

Gong is a revenue intelligence platform that captures and analyzes customer interactions
across calls, emails, and web conferences. This connector provides access to users,
recorded calls with transcripts, activity statistics, scorecards, trackers, workspaces,
coaching metrics, and library content for sales performance analysis and revenue insights.


## Example questions

- List all users in my Gong account
- Show me calls from last week
- Get the transcript for call abc123
- What are the activity stats for our sales team?
- List all workspaces in Gong
- Show me the scorecard configurations
- What trackers are set up in my account?
- Get coaching metrics for manager user123

## Unsupported questions

- Create a new user in Gong
- Delete a call recording
- Update scorecard questions
- Schedule a new meeting
- Send feedback to a team member
- Modify tracker keywords

## Installation

```bash
uv pip install airbyte-agent-gong
```

## Usage

This connector supports multiple authentication methods:

### OAuth 2.0 Authentication

```python
from airbyte_agent_gong import GongConnector
from airbyte_agent_gong.models import GongOauth20AuthenticationAuthConfig

connector = GongConnector(
  auth_config=GongOauth20AuthenticationAuthConfig(
    access_token="..."
  )
)
result = await connector.users.list()
```

### Access Key Authentication

```python
from airbyte_agent_gong import GongConnector
from airbyte_agent_gong.models import GongAccessKeyAuthenticationAuthConfig

connector = GongConnector(
  auth_config=GongAccessKeyAuthenticationAuthConfig(
    access_key="...",
    access_key_secret="..."
  )
)
result = await connector.users.list()
```


## Full documentation

This connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get) |
| Calls | [List](./REFERENCE.md#calls-list), [Get](./REFERENCE.md#calls-get) |
| Calls Extensive | [List](./REFERENCE.md#calls-extensive-list) |
| Call Audio | [Download](./REFERENCE.md#call-audio-download) |
| Call Video | [Download](./REFERENCE.md#call-video-download) |
| Workspaces | [List](./REFERENCE.md#workspaces-list) |
| Call Transcripts | [List](./REFERENCE.md#call-transcripts-list) |
| Stats Activity Aggregate | [List](./REFERENCE.md#stats-activity-aggregate-list) |
| Stats Activity Day By Day | [List](./REFERENCE.md#stats-activity-day-by-day-list) |
| Stats Interaction | [List](./REFERENCE.md#stats-interaction-list) |
| Settings Scorecards | [List](./REFERENCE.md#settings-scorecards-list) |
| Settings Trackers | [List](./REFERENCE.md#settings-trackers-list) |
| Library Folders | [List](./REFERENCE.md#library-folders-list) |
| Library Folder Content | [List](./REFERENCE.md#library-folder-content-list) |
| Coaching | [List](./REFERENCE.md#coaching-list) |
| Stats Activity Scorecards | [List](./REFERENCE.md#stats-activity-scorecards-list) |


For detailed documentation on available actions and parameters, see this connector's [full reference documentation](./REFERENCE.md).

For the service's official API docs, see the [Gong API reference](https://gong.app.gong.io/settings/api/documentation).

## Version information

- **Package version:** 0.19.26
- **Connector version:** 0.1.5
- **Generated with Connector SDK commit SHA:** 12f6b994298f84dfa217940afe7c6b19bec4167b