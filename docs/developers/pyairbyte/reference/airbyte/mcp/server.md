---
id: airbyte-mcp-server
title: "airbyte.mcp.server Module"
sidebar_label: "airbyte.mcp.server"
toc_max_heading_level: 5
---

# `airbyte.mcp.server` Module

MCP (Model Context Protocol) server for PyAirbyte connector management.

Supports two transport modes:

- **stdio** (default): For local MCP clients (Claude Desktop, etc.). Auth is not
  enforced; the provider assembled below is ignored by the stdio transport.
- **HTTP**: For hosted deployment. Start via `airbyte-mcp-http` entry point or
  `poe mcp-serve-http`. This server maps its own branded `AIRBYTE_MCP_*` env vars
  into the typed configs that `fastmcp_extensions.build_mcp_auth` consumes, which
  supports two client shapes on the same deployment:
    - **Interactive** (humans in a browser): Keycloak Authorization Code + PKCE
      via `OIDCProxy`, active once `AIRBYTE_MCP_OIDC_CLIENT_ID`,
      `AIRBYTE_MCP_OIDC_CLIENT_SECRET`, and `AIRBYTE_MCP_OIDC_CONFIG_URL` (the
      OIDC discovery URL) are supplied.
    - **Headless** (agents, CI): the client mints its own short-lived bearer
      token via the OAuth 2.0 client credentials grant and sends it as
      `Authorization: Bearer <token>`. The server verifies it with a
      `JWTVerifier`, active once a signing-key source (`AIRBYTE_MCP_AUTH_JWKS_URI`
      or `AIRBYTE_MCP_AUTH_JWT_PUBLIC_KEY`) is configured (no browser, no
      stored/rotating refresh token).
  When both are active they are combined via `MultiAuth`; when neither is
  configured `_create_auth` returns `None` and HTTP transport runs
  unauthenticated (a startup warning is logged in `http_main`).

This module declares only the env var *names* and maps their values into the
typed `OIDCAuthConfig` / `JWTAuthConfig` objects that `build_mcp_auth` consumes,
so the extensions library stays provider-neutral and reads no env itself. It
embeds no provider-specific configuration *values* (a realm's discovery URL,
issuer, JWKS URI, audience, algorithm, etc.); those are supplied at deploy time
by the deployment's own repo — e.g. the hosted Cloud MCP image in
`airbyte-ops-mcp` sets the `AIRBYTE_MCP_*` env for the Airbyte Cloud realm.

For the headless path, an agent mints an access token from its client id/secret
(via the deployment's `<api_root>/applications/token` endpoint) and sends it as
`Authorization: Bearer`. When the deployment's realm is Airbyte Cloud, that
single token both authenticates transport (verified here) and authorizes
downstream Cloud API calls, because an Airbyte-Cloud-issued JWT is itself a valid
Cloud API bearer.

- **`app`**

  The Airbyte MCP Server application instance.

### `health_check` {#airbyte.mcp.server.health_check}

<ApiMember kind="function">

<ApiSignature>

```python
def health_check(request: Request) -> JSONResponse
```

</ApiSignature>

Health check endpoint for load balancer probes.

</ApiMember>

### `main` {#airbyte.mcp.server.main}

<ApiMember kind="function">

<ApiSignature>

```python
def main() -> None
```

</ApiSignature>

@private Main entry point for the MCP server.

This function starts the FastMCP server to handle MCP requests.

It should not be called directly; instead, consult the MCP client documentation
for instructions on how to connect to the server.

</ApiMember>