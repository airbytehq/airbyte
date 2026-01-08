# Greenhouse agent connector

Greenhouse is an applicant tracking system (ATS) that helps companies manage their
hiring process. This connector provides access to candidates, applications, jobs,
offers, users, departments, offices, job posts, sources, and scheduled interviews
for recruiting analytics and talent acquisition insights.


## Example questions

The Greenhouse connector is optimized to handle prompts like these.

- Show me candidates from \{company\} who applied last month
- What are the top 5 sources for our job applications this quarter?
- List all open jobs in the Sales department
- Analyze the interview schedules for our engineering candidates this week
- Get details of recent job offers for \{team_member\}
- Compare the number of applications across different offices
- Identify candidates who have multiple applications in our system
- Show me upcoming scheduled interviews for our marketing positions
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

```python
from airbyte_agent_greenhouse import GreenhouseConnector, GreenhouseAuthConfig

connector = GreenhouseConnector(
  auth_config=GreenhouseAuthConfig(
    api_key="..."
  )
)
result = await connector.candidates.list()
```


## Full documentation

This connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Candidates | [List](./REFERENCE.md#candidates-list), [Get](./REFERENCE.md#candidates-get) |
| Applications | [List](./REFERENCE.md#applications-list), [Get](./REFERENCE.md#applications-get) |
| Jobs | [List](./REFERENCE.md#jobs-list), [Get](./REFERENCE.md#jobs-get) |
| Offers | [List](./REFERENCE.md#offers-list), [Get](./REFERENCE.md#offers-get) |
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get) |
| Departments | [List](./REFERENCE.md#departments-list), [Get](./REFERENCE.md#departments-get) |
| Offices | [List](./REFERENCE.md#offices-list), [Get](./REFERENCE.md#offices-get) |
| Job Posts | [List](./REFERENCE.md#job-posts-list), [Get](./REFERENCE.md#job-posts-get) |
| Sources | [List](./REFERENCE.md#sources-list) |
| Scheduled Interviews | [List](./REFERENCE.md#scheduled-interviews-list), [Get](./REFERENCE.md#scheduled-interviews-get) |
| Application Attachment | [Download](./REFERENCE.md#application-attachment-download) |
| Candidate Attachment | [Download](./REFERENCE.md#candidate-attachment-download) |


For detailed documentation on available actions and parameters, see this connector's [full reference documentation](./REFERENCE.md).

For the service's official API docs, see the [Greenhouse API reference](https://developers.greenhouse.io/harvest.html).

## Version information

- **Package version:** 0.17.28
- **Connector version:** 0.1.2
- **Generated with Connector SDK commit SHA:** d023e05f2b7a1ddabf81fab7640c64de1e0aa6a1