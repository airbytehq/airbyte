# Harvest

The Harvest agent connector is a Python package that equips AI agents to interact with Harvest through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Harvest time-tracking and invoicing API (v2). Provides read access
to time tracking data including users, clients, projects, tasks, time entries, invoices,
estimates, expenses, and more. Harvest is a cloud-based time tracking and invoicing
solution that helps teams track time, manage projects, and streamline invoicing.


## Example questions

The Harvest connector is optimized to handle prompts like these.

- List all users in Harvest
- Show me all active projects
- List all clients
- Show me recent time entries
- List all invoices
- Show me all tasks
- List all expense categories
- Get company information
- How many hours were logged last week?
- Which projects have the most time entries?
- Show me all unbilled time entries
- What are the active projects for a specific client?
- List all overdue invoices
- Which users logged the most hours this month?

## Unsupported questions

The Harvest connector isn't currently able to handle prompts like these.

- Create a new time entry in Harvest
- Update a project budget
- Delete an invoice
- Start a timer for a task

## Installation

```bash
uv pip install airbyte-agent-harvest
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_harvest import HarvestConnector
from airbyte_agent_harvest.models import HarvestPersonalAccessTokenAuthConfig

connector = HarvestConnector(
    auth_config=HarvestPersonalAccessTokenAuthConfig(
        token="<Your Harvest personal access token>",
        account_id="<Your Harvest account ID>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@HarvestConnector.tool_utils
async def harvest_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_harvest import HarvestConnector, AirbyteAuthConfig

connector = HarvestConnector(
    auth_config=AirbyteAuthConfig(
        customer_name="<your_customer_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@HarvestConnector.tool_utils
async def harvest_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get), [Search](./REFERENCE.md#users-search) |
| Clients | [List](./REFERENCE.md#clients-list), [Get](./REFERENCE.md#clients-get), [Search](./REFERENCE.md#clients-search) |
| Contacts | [List](./REFERENCE.md#contacts-list), [Get](./REFERENCE.md#contacts-get), [Search](./REFERENCE.md#contacts-search) |
| Company | [Get](./REFERENCE.md#company-get), [Search](./REFERENCE.md#company-search) |
| Projects | [List](./REFERENCE.md#projects-list), [Get](./REFERENCE.md#projects-get), [Search](./REFERENCE.md#projects-search) |
| Tasks | [List](./REFERENCE.md#tasks-list), [Get](./REFERENCE.md#tasks-get), [Search](./REFERENCE.md#tasks-search) |
| Time Entries | [List](./REFERENCE.md#time-entries-list), [Get](./REFERENCE.md#time-entries-get), [Search](./REFERENCE.md#time-entries-search) |
| Invoices | [List](./REFERENCE.md#invoices-list), [Get](./REFERENCE.md#invoices-get), [Search](./REFERENCE.md#invoices-search) |
| Invoice Item Categories | [List](./REFERENCE.md#invoice-item-categories-list), [Get](./REFERENCE.md#invoice-item-categories-get), [Search](./REFERENCE.md#invoice-item-categories-search) |
| Estimates | [List](./REFERENCE.md#estimates-list), [Get](./REFERENCE.md#estimates-get), [Search](./REFERENCE.md#estimates-search) |
| Estimate Item Categories | [List](./REFERENCE.md#estimate-item-categories-list), [Get](./REFERENCE.md#estimate-item-categories-get), [Search](./REFERENCE.md#estimate-item-categories-search) |
| Expenses | [List](./REFERENCE.md#expenses-list), [Get](./REFERENCE.md#expenses-get), [Search](./REFERENCE.md#expenses-search) |
| Expense Categories | [List](./REFERENCE.md#expense-categories-list), [Get](./REFERENCE.md#expense-categories-get), [Search](./REFERENCE.md#expense-categories-search) |
| Roles | [List](./REFERENCE.md#roles-list), [Get](./REFERENCE.md#roles-get), [Search](./REFERENCE.md#roles-search) |
| User Assignments | [List](./REFERENCE.md#user-assignments-list), [Search](./REFERENCE.md#user-assignments-search) |
| Task Assignments | [List](./REFERENCE.md#task-assignments-list), [Search](./REFERENCE.md#task-assignments-search) |
| Time Projects | [List](./REFERENCE.md#time-projects-list), [Search](./REFERENCE.md#time-projects-search) |
| Time Tasks | [List](./REFERENCE.md#time-tasks-list), [Search](./REFERENCE.md#time-tasks-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Harvest API docs

See the official [Harvest API reference](https://help.getharvest.com/api-v2/).

## Version information

- **Package version:** 0.1.8
- **Connector version:** 1.0.2
- **Generated with Connector SDK commit SHA:** 75f388847745be753ab20224c66697e1d4a84347
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/harvest/CHANGELOG.md)