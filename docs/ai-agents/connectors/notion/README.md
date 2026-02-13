# Notion

The Notion agent connector is a Python package that equips AI agents to interact with Notion through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Notion is an all-in-one workspace for notes, docs, wikis, projects, and collaboration.
This connector provides read access to Notion workspaces including users, pages, databases,
blocks, and comments through the Notion REST API. It enables querying workspace structure,
page content, database schemas, and collaboration data for productivity analysis and
content management insights.


## Example questions

The Notion connector is optimized to handle prompts like these.

- List all users in my Notion workspace
- Show me all pages in my Notion workspace
- What databases exist in my Notion workspace?
- Get the details of a specific page by ID
- List child blocks of a specific page
- Show me comments on a specific page
- What is the schema of a specific database?
- Who are the bot users in my workspace?
- Find pages created in the last week
- List databases that have been recently edited
- Show me all archived pages

## Unsupported questions

The Notion connector isn't currently able to handle prompts like these.

- Create a new page in Notion
- Update a database property
- Delete a block
- Add a comment to a page

## Installation

```bash
uv pip install airbyte-agent-notion
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_notion import NotionConnector
from airbyte_agent_notion.models import NotionAuthConfig

connector = NotionConnector(
    auth_config=NotionAuthConfig(
        token="<Notion internal integration token (starts with ntn_ or secret_)>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@NotionConnector.tool_utils
async def notion_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_notion import NotionConnector, AirbyteAuthConfig

connector = NotionConnector(
    auth_config=AirbyteAuthConfig(
        external_user_id="<your_external_user_id>",
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@NotionConnector.tool_utils
async def notion_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get), [Search](./REFERENCE.md#users-search) |
| Pages | [List](./REFERENCE.md#pages-list), [Get](./REFERENCE.md#pages-get), [Search](./REFERENCE.md#pages-search) |
| Databases | [List](./REFERENCE.md#databases-list), [Get](./REFERENCE.md#databases-get), [Search](./REFERENCE.md#databases-search) |
| Blocks | [List](./REFERENCE.md#blocks-list), [Get](./REFERENCE.md#blocks-get), [Search](./REFERENCE.md#blocks-search) |
| Comments | [List](./REFERENCE.md#comments-list) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Notion API docs

See the official [Notion API reference](https://developers.notion.com/reference/intro).

## Version information

- **Package version:** 0.1.0
- **Connector version:** 0.1.1
- **Generated with Connector SDK commit SHA:** 04a4f347a8f30c6f4f322ba94180755cc4359e49
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/notion/CHANGELOG.md)