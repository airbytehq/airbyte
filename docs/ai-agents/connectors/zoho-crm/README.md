# Zoho-Crm

The Zoho-Crm agent connector is a Python package that equips AI agents to interact with Zoho-Crm through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Zoho CRM API, providing access to CRM modules including leads, contacts, accounts, deals, campaigns, tasks, events, calls, products, quotes, and invoices. Supports OAuth 2.0 authentication with regional data center support (US, EU, AU, IN, CN, JP). Read-only operations (list and get) are supported for all entities.


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

- Create a new lead in Zoho CRM
- Update a contact's email address
- Delete a deal record
- Send an email to a lead
- Convert a lead to a contact
- Merge duplicate contacts

## Installation

```bash
uv pip install airbyte-agent-zoho-crm
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_zoho_crm import ZohoCrmConnector
from airbyte_agent_zoho_crm.models import ZohoCrmAuthConfig

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
from airbyte_agent_zoho_crm import ZohoCrmConnector, AirbyteAuthConfig

connector = ZohoCrmConnector(
    auth_config=AirbyteAuthConfig(
        customer_name="<your_customer_name>",
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
| Leads | [List](./REFERENCE.md#leads-list), [Get](./REFERENCE.md#leads-get), [Search](./REFERENCE.md#leads-search) |
| Contacts | [List](./REFERENCE.md#contacts-list), [Get](./REFERENCE.md#contacts-get), [Search](./REFERENCE.md#contacts-search) |
| Accounts | [List](./REFERENCE.md#accounts-list), [Get](./REFERENCE.md#accounts-get), [Search](./REFERENCE.md#accounts-search) |
| Deals | [List](./REFERENCE.md#deals-list), [Get](./REFERENCE.md#deals-get), [Search](./REFERENCE.md#deals-search) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Get](./REFERENCE.md#campaigns-get), [Search](./REFERENCE.md#campaigns-search) |
| Tasks | [List](./REFERENCE.md#tasks-list), [Get](./REFERENCE.md#tasks-get), [Search](./REFERENCE.md#tasks-search) |
| Events | [List](./REFERENCE.md#events-list), [Get](./REFERENCE.md#events-get), [Search](./REFERENCE.md#events-search) |
| Calls | [List](./REFERENCE.md#calls-list), [Get](./REFERENCE.md#calls-get), [Search](./REFERENCE.md#calls-search) |
| Products | [List](./REFERENCE.md#products-list), [Get](./REFERENCE.md#products-get), [Search](./REFERENCE.md#products-search) |
| Quotes | [List](./REFERENCE.md#quotes-list), [Get](./REFERENCE.md#quotes-get), [Search](./REFERENCE.md#quotes-search) |
| Invoices | [List](./REFERENCE.md#invoices-list), [Get](./REFERENCE.md#invoices-get), [Search](./REFERENCE.md#invoices-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Zoho-Crm API docs

See the official [Zoho-Crm API reference](https://www.zoho.com/crm/developer/docs/api/v2/).

## Version information

- **Package version:** 0.1.6
- **Connector version:** 1.0.2
- **Generated with Connector SDK commit SHA:** 75f388847745be753ab20224c66697e1d4a84347
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/zoho-crm/CHANGELOG.md)