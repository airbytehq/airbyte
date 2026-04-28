# Amplitude

The Amplitude agent connector is a Python package that equips AI agents to interact with Amplitude through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Amplitude Analytics API. Provides access to core analytics data including event exports, cohort definitions, chart annotations, event type listings, active user counts, and average session length metrics. Authentication uses HTTP Basic with your Amplitude API key and secret key.


## Example questions

The Amplitude connector is optimized to handle prompts like these.

- List all chart annotations in Amplitude
- Show me all cohorts
- List all event types
- Which cohorts have more than 1000 users?
- What are the most popular event types by total count?
- Show me annotations created in the last month

## Unsupported questions

The Amplitude connector isn't currently able to handle prompts like these.

- Create a new annotation
- Delete a cohort
- Export raw event data

## Installation

```bash
uv pip install airbyte-agent-sdk
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_sdk.connectors.amplitude import AmplitudeConnector
from airbyte_agent_sdk.connectors.amplitude.models import AmplitudeAuthConfig

connector = AmplitudeConnector(
    auth_config=AmplitudeAuthConfig(
        api_key="<Your Amplitude project API key. Find it in Settings > Projects in your Amplitude account.
>",
        secret_key="<Your Amplitude project secret key. Find it in Settings > Projects in your Amplitude account.
>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@AmplitudeConnector.tool_utils
async def amplitude_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

The `connect()` factory returns a fully typed `AmplitudeConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:

```python
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amplitude import AmplitudeConnector

connector = connect("amplitude", workspace_name="<your_workspace_name>")

@agent.tool_plain # assumes you're using Pydantic AI
@AmplitudeConnector.tool_utils
async def amplitude_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

```python
from airbyte_agent_sdk.connectors.amplitude import AmplitudeConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AmplitudeConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@AmplitudeConnector.tool_utils
async def amplitude_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Annotations | [List](./REFERENCE.md#annotations-list), [Get](./REFERENCE.md#annotations-get), [Context Store Search](./REFERENCE.md#annotations-context-store-search) |
| Cohorts | [List](./REFERENCE.md#cohorts-list), [Get](./REFERENCE.md#cohorts-get), [Context Store Search](./REFERENCE.md#cohorts-context-store-search) |
| Events List | [List](./REFERENCE.md#events-list-list), [Context Store Search](./REFERENCE.md#events-list-context-store-search) |
| Active Users | [List](./REFERENCE.md#active-users-list), [Context Store Search](./REFERENCE.md#active-users-context-store-search) |
| Average Session Length | [List](./REFERENCE.md#average-session-length-list), [Context Store Search](./REFERENCE.md#average-session-length-context-store-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Amplitude API docs

See the official [Amplitude API reference](https://www.docs.developers.amplitude.com/analytics/apis/).

## Version information

- **Package version:** 1.0.3
- **Connector version:** 1.0.3
- **Generated with Connector SDK commit SHA:** unknown