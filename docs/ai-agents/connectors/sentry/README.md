# Sentry

The Sentry agent connector is a Python package that equips AI agents to interact with Sentry through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Sentry error monitoring and performance tracking API. Provides access to projects, issues, events, and releases within your Sentry organization. Supports listing and retrieving detailed information about error tracking data, project configurations, and software releases.

## Example questions

The Sentry connector is optimized to handle prompts like these.

- List all projects in my Sentry organization
- Show me the issues for a specific project
- List recent events from a project
- Show me all releases for my organization
- Get the details of a specific project
- What are the most common unresolved issues?
- Which projects have the most events?
- Show me issues that were first seen this week
- Find releases created in the last month

## Unsupported questions

The Sentry connector isn't currently able to handle prompts like these.

- Create a new project in Sentry
- Delete an issue
- Update a release
- Resolve all issues in a project

## Installation

```bash
uv pip install airbyte-agent-sentry
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_sentry import SentryConnector
from airbyte_agent_sentry.models import SentryAuthConfig

connector = SentryConnector(
    auth_config=SentryAuthConfig(
        auth_token="<Sentry authentication token. Log into Sentry and create one at Settings > Account > API > Auth Tokens.>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@SentryConnector.tool_utils
async def sentry_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_sentry import SentryConnector, AirbyteAuthConfig

connector = SentryConnector(
    auth_config=AirbyteAuthConfig(
        customer_name="<your_customer_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@SentryConnector.tool_utils
async def sentry_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Projects | [List](./REFERENCE.md#projects-list), [Get](./REFERENCE.md#projects-get), [Search](./REFERENCE.md#projects-search) |
| Issues | [List](./REFERENCE.md#issues-list), [Get](./REFERENCE.md#issues-get), [Search](./REFERENCE.md#issues-search) |
| Events | [List](./REFERENCE.md#events-list), [Get](./REFERENCE.md#events-get), [Search](./REFERENCE.md#events-search) |
| Releases | [List](./REFERENCE.md#releases-list), [Get](./REFERENCE.md#releases-get), [Search](./REFERENCE.md#releases-search) |
| Project Detail | [Get](./REFERENCE.md#project-detail-get) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Sentry API docs

See the official [Sentry API reference](https://docs.sentry.io/api/).

## Version information

- **Package version:** 0.1.8
- **Connector version:** 1.0.2
- **Generated with Connector SDK commit SHA:** 09ed4945e89bf743be8a0f0d596ae77c99526607
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/sentry/CHANGELOG.md)