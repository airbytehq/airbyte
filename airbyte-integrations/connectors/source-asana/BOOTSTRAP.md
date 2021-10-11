# Asana

Asana is a project management platform designed to organize and manage teams and their work.
This connector adds ability to fetch projects, tasks, teams etc over REST API.
Connector is implemented with [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

Some streams depend on:
- workspaces (Teams, Users, CustomFields, Projects, Tags, Users streams);
- projects (Sections, Tasks streams);
- tasks (Stories stream);
- teams (TeamMemberships stream).

Each record can be uniquely identified by a `gid` key.
Asana API by default returns 3 fields for each record: `gid`, `name`, `resource_type`.
Because of that if we want to get additional fields we need to specify those fields in each request.
For this purpose there is `get_opt_fields()` function.
It goes through stream's schema and forms a set of fields to return for each request.

Requests that hit any of Asana rate limits will receive a `429 Too Many Requests` response, which contains the standard Retry-After header indicating how many seconds the client should wait before retrying the request.

[Here](https://developers.asana.com/docs/pagination) is a link with info on how pagination is implemented.

See [this](https://docs.airbyte.io/integrations/sources/asana) link for the nuances about the connector.
