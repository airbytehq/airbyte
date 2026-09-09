---
plan: all
sidebar_position: 1
---

# Authenticate

The CLI needs three values to call the Airbyte Agent API:

- `client_id`
- `client_secret`
- `organization_id`

The default login flow fetches and saves them for you.

## Browser login

Run:

```bash
airbyte-agent login
```

The CLI opens your browser, signs you in to Airbyte Cloud, and starts a temporary callback server on `127.0.0.1` to complete the login. When login succeeds, it writes `$HOME/.airbyte-agent/settings.json` with `0600` permissions.

If your account belongs to more than one organization, the browser flow may ask you which organization to use. To skip the picker, pass the organization UUID:

```bash
airbyte-agent login --org-id <organization-id>
```

Re-running `airbyte-agent login` refreshes the credential trio and preserves saved values such as `workspace`, `allow_destructive`, `telemetry_enabled`, and `version_check_enabled`.

## Headless machines: manual login

If the machine running the CLI can't open a browser, run:

```bash
airbyte-agent login --manual
```

The CLI prompts for your client ID, client secret, organization ID, and default workspace. Use this flow only when the browser flow isn't available. The browser flow doesn't prompt for a workspace; use `workspaces use` to change the saved default after login.

## Check saved settings

Print the saved settings with the client secret obfuscated:

```bash
airbyte-agent login show
```

This command reads `$HOME/.airbyte-agent/settings.json` directly. If you set `AIRBYTE_*` environment variables, they may override what `login show` prints when the CLI makes API calls.

## Resolution order

For API calls, the CLI resolves credentials in this order:

1. Environment variables, but only when all three of `AIRBYTE_CLIENT_ID`, `AIRBYTE_CLIENT_SECRET`, and `AIRBYTE_ORGANIZATION_ID` are set.
2. `$HOME/.airbyte-agent/settings.json`, when all three fields are populated.
3. An authentication error.

If only one or two of the required environment variables are set, the CLI ignores the partial environment configuration and falls back to the settings file.

## Environment variables

Use these variables for one-off overrides, CI, or headless environments:

- **`AIRBYTE_CLIENT_ID`**: OAuth client ID. Must be set with `AIRBYTE_CLIENT_SECRET` and `AIRBYTE_ORGANIZATION_ID` to override the settings file. Default: required for env auth.
- **`AIRBYTE_CLIENT_SECRET`**: OAuth client secret. Must be set with `AIRBYTE_CLIENT_ID` and `AIRBYTE_ORGANIZATION_ID` to override the settings file. Default: required for env auth.
- **`AIRBYTE_ORGANIZATION_ID`**: Organization UUID. Must be set with `AIRBYTE_CLIENT_ID` and `AIRBYTE_CLIENT_SECRET` to override the settings file. Default: required for env auth.
- **`AIRBYTE_WORKSPACE`**: Default workspace for commands that take a `workspace` parameter. Default: `default`.
- **`AIRBYTE_API_HOST`**: Agent API base URL. Default: `https://api.airbyte.ai`.
- **`AIRBYTE_WEBAPP_URL`**: Web app URL used by connector credential flows. Default: `https://app.airbyte.ai`.
- **`AIRBYTE_CREDENTIAL_TIMEOUT`**: Credential-flow timeout for `connectors create`, in seconds. Default: `180`.
- **`AIRBYTE_ALLOW_DESTRUCTIVE`**: When truthy (`1`, `true`, `yes`, or `on`), skips the confirmation prompt on destructive commands such as `connectors delete`. Default: `false`.
- **`AIRBYTE_TELEMETRY_MODE`**: Set to `disabled` to turn off telemetry. Default: settings file value.
- **`AIRBYTE_VERSION_CHECK`**: Set to `disabled` to suppress the once-per-day release check. Default: settings file value.

## Settings file

The settings file lives at `$HOME/.airbyte-agent/settings.json`:

```json
{
  "settings": {
    "credentials": {
      "client_id": "<client-id>",
      "client_secret": "<client-secret>"
    },
    "organization_id": "<organization-id>",
    "workspace": "default",
    "allow_destructive": false,
    "telemetry_enabled": true,
    "version_check_enabled": true
  }
}
```

The CLI creates the parent directory with `0700` permissions and writes the file with `0600` permissions.

## Switch defaults

Set the default organization:

```bash
airbyte-agent organizations use --json '{"id": "<organization-id>"}'
```

Set the default workspace:

```bash
airbyte-agent workspaces use --json '{"name": "default"}'
```

Both commands verify the target exists before updating `$HOME/.airbyte-agent/settings.json`.
