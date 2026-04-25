# Zoho-Crm

The Zoho-Crm agent connector is a Python package that equips AI agents to interact with Zoho-Crm through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Zoho CRM API, providing access to CRM modules including leads, contacts, accounts, deals, campaigns, tasks, events, calls, products, quotes, and invoices. Supports OAuth 2.0 authentication with regional data center support (US, EU, AU, IN, CN, JP). Supports read operations (list and get) for all entities, and write operations (create and update) for leads, contacts, accounts, deals, and tasks.


## Example questions

The Zoho-Crm connector is optimized to handle prompts like these.

- List all leads
- Show me details for a specific lead
- List all contacts
- List all accounts
- List all open deals
- Show me details for a specific deal
- List all campaigns
- List all tasks
- List all events
- List recent calls
- List all products
- List all quotes
- List all invoices
- Create a new lead named John Smith at Acme Corp
- Update the status of lead to Contacted
- Create a new contact with email jane@example.com
- Create a new account called Global Industries
- Create a deal called Enterprise License worth $50,000
- Update the deal stage to Closed Won
- Create a task to follow up with the client
- Update the task priority to High
- Show me leads created in the last 30 days
- Which deals have the highest amount?
- List all contacts at a specific company
- What is the total revenue across all deals by stage?
- Show me overdue tasks
- Which campaigns generated the most leads?
- Summarize the deal pipeline by stage
- Show me accounts with the highest annual revenue
- List all events scheduled for this week
- What are the top-performing products by unit price?
- Show me all invoices that are past due
- Break down leads by source and industry

## Unsupported questions

The Zoho-Crm connector isn't currently able to handle prompts like these.

- Delete a deal record
- Send an email to a lead
- Convert a lead to a contact
- Merge duplicate contacts
- Bulk import leads from CSV
- Create a workflow rule

## Installation

```bash
uv pip install airbyte-agent-sdk
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector
from airbyte_agent_sdk.connectors.zoho_crm.models import ZohoCrmAuthConfig

connector = ZohoCrmConnector(
    auth_config=ZohoCrmAuthConfig(
        client_id="<OAuth 2.0 Client ID from Zoho Developer Console>",
        client_secret="<OAuth 2.0 Client Secret from Zoho Developer Console>",
        refresh_token="<OAuth 2.0 Refresh Token (does not expire)>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@ZohoCrmConnector.tool_utils
async def zoho_crm_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector, AirbyteAuthConfig

connector = ZohoCrmConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@ZohoCrmConnector.tool_utils
async def zoho_crm_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Leads | [List](./REFERENCE.md#leads-list), [Create](./REFERENCE.md#leads-create), [Get](./REFERENCE.md#leads-get), [Update](./REFERENCE.md#leads-update), [Context Store Search](./REFERENCE.md#leads-context-store-search) |
| Contacts | [List](./REFERENCE.md#contacts-list), [Create](./REFERENCE.md#contacts-create), [Get](./REFERENCE.md#contacts-get), [Update](./REFERENCE.md#contacts-update), [Context Store Search](./REFERENCE.md#contacts-context-store-search) |
| Accounts | [List](./REFERENCE.md#accounts-list), [Create](./REFERENCE.md#accounts-create), [Get](./REFERENCE.md#accounts-get), [Update](./REFERENCE.md#accounts-update), [Context Store Search](./REFERENCE.md#accounts-context-store-search) |
| Deals | [List](./REFERENCE.md#deals-list), [Create](./REFERENCE.md#deals-create), [Get](./REFERENCE.md#deals-get), [Update](./REFERENCE.md#deals-update), [Context Store Search](./REFERENCE.md#deals-context-store-search) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Get](./REFERENCE.md#campaigns-get), [Context Store Search](./REFERENCE.md#campaigns-context-store-search) |
| Tasks | [List](./REFERENCE.md#tasks-list), [Create](./REFERENCE.md#tasks-create), [Get](./REFERENCE.md#tasks-get), [Update](./REFERENCE.md#tasks-update), [Context Store Search](./REFERENCE.md#tasks-context-store-search) |
| Events | [List](./REFERENCE.md#events-list), [Get](./REFERENCE.md#events-get), [Context Store Search](./REFERENCE.md#events-context-store-search) |
| Calls | [List](./REFERENCE.md#calls-list), [Get](./REFERENCE.md#calls-get), [Context Store Search](./REFERENCE.md#calls-context-store-search) |
| Products | [List](./REFERENCE.md#products-list), [Get](./REFERENCE.md#products-get), [Context Store Search](./REFERENCE.md#products-context-store-search) |
| Quotes | [List](./REFERENCE.md#quotes-list), [Get](./REFERENCE.md#quotes-get), [Context Store Search](./REFERENCE.md#quotes-context-store-search) |
| Invoices | [List](./REFERENCE.md#invoices-list), [Get](./REFERENCE.md#invoices-get), [Context Store Search](./REFERENCE.md#invoices-context-store-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Zoho-Crm API docs

See the official [Zoho-Crm API reference](https://www.zoho.com/crm/developer/docs/api/v2/).

## Version information

- **Package version:** 1.0.3
- **Connector version:** 1.0.3
- **Generated with Connector SDK commit SHA:** unknown