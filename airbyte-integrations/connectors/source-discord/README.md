# Source Discord

This is the repository for the Discord source connector, written in the declarative YAML framework.
For information about how to use this connector within Airbyte, see [the user-facing documentation](https://docs.airbyte.com/integrations/sources/discord).

## Local development

### Prerequisites

- A Discord Bot Token (create one at [Discord Developer Portal](https://discord.com/developers/applications))
- The bot must be invited to target guilds with appropriate permissions

### Building and running

No local build steps are required for manifest-only connectors.
To test changes locally, use the Connector Builder in the Airbyte UI or the Airbyte CDK CLI tools.

For general information about developing declarative connectors, see the
[Connector Builder documentation](https://docs.airbyte.com/connector-development/connector-builder-ui/overview).

### Running unit tests

```bash
cd airbyte-integrations/connectors/source-discord
python -m pytest unit_tests/ -v
```
