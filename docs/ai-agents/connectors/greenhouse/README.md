# Greenhouse

The Greenhouse agent connector is a Python package that equips AI agents to interact with Greenhouse through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Greenhouse is an applicant tracking system (ATS) that helps companies manage their
hiring process. This connector provides access to candidates, applications, jobs,
offers, users, departments, offices, job posts, sources, and scheduled interviews
for recruiting analytics and talent acquisition insights.


## Example questions

The Greenhouse connector is optimized to handle prompts like these.

- List all open jobs
- Show me upcoming interviews this week
- Show me recent job offers
- List recent applications
- Show me candidates from \{company\} who applied last month
- What are the top 5 sources for our job applications this quarter?
- Analyze the interview schedules for our engineering candidates this week
- Compare the number of applications across different offices
- Identify candidates who have multiple applications in our system
- Summarize the candidate pipeline for our latest job posting
- Find the most active departments in recruiting this month

## Unsupported questions

The Greenhouse connector isn't currently able to handle prompts like these.

- Create a new job posting for the marketing team
- Schedule an interview for \{candidate\}
- Update the status of \{candidate\}'s application
- Delete a candidate profile
- Send an offer letter to \{candidate\}
- Edit the details of a job description

## Installation

```bash
uv pip install airbyte-agent-greenhouse
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_greenhouse import GreenhouseConnector
from airbyte_agent_greenhouse.models import GreenhouseAuthConfig

connector = GreenhouseConnector(
    auth_config=GreenhouseAuthConfig(
        api_key="<Your Greenhouse Harvest API Key from the Dev Center>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@GreenhouseConnector.tool_utils
async def greenhouse_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_greenhouse import GreenhouseConnector, AirbyteAuthConfig

connector = GreenhouseConnector(
    auth_config=AirbyteAuthConfig(
        external_user_id="<your_external_user_id>",
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@GreenhouseConnector.tool_utils
async def greenhouse_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Candidates | [List](./REFERENCE.md#candidates-list), [Get](./REFERENCE.md#candidates-get), [Search](./REFERENCE.md#candidates-search) |
| Applications | [List](./REFERENCE.md#applications-list), [Get](./REFERENCE.md#applications-get), [Search](./REFERENCE.md#applications-search) |
| Jobs | [List](./REFERENCE.md#jobs-list), [Get](./REFERENCE.md#jobs-get), [Search](./REFERENCE.md#jobs-search) |
| Offers | [List](./REFERENCE.md#offers-list), [Get](./REFERENCE.md#offers-get), [Search](./REFERENCE.md#offers-search) |
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get), [Search](./REFERENCE.md#users-search) |
| Departments | [List](./REFERENCE.md#departments-list), [Get](./REFERENCE.md#departments-get), [Search](./REFERENCE.md#departments-search) |
| Offices | [List](./REFERENCE.md#offices-list), [Get](./REFERENCE.md#offices-get), [Search](./REFERENCE.md#offices-search) |
| Job Posts | [List](./REFERENCE.md#job-posts-list), [Get](./REFERENCE.md#job-posts-get), [Search](./REFERENCE.md#job-posts-search) |
| Sources | [List](./REFERENCE.md#sources-list), [Search](./REFERENCE.md#sources-search) |
| Scheduled Interviews | [List](./REFERENCE.md#scheduled-interviews-list), [Get](./REFERENCE.md#scheduled-interviews-get) |
| Application Attachment | [Download](./REFERENCE.md#application-attachment-download) |
| Candidate Attachment | [Download](./REFERENCE.md#candidate-attachment-download) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Greenhouse API docs

See the official [Greenhouse API reference](https://developers.greenhouse.io/harvest.html).

## Version information

- **Package version:** 0.17.98
- **Connector version:** 0.1.6
- **Generated with Connector SDK commit SHA:** 8c602f77c94fa829be7c1e10d063c5234b17dbef
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/greenhouse/CHANGELOG.md)