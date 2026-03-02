# Incident-Io

The Incident-Io agent connector is a Python package that equips AI agents to interact with Incident-Io through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connect to the incident.io API to access incident management data including
incidents, alerts, escalations, users, schedules, and more. incident.io is an
on-call, status pages, and incident response platform. This connector provides
read-only access to core incident management entities via the v1 and v2 APIs.
Requires an API key from your incident.io dashboard (Pro plan or above).


## Example questions

The Incident-Io connector is optimized to handle prompts like these.

- List all incidents
- Show all open incidents
- List all alerts
- Show all users
- List all escalations
- Show all on-call schedules
- List all severities
- Show all incident statuses
- List all custom fields
- Which incidents were created this week?
- What are the most recent high-severity incidents?
- Who is currently on-call?
- How many incidents are in triage status?
- What incidents were updated today?

## Unsupported questions

The Incident-Io connector isn't currently able to handle prompts like these.

- Create a new incident
- Update an incident's severity
- Delete an alert
- Assign someone to an incident role

## Installation

```bash
uv pip install airbyte-agent-incident-io
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_incident_io import IncidentIoConnector
from airbyte_agent_incident_io.models import IncidentIoAuthConfig

connector = IncidentIoConnector(
    auth_config=IncidentIoAuthConfig(
        api_key="<Your incident.io API key. Create one at https://app.incident.io/settings/api-keys>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@IncidentIoConnector.tool_utils
async def incident_io_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_incident_io import IncidentIoConnector, AirbyteAuthConfig

connector = IncidentIoConnector(
    auth_config=AirbyteAuthConfig(
        customer_name="<your_customer_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@IncidentIoConnector.tool_utils
async def incident_io_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Incidents | [List](./REFERENCE.md#incidents-list), [Get](./REFERENCE.md#incidents-get), [Search](./REFERENCE.md#incidents-search) |
| Alerts | [List](./REFERENCE.md#alerts-list), [Get](./REFERENCE.md#alerts-get), [Search](./REFERENCE.md#alerts-search) |
| Escalations | [List](./REFERENCE.md#escalations-list), [Get](./REFERENCE.md#escalations-get), [Search](./REFERENCE.md#escalations-search) |
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get), [Search](./REFERENCE.md#users-search) |
| Incident Updates | [List](./REFERENCE.md#incident-updates-list), [Search](./REFERENCE.md#incident-updates-search) |
| Incident Roles | [List](./REFERENCE.md#incident-roles-list), [Get](./REFERENCE.md#incident-roles-get), [Search](./REFERENCE.md#incident-roles-search) |
| Incident Statuses | [List](./REFERENCE.md#incident-statuses-list), [Get](./REFERENCE.md#incident-statuses-get), [Search](./REFERENCE.md#incident-statuses-search) |
| Incident Timestamps | [List](./REFERENCE.md#incident-timestamps-list), [Get](./REFERENCE.md#incident-timestamps-get), [Search](./REFERENCE.md#incident-timestamps-search) |
| Severities | [List](./REFERENCE.md#severities-list), [Get](./REFERENCE.md#severities-get), [Search](./REFERENCE.md#severities-search) |
| Custom Fields | [List](./REFERENCE.md#custom-fields-list), [Get](./REFERENCE.md#custom-fields-get), [Search](./REFERENCE.md#custom-fields-search) |
| Catalog Types | [List](./REFERENCE.md#catalog-types-list), [Get](./REFERENCE.md#catalog-types-get), [Search](./REFERENCE.md#catalog-types-search) |
| Schedules | [List](./REFERENCE.md#schedules-list), [Get](./REFERENCE.md#schedules-get), [Search](./REFERENCE.md#schedules-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Incident-Io API docs

See the official [Incident-Io API reference](https://api-docs.incident.io/).

## Version information

- **Package version:** 0.1.0
- **Connector version:** 1.0.1
- **Generated with Connector SDK commit SHA:** 7cd2cc4e688e626633336d4f04a0999d41718d2b
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/incident-io/CHANGELOG.md)