# Airbyte knowledge MCP server

The Airbyte knowledge MCP server connects AI agents to comprehensive sources of information about Airbyte. It provides semantic search over Airbyte's documentation, website, OpenAPI specs, YouTube content, and GitHub issues, discussions, and pull requests.

When you're working with an AI agent on tasks that involve Airbyte, the MCP server gives your agent up-to-date context about Airbyte's features, APIs, and best practices without leaving your development environment.

## When to use it

The Airbyte knowledge MCP is helpful when your AI agent is:

- Building a custom connector
- Working with PyAirbyte, Airbyte's Terraform provider, or REST API to configure sources, destinations, and connections
- Troubleshooting sync errors or connection issues
- Learning about Airbyte's architecture or deployment options

Any time an agent performs a task that requires interacting with Airbyte, the MCP server can provide relevant context.

## Connecting to the MCP server

The server URL is `https://airbyte.mcp.kapa.ai`.

### Cursor and VS Code

If you're using Cursor or VS Code, you can connect with one click through the Ask AI button in the [Airbyte documentation](https://docs.airbyte.com). Click the button, then select the MCP install option from the dropdown menu.

### Claude

For Claude Desktop or Claude Code, run the following command:

```bash
claude mcp add --transport http airbyte-docs https://airbyte.mcp.kapa.ai
```

### Other AI tools

The Airbyte knowledge MCP works with any MCP-compatible tool, including Windsurf and ChatGPT Desktop. Refer to your tool's documentation for instructions on adding MCP servers, and use the server URL `https://airbyte.mcp.kapa.ai`.

## Authentication

When connecting for the first time, you'll be prompted to sign in with any Google account. This authentication is used only to enforce rate limits and prevent abuse of the server. Airbyte does not access your email, name, or other personal data.

## Rate limits

Each authenticated user is limited to 40 requests per hour and 200 requests per day.

## Additional resources

- [Model Context Protocol documentation](https://modelcontextprotocol.io/)
