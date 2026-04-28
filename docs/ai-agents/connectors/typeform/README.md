# Typeform

The Typeform agent connector is a Python package that equips AI agents to interact with Typeform through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Typeform API. Provides access to forms, form responses, webhooks, workspaces, images, and themes. Supports listing and retrieving typeform resources for survey and form management workflows.


## Example questions

The Typeform connector is optimized to handle prompts like these.

- List all my typeforms
- Show me the responses for my latest form
- What workspaces do I have?
- List all themes in my account
- Get the details of a specific form
- Which forms received the most responses last month?
- Find responses submitted in the last week
- What forms were created this year?
- Show me all forms in a specific workspace

## Unsupported questions

The Typeform connector isn't currently able to handle prompts like these.

- Create a new typeform
- Delete a form response
- Update form settings
- Send a webhook notification

## Installation

```bash
uv pip install airbyte-agent-sdk
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_sdk.connectors.typeform import TypeformConnector
from airbyte_agent_sdk.connectors.typeform.models import TypeformAuthConfig

connector = TypeformConnector(
    auth_config=TypeformAuthConfig(
        access_token="<Personal access token from your Typeform account settings>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@TypeformConnector.tool_utils
async def typeform_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

The `connect()` factory returns a fully typed `TypeformConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:

```python
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.typeform import TypeformConnector

connector = connect("typeform", workspace_name="<your_workspace_name>")

@agent.tool_plain # assumes you're using Pydantic AI
@TypeformConnector.tool_utils
async def typeform_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

```python
from airbyte_agent_sdk.connectors.typeform import TypeformConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = TypeformConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@TypeformConnector.tool_utils
async def typeform_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Forms | [List](./REFERENCE.md#forms-list), [Get](./REFERENCE.md#forms-get), [Context Store Search](./REFERENCE.md#forms-context-store-search) |
| Responses | [List](./REFERENCE.md#responses-list), [Context Store Search](./REFERENCE.md#responses-context-store-search) |
| Webhooks | [List](./REFERENCE.md#webhooks-list), [Context Store Search](./REFERENCE.md#webhooks-context-store-search) |
| Workspaces | [List](./REFERENCE.md#workspaces-list), [Context Store Search](./REFERENCE.md#workspaces-context-store-search) |
| Images | [List](./REFERENCE.md#images-list), [Context Store Search](./REFERENCE.md#images-context-store-search) |
| Themes | [List](./REFERENCE.md#themes-list), [Context Store Search](./REFERENCE.md#themes-context-store-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Typeform API docs

See the official [Typeform API reference](https://developer.typeform.com/).

## Version information

- **Package version:** 1.0.4
- **Connector version:** 1.0.4
- **Generated with Connector SDK commit SHA:** unknown