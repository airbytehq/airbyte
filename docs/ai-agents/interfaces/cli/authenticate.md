---
plan: all
sidebar_position: 1
---

# Authenticate

The CLI authenticates with Airbyte Agents using an `AIRBYTE_CLIENT_ID`, an `AIRBYTE_CLIENT_SECRET`, and an `AIRBYTE_ORGANIZATION_ID`. After you provide those three values once, the CLI obtains a short-lived OAuth token on first use, caches it locally, and refreshes it automatically before it expires. You never manage tokens yourself.

:::note Two sets of credentials
The credentials on this page authenticate *your machine* with Airbyte Agents. They aren't the same as the per-connector credentials (an OAuth `client_id`/`client_secret`/`refresh_token`, an API key, and so on) that you provide when you [add a connector](./add-connector). The two are independent, and rotating one doesn't affect the other. The CLI also never accepts per-connector credentials inline; those always go through the browser flow.
:::

## Get your credentials

1. Sign in to [app.airbyte.ai](https://app.airbyte.ai/).
2. Find the **Your API Credentials** card in the app and copy your `AIRBYTE_CLIENT_ID`, `AIRBYTE_CLIENT_SECRET`, and `AIRBYTE_ORGANIZATION_ID` from there. New accounts see this card on the onboarding screen; if you've already finished onboarding, it's available alongside your other account details.

If the card isn't visible, copy the organization ID from the URL of any organization page (the UUID after `/organizations/`).

## Provide credentials

The CLI accepts credentials three ways. Pick whichever fits your environment best.

The CLI resolves them in this order: environment variables, then the settings file. Environment variables take precedence only when all three (`AIRBYTE_CLIENT_ID`, `AIRBYTE_CLIENT_SECRET`, and `AIRBYTE_ORGANIZATION_ID`) are set. If any one is missing, the CLI ignores the env vars entirely and reads `~/.airbyte-agent/settings.json` instead.

### Recommended: `airbyte-agent configure`

`configure` prompts for the three values, verifies them by listing organizations, and writes them to `~/.airbyte-agent/settings.json` with `0600` permissions:

```bash
airbyte-agent configure
```

It also prompts for a default workspace name. You can press Enter to keep `default`, or set one later with [`workspaces use`](./workspaces#set-a-default-workspace).

This is the right choice on a developer laptop or any machine where the credentials should persist across sessions.

### Environment variables

Useful for CI, containers, and one-off overrides. All three must be set; if any is missing, the CLI falls through to the settings file.

```bash title=".env"
AIRBYTE_CLIENT_ID=<your_client_id>
AIRBYTE_CLIENT_SECRET=<your_client_secret>
AIRBYTE_ORGANIZATION_ID=<your_organization_id>
```

```bash
export $(grep -v '^#' .env | xargs)
airbyte-agent workspaces list
```

Environment-variable resolution is all-or-nothing: the CLI uses env vars only when **all three** of `AIRBYTE_CLIENT_ID`, `AIRBYTE_CLIENT_SECRET`, and `AIRBYTE_ORGANIZATION_ID` are set. If any one is missing, it falls back to `~/.airbyte-agent/settings.json` and the env values are ignored. There's no partial override: setting only `AIRBYTE_ORGANIZATION_ID` alongside a populated settings file will use the file's org ID, not the env var.

To flip orgs for a single invocation, pass all three:

```bash
AIRBYTE_CLIENT_ID=<other_client_id> \
AIRBYTE_CLIENT_SECRET=<other_client_secret> \
AIRBYTE_ORGANIZATION_ID=<other_org_id> \
  airbyte-agent organizations list
```

### Settings file

You can also write `~/.airbyte-agent/settings.json` directly. `configure` writes the same shape:

```json title="~/.airbyte-agent/settings.json"
{
  "settings": {
    "credentials": {
      "client_id": "your-client-id",
      "client_secret": "your-client-secret"
    },
    "organization_id": "your-org-id",
    "workspace": "default",
    "allow_destructive": false,
    "telemetry_enabled": true
  }
}
```

`workspace` is optional. When set, commands that take a `workspace` parameter without receiving one fall back to this value instead of the literal `"default"`. Set it with [`workspaces use`](./workspaces#set-a-default-workspace) so the CLI verifies the workspace exists and writes the canonical name.

`allow_destructive` and `telemetry_enabled` are also optional. See [Troubleshooting](./troubleshooting) for when you'd flip them.

The file must be readable only by you. The CLI writes it at `0600` by default; if you create it by hand, set the permissions explicitly:

```bash
chmod 600 ~/.airbyte-agent/settings.json
```

## Verify

After authenticating, list your organizations to confirm the CLI can reach the API:

```bash
airbyte-agent organizations list
```

A successful response is a JSON object with two keys, `organizations` (an array) and `is_instance_admin` (a boolean):

```json
{
  "organizations": [
    { "organization_id": "...", "organization_name": "...", ... }
  ],
  "is_instance_admin": false
}
```

Authentication failures exit with code `2` and return a structured error on stderr. See [Troubleshooting](./troubleshooting#authentication-fails) for the most common causes.

## Token refresh

The CLI obtains a short-lived OAuth token on first use and refreshes it automatically before it expires. The token is cached on disk so subsequent commands don't have to re-authenticate. There's nothing for you to manage.

## Self-hosted or staging endpoints

By default, the CLI talks to `https://api.airbyte.ai` and opens browser credential flows against `https://app.airbyte.ai`. Override either with an environment variable:

| Variable | Description | Default |
| --- | --- | --- |
| `AIRBYTE_API_HOST` | API base URL. | `https://api.airbyte.ai` |
| `AIRBYTE_WEBAPP_URL` | Web app URL used for [`connectors create`](./add-connector). | `https://app.airbyte.ai` |

Set both when you point the CLI at a staging or self-hosted environment so the credential flow lands on the matching web app.
