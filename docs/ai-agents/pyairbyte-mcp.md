---
products: embedded
---

# PyAirbyte MCP Server

> **NOTE:**
> This MCP server implementation is experimental and may change without notice between minor versions of PyAirbyte. The API may be modified or entirely refactored in future versions.

The PyAirbyte MCP (Model Context Protocol) server provides a standardized interface for managing Airbyte connectors through MCP-compatible clients. This experimental feature allows you to list connectors, validate configurations, and run sync operations using the MCP protocol.

## Getting Started with PyAirbyte MCP

To get started with the PyAirbyte MCP server, follow these steps:

1. Create a Dotenv secrets file.
2. Register the MCP server with your MCP client.
3. Test the MCP server connection using your MCP client.

### Step 1: Generate a Dotenv Secrets File

To get started with the PyAirbyte MCP server, you will need to create a dotenv file containing your Airbyte Cloud credentials, as well as credentials for any third-party services you wish to connect to via Airbyte.

Create a file named `~/.mcp/airbyte_mcp.env` with the following content:

```ini
# Airbyte Project Artifacts Directory
AIRBYTE_PROJECT_DIR=/path/to/any/writeable/project-dir

# Airbyte Cloud Credentials (Required for Airbyte Cloud Operations)
AIRBYTE_CLOUD_CLIENT_ID=your_api_key
AIRBYTE_CLOUD_CLIENT_SECRET=your_api_secret
AIRBYTE_CLOUD_WORKSPACE_ID=your_workspace_id

# API-Specific Credentials (Optional, depending on your connectors)

# For example, for a PostgreSQL source connector:
# POSTGRES_HOST=your_postgres_host
# POSTGRES_PORT=5432
# POSTGRES_DB=your_database_name
# POSTGRES_USER=your_database_user
# POSTGRES_PASSWORD=your_database_password

# For example, for a Stripe source connector:
# STRIPE_API_KEY=your_stripe_api_key
# STRIPE_API_SECRET=your_stripe_api_secret
# STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
```

Note:

1. You can add more environment variables to this file as needed for different connectors. To start, you only need to create the file and pass it to the MCP server.
2. Ensure that this file is kept secure, as it contains sensitive information. Your LLM *should never* be given direct access to this file or its contents.
3. The MCP tools will give your LLM the ability to view *which* variables are available, but it does not give access to their values.
4. The `AIRBYTE_PROJECT_DIR` variable specifies a directory where the MCP server can store temporary project files. Ensure this directory is writable by the user running the MCP server.

### Step 2: Registering the MCP Server

First install `uv` (`brew install uv`).

Then, create a file named `server_config.json` (or the file name required by your MCP client) with the following content. This uses `uvx` (from `brew install uv`) to run the MCP server. If a matching version Python is not yet installed, a `uv`-managed Python version will be installed automatically. This will also auto-update to use the "latest" Airbyte MCP release at time of launch. You can alternatively pin to a specific version of Python and/or of the Airbyte library if you have special requirements.

```json
{
  "mcpServers": {
    "airbyte": {
      "command": "uvx",
      "args": [
        "--python=3.11",
        "--from=airbyte@latest",
        "airbyte-mcp"
      ],
      "env": {
        "AIRBYTE_MCP_ENV_FILE": "/path/to/my/.mcp/airbyte_mcp.env"
      }
    }
  }
}
```

Note:

- Replace `/path/to/my/.mcp/airbyte_mcp.env` with the absolute path to your dotenv file created in Step 1.

### Step 3: Testing the MCP Server Connection

You can test the MCP server connection using your MCP client.

Helpful prompts to try:

1. "Use your MCP tools to list all available Airbyte connectors."
2. "Use your MCP tools to get information about the Airbyte Stripe connector."
3. "Use your MCP tools to list all variables you have access to in the dotenv secrets file."
4. "Use your MCP tools to check your connection to your Airbyte Cloud workspace."
5. "Use your MCP tools to list all available destinations in my Airbyte Cloud workspace."

## Contributing to the Airbyte MCP Server

- [PyAirbyte Contributing Guide](https://github.com/airbytehq/PyAirbyte/blob/main/docs/CONTRIBUTING.md)

### Additional resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

For issues and questions:

- [PyAirbyte GitHub Issues](https://github.com/airbytehq/pyairbyte/issues)
- [PyAirbyte Discussions](https://github.com/airbytehq/pyairbyte/discussions)
