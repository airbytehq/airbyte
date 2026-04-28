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
uv pip install airbyte-agent-sdk
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_sdk.connectors.ashby import AshbyConnector
from airbyte_agent_sdk.connectors.ashby.models import AshbyAuthConfig

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
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

The `connect()` factory returns a fully typed `AshbyConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:

```python
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.ashby import AshbyConnector

connector = connect("ashby", workspace_name="<your_workspace_name>")

@agent.tool_plain # assumes you're using Pydantic AI
@AshbyConnector.tool_utils
async def ashby_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

```python
from airbyte_agent_sdk.connectors.ashby import AshbyConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AshbyConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
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
| Candidates | [List](./REFERENCE.md#candidates-list), [Get](./REFERENCE.md#candidates-get), [Context Store Search](./REFERENCE.md#candidates-context-store-search) |
| Applications | [List](./REFERENCE.md#applications-list), [Get](./REFERENCE.md#applications-get), [Context Store Search](./REFERENCE.md#applications-context-store-search) |
| Jobs | [List](./REFERENCE.md#jobs-list), [Get](./REFERENCE.md#jobs-get), [Context Store Search](./REFERENCE.md#jobs-context-store-search) |
| Departments | [List](./REFERENCE.md#departments-list), [Get](./REFERENCE.md#departments-get) |
| Locations | [List](./REFERENCE.md#locations-list), [Get](./REFERENCE.md#locations-get) |
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get), [Context Store Search](./REFERENCE.md#users-context-store-search) |
| Job Postings | [List](./REFERENCE.md#job-postings-list), [Get](./REFERENCE.md#job-postings-get), [Context Store Search](./REFERENCE.md#job-postings-context-store-search) |
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
- **Connector version:** 0.1.4
- **Generated with Connector SDK commit SHA:** unknown