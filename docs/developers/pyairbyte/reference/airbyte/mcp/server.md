---
id: airbyte-mcp-server
title: airbyte.mcp.server
---

Module airbyte.mcp.server
=========================
Experimental MCP (Model Context Protocol) server for PyAirbyte connector management.

Variables
---------

`app: fastmcp.server.server.FastMCP`
:   The Airbyte MCP Server application instance.

Functions
---------

`main() ‑> None`
:   @private Main entry point for the MCP server.
    
    This function starts the FastMCP server to handle MCP requests.
    
    It should not be called directly; instead, consult the MCP client documentation
    for instructions on how to connect to the server.