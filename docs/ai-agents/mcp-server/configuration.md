---
sidebar_label: "Configuration"
sidebar_position: 2
---

# Configure the MCP server

The Agent Engine MCP server is configured with a YAML file that specifies which connector to use and how to authenticate. This page covers the configuration file format, the two execution modes, credential management, and aggregate configurations for running multiple connectors.

## Configuration file format

A connector configuration file has two required sections:

```yaml
connector:
  package: airbyte-agent-gong
credentials:
  access_key: ${env.GONG_ACCESS_KEY}
  access_key_secret: ${env.GONG_ACCESS_KEY_SECRET}
```

- **`connector`**: Specifies the connector source. This can be a PyPI package, a git URL, a local path, or an Airbyte Cloud connector ID.
- **`credentials`**: A key-value map of authentication fields. Values use `${env.VAR_NAME}` syntax to reference environment variables.

Some connectors also accept a **`config`** section for additional parameters like subdomains or workspace IDs. The `adp connectors configure` command generates the correct structure for each connector.

## Open source mode

In open source mode, the MCP server installs a connector package and calls the third-party API directly using your credentials. This mode supports the operations that the API provides, such as list and get by ID.

### PyPI packages

The most common configuration. Specify a package name from the Airbyte connector registry:

```yaml
connector:
  package: airbyte-agent-gong
credentials:
  access_key: ${env.GONG_ACCESS_KEY}
  access_key_secret: ${env.GONG_ACCESS_KEY_SECRET}
```

To pin a specific version:

```yaml
connector:
  package: airbyte-agent-gong
  version: 0.1.13
credentials:
  access_key: ${env.GONG_ACCESS_KEY}
  access_key_secret: ${env.GONG_ACCESS_KEY_SECRET}
```

Run `uv run adp connectors list-oss` to see available packages and their versions.

### Git URLs

Point the connector to a git repository:

```yaml
connector:
  git: https://github.com/org/repo.git
credentials:
  token: ${env.MY_TOKEN}
```

You can specify a branch or tag with `ref` and a subdirectory with `subdirectory`:

```yaml
connector:
  git: https://github.com/org/repo.git
  ref: main
  subdirectory: connectors/my-connector
credentials:
  token: ${env.MY_TOKEN}
```

### Local paths

Point the connector to a local directory:

```yaml
connector:
  path: ../integrations/my-connector/.generated
credentials:
  token: ${env.MY_TOKEN}
```

This is useful during connector development.

## Hosted mode

In hosted mode, the MCP server calls the Airbyte Cloud API instead of the third-party API directly. This mode supports arbitrary search and filter queries across all entities because Airbyte Cloud keeps data indexed in the [context store](../platform/context-store).

```yaml
connector:
  connector_id: <your-connector-id>
credentials:
  airbyte_client_id: ${env.AIRBYTE_CLIENT_ID}
  airbyte_client_secret: ${env.AIRBYTE_CLIENT_SECRET}
```

You can combine a connector ID with a package source to get both hosted search and local execution:

```yaml
connector:
  package: airbyte-agent-gong
  connector_id: <your-connector-id>
credentials:
  airbyte_client_id: ${env.AIRBYTE_CLIENT_ID}
  airbyte_client_secret: ${env.AIRBYTE_CLIENT_SECRET}
```

To generate a hosted mode configuration:

```bash
uv run adp connectors configure --connector-id <your-connector-id>
```

Run `uv run adp connectors list-cloud` to see connectors available in your Airbyte Cloud organization. Use `--customer` to filter by customer name:

```bash
uv run adp connectors list-cloud --customer acme
```

## Credential management

### Environment variable interpolation

Credential values use `${env.VAR_NAME}` syntax. The MCP server resolves these placeholders at startup by reading from the process environment.

```yaml
credentials:
  access_key: ${env.GONG_ACCESS_KEY}
  access_key_secret: ${env.GONG_ACCESS_KEY_SECRET}
```

If a referenced variable is not set, the server raises an error.

### The .env file

The `adp` CLI automatically loads `.env` files from the current working directory. Create a `.env` file alongside your connector configuration:

```text title=".env"
GONG_ACCESS_KEY=your-access-key
GONG_ACCESS_KEY_SECRET=your-secret
```

:::warning
Never commit your `.env` file to version control. Add `.env` to your `.gitignore` file. If you commit credentials by mistake, rotate them immediately.
:::

### Organization login

For Airbyte Cloud connectors, you can save your credentials globally instead of using a `.env` file:

```bash
uv run adp login <organization-id>
```

This prints a link to the Airbyte authentication page for your organization, then prompts for your Client ID and Secret. Credentials are saved to `~/.airbyte_agent_mcp/orgs/<organization-id>/.env` and the organization is set as the default.

You can log into multiple organizations and switch between them:

```bash
uv run adp orgs list                  # List logged-in organizations
uv run adp orgs default <org-id>      # Set the default organization
uv run adp --org <org-id> <command>   # Override for a single command
```

## Aggregate configurations

An aggregate configuration lets you run multiple connectors in a single MCP server. Create a YAML file that references your individual connector config files:

```yaml title="connectors.yaml"
name: airbyte-crm-suite
configs:
  - connector-gong-package.yaml
  - connector-salesforce-cloud.yaml
```

The `name` field sets the MCP server name. The `configs` field lists paths to individual connector configuration files (relative to the aggregate file's directory).

Register the aggregate config with your agent the same way you would a single connector:

```bash
uv run adp mcp add-to claude-code connectors.yaml
```

## CLI reference

All commands use `uv run adp <command>`. Use `--help` on any command for full options.

### `adp connectors list-oss`

List available open source connectors from the Airbyte registry.

```bash
uv run adp connectors list-oss
uv run adp connectors list-oss --pattern salesforce
```

### `adp connectors list-cloud`

List connectors configured in your Airbyte Cloud organization. Requires `adp login` first.

```bash
uv run adp connectors list-cloud
uv run adp connectors list-cloud --customer acme
```

### `adp connectors configure`

Generate a connector configuration file by inspecting the connector's authentication requirements.

```bash
uv run adp connectors configure --package airbyte-agent-gong
uv run adp connectors configure --package airbyte-agent-gong --version 0.1.13
uv run adp connectors configure --connector-id <id>
uv run adp connectors configure --package airbyte-agent-gong --filename my-gong.yaml
```

| Flag | Description |
| --- | --- |
| `--package` | PyPI package name, local path, or `git+https://` URL |
| `--connector-id`, `-c` | Airbyte Cloud connector ID |
| `--version`, `-v` | Package version (PyPI only) |
| `--filename`, `-f` | Output file path (auto-generated if not specified) |
| `--overwrite`, `-o` | Overwrite the output file if it already exists |

### `adp login`

Save Airbyte Cloud credentials to the global config directory.

```bash
uv run adp login <organization-id>
```

### `adp orgs`

Manage logged-in organizations.

```bash
uv run adp orgs list                 # List all logged-in organizations
uv run adp orgs default              # Show the default organization
uv run adp orgs default <org-id>     # Set the default organization
```
