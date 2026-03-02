---
sidebar_label: "Troubleshooting"
sidebar_position: 5
---

# Troubleshoot the MCP server

This page covers common issues you may encounter when using the Agent Engine MCP server.

## MCP server not found

Your agent can't discover the MCP server's tools.

- Ensure you restarted your agent after registering the server.
- Verify the registration succeeded by checking your agent's MCP server list or configuration file.

## Environment variable errors

The MCP server fails to start or returns credential errors.

- Verify your `.env` file is in the same directory where you run `adp` commands.
- Confirm the variable names in your `.env` file match the `${env.VAR_NAME}` placeholders in your YAML configuration.
- Check that there are no extra spaces or characters in your `.env` values.

## HTTP 401 errors

Authentication failed.

- **Open source mode**: Your API credential is invalid or expired. Generate a new credential from the third-party service and update your `.env` file.
- **Hosted mode**: Your Agent Engine credentials are invalid. Run `uv run adp login <organization-id>` to re-enter your Client ID and Secret.

## HTTP 403 errors

Authentication succeeded but the request is forbidden.

- Your API credential doesn't have the required permissions. Check the third-party service's documentation for the scopes or roles your credential needs.

## Long text fields are truncated

For `list` and `search` results, the MCP server truncates text fields longer than 200 characters to reduce token usage. Truncated fields are marked with `[truncated]`. To get the full value:

1. Use the `get` action with the record ID.
2. If `get` is not available, retry the original query with `skip_truncation=true` and tight `select_fields` and `limit`.

## Search returns no results

If `search` returns no results but you expect data:

- The `search` action only works in [hosted mode](configuration#hosted-mode) with the [context store](../platform/context-store) enabled. In open source mode, use `list` with date boundary parameters instead.
- The search index may lag behind by hours. Try `list` with date boundary parameters instead.
- Try `fuzzy` matching instead of `like` in your filter (e.g., `{"fuzzy": {"name": "search term"}}`).

## Date range queries miss recent data

When querying date ranges that include today, the search index may not have the latest records. Issue both a `search` call and a `list` call with date boundary parameters, then merge results and deduplicate by ID.
