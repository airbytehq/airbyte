# Overview

The Embedded Operator MCP is a remote MCP server providing tools that enable managing embedded configurations and the resulting pipelines. Users can create connection and source templates, securely create sources, query API and File Storage sources, monitor connections and jobs, and more.

# Installation

To install, follow the instructions for adding remote MCP servers to your client.

For Claude Desktop, visit Settings > Connectors > Add Custom Connector. Name the server "Airbyte Embedded Operator MCP" and enter the following URL:
```
https://mcp.airbyte.ai/sonar
```

For Claude Code, run the following in your terminal (not in the Claude Code CLI):
```bash
claude mcp add -t http sonar https://mcp.airbyte.ai/sonar
```

# Authentication

The Embedded Operator MCP adheres to the MCP OAuth 2.0 specification. This specification is evolving and may not be stable. In particular, Claude Desktop may require a few attempts to successfully connect.

To connect with Claude Desktop, press the `Connect` button that appears when you first add the server. A browser window will open and prompt you to enter your Airbyte Client ID and Secret. (Be sure that the window opens in a browser where you are logged into Claude Web using the same account as Claude Desktop.)

To connect with Claude Code, run the following in the Claude Code CLI
```
/mcp reconnect sonar
```

TODO: CALLOUT: Your credentials must reference an organization that has been enabled for Airbyte Embedded. Contact michel@airbyte.io or teo@airbyte.io to enable Airbyte Embedded on your account.