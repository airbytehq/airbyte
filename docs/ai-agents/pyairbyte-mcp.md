---
products: embedded
---

# PyAirbyte MCP Server

> **NOTE:**
> This MCP server implementation is experimental and may change without notice between minor versions of PyAirbyte. The API may be modified or entirely refactored in future versions.

The PyAirbyte MCP (Model Context Protocol) server provides a standardized interface for managing Airbyte connectors through MCP-compatible clients. This experimental feature allows you to list connectors, validate configurations, and run sync operations using the MCP protocol.

## Documentation

For complete setup instructions, troubleshooting guidance, and detailed documentation, please refer to the authoritative PyAirbyte MCP documentation:

**[PyAirbyte MCP Server Documentation](https://airbytehq.github.io/PyAirbyte/airbyte/mcp.html)**

The PyAirbyte documentation includes:
- Step-by-step setup instructions
- Environment configuration requirements
- Security model and safety features
- Troubleshooting guide with common issues and solutions
- Architecture overview
- Prerequisites checklist

## Quick Start

To get started with the PyAirbyte MCP server:

1. Install `uv`: `brew install uv`
2. Create a dotenv secrets file with your Airbyte Cloud credentials and connector configurations
3. Register the MCP server with your MCP client using `uvx --python=3.11 --from=airbyte@latest airbyte-mcp`
4. Test the connection using your MCP client

For detailed instructions on each step, see the [PyAirbyte MCP documentation](https://airbytehq.github.io/PyAirbyte/airbyte/mcp.html).

## Contributing to the Airbyte MCP Server

- [PyAirbyte Contributing Guide](https://github.com/airbytehq/PyAirbyte/blob/main/docs/CONTRIBUTING.md)

### Additional resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

For issues and questions:

- [PyAirbyte GitHub Issues](https://github.com/airbytehq/pyairbyte/issues)
- [PyAirbyte Discussions](https://github.com/airbytehq/pyairbyte/discussions)
