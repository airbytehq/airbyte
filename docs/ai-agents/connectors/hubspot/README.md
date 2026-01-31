# Hubspot agent connector

HubSpot is a CRM platform that provides tools for marketing, sales, customer service,
and content management. This connector provides access to contacts, companies, deals,
tickets, and custom objects for customer relationship management and sales analytics.


## Example questions

The Hubspot connector is optimized to handle prompts like these.

- Show me all deals from \{company\} this quarter
- What are the top 5 most valuable deals in my pipeline right now?
- List recent tickets from \{customer\} and analyze their support trends
- Search for contacts in the marketing department at \{company\}
- Give me an overview of my sales team's deals in the last 30 days
- Identify the most active companies in our CRM this month
- Compare the number of deals closed by different sales representatives
- Find all tickets related to a specific product issue and summarize their status

## Unsupported questions

The Hubspot connector isn't currently able to handle prompts like these.

- Create a new contact record for \{person\}
- Update the contact information for \{customer\}
- Delete the ticket from last week's support case
- Schedule a follow-up task for this deal
- Send an email to all contacts in the sales pipeline

## Installation

```bash
uv pip install airbyte-agent-hubspot
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_hubspot import HubspotConnector
from airbyte_agent_hubspot.models import HubspotAuthConfig

connector = HubspotConnector(
    auth_config=HubspotAuthConfig(
        client_id="<Your HubSpot OAuth2 Client ID>",
        client_secret="<Your HubSpot OAuth2 Client Secret>",
        refresh_token="<Your HubSpot OAuth2 Refresh Token>",
        access_token="<Your HubSpot OAuth2 Access Token (optional if refresh_token is provided)>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@HubspotConnector.tool_utils
async def hubspot_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_hubspot import HubspotConnector

connector = HubspotConnector(
    external_user_id="<your_external_user_id>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@HubspotConnector.tool_utils
async def hubspot_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Contacts | [List](./REFERENCE.md#contacts-list), [Get](./REFERENCE.md#contacts-get), [API Search](./REFERENCE.md#contacts-api_search) |
| Companies | [List](./REFERENCE.md#companies-list), [Get](./REFERENCE.md#companies-get), [API Search](./REFERENCE.md#companies-api_search) |
| Deals | [List](./REFERENCE.md#deals-list), [Get](./REFERENCE.md#deals-get), [API Search](./REFERENCE.md#deals-api_search) |
| Tickets | [List](./REFERENCE.md#tickets-list), [Get](./REFERENCE.md#tickets-get), [API Search](./REFERENCE.md#tickets-api_search) |
| Schemas | [List](./REFERENCE.md#schemas-list), [Get](./REFERENCE.md#schemas-get) |
| Objects | [List](./REFERENCE.md#objects-list), [Get](./REFERENCE.md#objects-get) |


### Authentication and configuration

For all authentication and configuration options, see the connector's [authentication documentation](AUTH.md).

### Hubspot API docs

See the official [Hubspot API reference](https://developers.hubspot.com/docs/api/crm/understanding-the-crm).

## Version information

- **Package version:** 0.15.76
- **Connector version:** 0.1.9
- **Generated with Connector SDK commit SHA:** b184da3e22ef8521d2eeebf3c96a0fe8da2424f5
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/hubspot/CHANGELOG.md)