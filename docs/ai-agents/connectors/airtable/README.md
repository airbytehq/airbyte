# Airtable agent connector

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
uv pip install airbyte-agent-airtable
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_airtable import AirtableConnector
from airbyte_agent_airtable.models import AirtableAuthConfig

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

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_airtable import AirtableConnector, AirbyteAuthConfig

connector = AirtableConnector(
    auth_config=AirbyteAuthConfig(
        external_user_id="<your_external_user_id>",
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
| Bases | [List](./REFERENCE.md#bases-list) |
| Tables | [List](./REFERENCE.md#tables-list) |
| Records | [List](./REFERENCE.md#records-list), [Get](./REFERENCE.md#records-get) |


### Authentication and configuration

For all authentication and configuration options, see the connector's [authentication documentation](AUTH.md).

### Airtable API docs

See the official [Airtable API reference](https://airtable.com/developers/web/api/introduction).

## Version information

- **Package version:** 0.1.21
- **Connector version:** 1.0.3
- **Generated with Connector SDK commit SHA:** e4f3b9c8a8118bfaa9d57578c64868c91cb9b3a4
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/airtable/CHANGELOG.md)