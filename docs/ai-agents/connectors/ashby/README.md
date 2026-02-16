# Ashby

The Ashby agent connector is a Python package that equips AI agents to interact with Ashby through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Ashby is a modern applicant tracking system (ATS) and recruiting platform that helps companies manage their hiring process. This connector provides access to candidates, applications, jobs, departments, locations, users, job postings, sources, archive reasons, candidate tags, custom fields, and feedback form definitions for talent acquisition analytics and hiring insights.


## Example questions

The Ashby connector is optimized to handle prompts like these.

- List all open jobs
- Show me all candidates
- List recent applications
- List all departments
- Show me all job postings
- List all users in the organization
- Show me candidates who applied last month
- What are the top sources for job applications?
- Compare the number of applications across different departments
- Find candidates with multiple applications
- Summarize the candidate pipeline for our latest job posting
- Find the most active departments in recruiting this month

## Unsupported questions

The Ashby connector isn't currently able to handle prompts like these.

- Create a new job posting
- Schedule an interview for a candidate
- Update a candidates application status
- Delete a candidate profile
- Send an offer letter to a candidate

## Installation

```bash
uv pip install airbyte-agent-ashby
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_ashby import AshbyConnector
from airbyte_agent_ashby.models import AshbyAuthConfig

connector = AshbyConnector(
    auth_config=AshbyAuthConfig(
        api_key="<Your Ashby API key>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@AshbyConnector.tool_utils
async def ashby_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_ashby import AshbyConnector, AirbyteAuthConfig

connector = AshbyConnector(
    auth_config=AirbyteAuthConfig(
        external_user_id="<your_external_user_id>",
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@AshbyConnector.tool_utils
async def ashby_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Candidates | [List](./REFERENCE.md#candidates-list), [Get](./REFERENCE.md#candidates-get) |
| Applications | [List](./REFERENCE.md#applications-list), [Get](./REFERENCE.md#applications-get) |
| Jobs | [List](./REFERENCE.md#jobs-list), [Get](./REFERENCE.md#jobs-get) |
| Departments | [List](./REFERENCE.md#departments-list), [Get](./REFERENCE.md#departments-get) |
| Locations | [List](./REFERENCE.md#locations-list), [Get](./REFERENCE.md#locations-get) |
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get) |
| Job Postings | [List](./REFERENCE.md#job-postings-list), [Get](./REFERENCE.md#job-postings-get) |
| Sources | [List](./REFERENCE.md#sources-list) |
| Archive Reasons | [List](./REFERENCE.md#archive-reasons-list) |
| Candidate Tags | [List](./REFERENCE.md#candidate-tags-list) |
| Custom Fields | [List](./REFERENCE.md#custom-fields-list) |
| Feedback Form Definitions | [List](./REFERENCE.md#feedback-form-definitions-list) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Ashby API docs

See the official [Ashby API reference](https://developers.ashbyhq.com/reference).

## Version information

- **Package version:** 0.1.4
- **Connector version:** 0.1.2
- **Generated with Connector SDK commit SHA:** 733df4ffbedca1d2e5e81b775a1e389a60446f67
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/ashby/CHANGELOG.md)