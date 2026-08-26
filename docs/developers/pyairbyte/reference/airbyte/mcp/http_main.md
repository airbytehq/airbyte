---
id: airbyte-mcp-http_main
title: "airbyte.mcp.http_main Module"
sidebar_label: "airbyte.mcp.http_main"
---

# `airbyte.mcp.http_main` Module

HTTP transport entry point for the Airbyte MCP server.

Starts the MCP server with HTTP transport, suitable for hosted deployment
behind a load balancer. Transport auth is assembled in `server.py`, which maps
this server's branded `AIRBYTE_MCP_*` env vars into the typed configs consumed
by `fastmcp_extensions.build_mcp_auth` (interactive OIDC and/or headless
bearer-token verification, combined via `MultiAuth`). Auth activates only for
the paths a deployment configures via env; with no auth env set the server
falls back to unauthenticated local behavior. This module declares only the env
var *names* — the concrete values are supplied at deploy time by the
deployment's own repo. See `server.py` and `_client_credentials.py` for
details.

Stateless streamable HTTP does not retain initialize-time client capabilities
internally. For clients that declare extensions at initialize, the server
returns a self-describing `Mcp-Session-Id`, and spec-compliant clients echo it
on subsequent requests. This makes MCP Apps `interactive-ui` tools available
without a client-specific header. Clients that do not echo session IDs can use
the explicit fallback `X-MCP-Extensions: io.modelcontextprotocol/ui` header on
each HTTP request. Multiple extension IDs may be comma-separated (recommended)
or whitespace-separated. The capability-token and SSE GET middleware are
provided by the installed `fastmcp-extensions` package.

The eventual spec-aligned replacement is per-request `_meta` under
`io.modelcontextprotocol/clientCapabilities`. That path exists in the modern
`mcp` 2.x server architecture, while this project currently resolves the
legacy `fastmcp` 3.x and `mcp` 1.x stack. Using it requires a stack migration
rather than a version-only change.

Environment variables:

- `MCP_SERVER_URL`: Public base URL. Used for OIDC redirect callbacks and to
  derive the MCP endpoint mount path (serves at `/` when the URL has a path
  prefix, otherwise defaults to `/mcp`).

Interactive OIDC (Keycloak Authorization Code + PKCE), enabled when the client
credentials are set:

- `AIRBYTE_MCP_OIDC_CLIENT_ID`: OIDC client identifier
- `AIRBYTE_MCP_OIDC_CLIENT_SECRET`: OIDC client secret
- `AIRBYTE_MCP_OIDC_CONFIG_URL`: OIDC discovery URL (required when the client
  credentials are set)
- `AIRBYTE_MCP_OIDC_CLIENT_STORAGE_FACTORY`: optional `"package.module:callable"`
  naming a durable OAuth-state store factory (defaults to in-memory)

Headless bearer-token verification (for agents/CI that mint their own
short-lived token via the client credentials grant). The verifier activates
once a signing-key source — the JWKS URI or a static public key — is set;
issuer, audience, and algorithm refine verification when provided:

- `AIRBYTE_MCP_AUTH_JWKS_URI`: JWKS endpoint used to verify token signatures
- `AIRBYTE_MCP_AUTH_JWT_PUBLIC_KEY`: static public key (alternative to the JWKS
  URI)
- `AIRBYTE_MCP_AUTH_ISSUER`: expected token issuer
- `AIRBYTE_MCP_AUTH_AUDIENCE`: expected token audience
- `AIRBYTE_MCP_AUTH_ALGORITHM`: signing algorithm override

Opt-in static client credentials:

- `AIRBYTE_MCP_AUTH_ALLOW_CLIENT_CREDENTIALS`: enable `Client-Id` /
  `Client-Secret` headers and HTTP Basic credentials. This is an exchange-and-
  rewrite layer, not a bearer-token verifier; configure `AIRBYTE_MCP_AUTH_JWKS_URI`
  or `AIRBYTE_MCP_AUTH_JWT_PUBLIC_KEY` as well. Without a verifier, minted token
  claims and requests with no credentials are not checked.
- `AIRBYTE_MCP_AUTH_CLIENT_CREDENTIALS_TOKEN_URL`: OAuth token endpoint for the
  exchange; defaults to the Airbyte Cloud application-token endpoint

### `main` {#airbyte.mcp.http_main.main}

<ApiMember kind="function">

<ApiSignature>

```python
def main() -> None
```

</ApiSignature>

Start the Airbyte MCP server with HTTP transport.

</ApiMember>