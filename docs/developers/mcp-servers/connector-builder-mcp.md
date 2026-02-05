# Connector Builder MCP Server

The Connector Builder MCP (Model Context Protocol) server enables AI agents to autonomously build Airbyte source connectors. Rather than assisting a human developer, this MCP server gives AI agents full ownership of the connector development lifecycle, from manifest creation and validation to stream testing and PR creation.

## Documentation

For the complete API reference, refer to the auto-generated Connector Builder MCP documentation:

**[Connector Builder MCP API Reference](https://airbytehq.github.io/connector-builder-mcp/)**

## When to use

Use the Connector Builder MCP when you want an AI agent to build a new Airbyte source connector for an API that isn't already in the [connector catalog](/integrations/sources). The MCP server provides tools that let AI agents:

- Create and edit declarative YAML connector manifests
- Validate manifests against the Airbyte CDK schema
- Test stream reads against live APIs
- Run connector readiness reports
- Manage secrets for API authentication
- Access connector-building documentation and guidance

## Quick start

### Prerequisites

- [uv](https://docs.astral.sh/uv/) for package management (`brew install uv`)
- Python 3.10+

### Install and run

The Connector Builder MCP server is available on PyPI and can be run directly with `uvx`:

```bash
uvx airbyte-connector-builder-mcp
```

### Configure your MCP client

Add the following configuration to your MCP client. The example below works with Claude Desktop, Claude Code, and other MCP-compatible clients.

```json
{
  "mcpServers": {
    "airbyte-connector-builder-mcp": {
      "command": "uvx",
      "args": [
        "airbyte-connector-builder-mcp"
      ]
    }
  }
}
```

For a more complete setup that includes the [PyAirbyte MCP](pyairbyte-mcp.md) server for publishing connectors to Airbyte Cloud, see the [suggested configuration](https://github.com/airbytehq/connector-builder-mcp#suggested-mcp-server-config) in the GitHub repository.

## Sample prompts

Here are some prompts to get started:

1. "Create an Airbyte source connector for the Sentry API from scratch using your connector-builder-mcp tools."
2. "Validate the current connector manifest and fix any issues."
3. "Test the `events` stream and show me the results."
4. "Run a full readiness test report for all streams."
5. "List the secrets available in my `.env` file."

When prompting the agent, provide the path to a `.env` file containing the API credentials for the source you're building. For example:

> I have a `.env` file at `/path/to/secrets/.env` with my API credentials. Use the connector-builder-mcp tools to build a source connector for the Sentry API.

## Complementary MCP servers

The Connector Builder MCP works well alongside other MCP servers:

- **[PyAirbyte MCP](pyairbyte-mcp.md)**: Publish built connectors to your Airbyte Cloud workspace, run local syncs, and validate data.
- **Playwright MCP**: Give the agent web browsing capabilities for researching API documentation.

## Contributing

- [Connector Builder MCP Contributing Guide](https://github.com/airbytehq/connector-builder-mcp/blob/main/CONTRIBUTING.md)

### Additional resources

- [Connector Builder MCP on GitHub](https://github.com/airbytehq/connector-builder-mcp)
- [Connector Builder MCP on PyPI](https://pypi.org/project/airbyte-connector-builder-mcp/)
- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)

For issues and questions:

- [GitHub Issues](https://github.com/airbytehq/connector-builder-mcp/issues)
- [Airbyte Community Slack](https://airbyte.com/community)
