# Asana

Asana is a REST based API. Connector is implemented with [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

Asana API by default returns 3 fields for each record: `gid`, `name`, `resource_type`.
If you want to get additional fields you need to specify those fields in each request.

See [this](https://docs.airbyte.io/integrations/sources/asana) link for the nuances about the connector.
