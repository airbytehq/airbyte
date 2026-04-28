# Airtable

The Airtable agent connector is a Python package that equips AI agents to interact with Airtable through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Airtable is a cloud-based platform that combines the simplicity of a spreadsheet with the 
power of a database. This connector provides access to bases, tables, and records for 
data analysis and workflow automation.


## Example questions

The Airtable connector is optimized to handle prompts like these.

- List all my Airtable bases
- What tables are in my first base?
- Show me the schema for tables in a base
- List records from a table in my base
- Show me recent records from a table
- What fields are in a table?
- List records where Status is 'Done' in table tblXXX
- Find records created last week in table tblXXX
- Show me records updated in the last 30 days in base appXXX

## Unsupported questions

The Airtable connector isn't currently able to handle prompts like these.

- Create a new record in Airtable
- Update a record in Airtable
- Delete a record from Airtable
- Create a new table
- Modify table schema

## Installation

```bash
uv pip install airbyte-agent-sdk
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_sdk.connectors.airtable import AirtableConnector
from airbyte_agent_sdk.connectors.airtable.models import AirtableAuthConfig

connector = AirtableConnector(
    auth_config=AirtableAuthConfig(
        personal_access_token="<Airtable Personal Access Token. See https://airtable.com/developers/web/guides/personal-access-tokens>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@AirtableConnector.tool_utils
async def airtable_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

The `connect()` factory returns a fully typed `AirtableConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:

```python
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.airtable import AirtableConnector

connector = connect("airtable", workspace_name="<your_workspace_name>")

@agent.tool_plain # assumes you're using Pydantic AI
@AirtableConnector.tool_utils
async def airtable_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

```python
from airbyte_agent_sdk.connectors.airtable import AirtableConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AirtableConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@AirtableConnector.tool_utils
async def airtable_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Bases | [List](./REFERENCE.md#bases-list), [Context Store Search](./REFERENCE.md#bases-context-store-search) |
| Tables | [List](./REFERENCE.md#tables-list), [Context Store Search](./REFERENCE.md#tables-context-store-search) |
| Records | [List](./REFERENCE.md#records-list), [Get](./REFERENCE.md#records-get) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Airtable API docs

See the official [Airtable API reference](https://airtable.com/developers/web/api/introduction).

## Version information

- **Package version:** 1.0.8
- **Connector version:** 1.0.8
- **Generated with Connector SDK commit SHA:** unknown