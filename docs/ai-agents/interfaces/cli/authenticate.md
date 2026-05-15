---
plan: all
sidebar_position: 1
---

# Authenticate

The CLI authenticates with Airbyte Agents using an `AIRBYTE_CLIENT_ID`, an `AIRBYTE_CLIENT_SECRET`, and an `AIRBYTE_ORGANIZATION_ID`. After you provide those three values once, the CLI obtains a short-lived OAuth token on first use, caches it locally, and refreshes it automatically before it expires. You never manage tokens yourself.

:::note Two sets of credentials
The credentials on this page authenticate *your machine* with Airbyte Agents. They aren't the same as the per-connector credentials (an OAuth `client_id`/`client_secret`/`refresh_token`, an API key, and so on) that you provide when you [add a connector](./add-connector). The two are independent, and rotating one doesn't affect the other. The CLI also never accepts per-connector credentials inline; those always go through the browser flow.
:::

## Provide credentials

The CLI accepts credentials three ways. Pick whichever fits your environment best.

The CLI resolves them in this order: environment variables, then the settings file. Environment variables take precedence only when all three (`AIRBYTE_CLIENT_ID`, `AIRBYTE_CLIENT_SECRET`, and `AIRBYTE_ORGANIZATION_ID`) are set. If any one is missing, the CLI ignores the env vars entirely and reads `~/.airbyte-agent/settings.json` instead.

### Recommended: `airbyte-agent login`

`login` opens your browser to [app.airbyte.ai](https://app.airbyte.ai/) for a Keycloak sign-in, then fetches your `client_id`, `client_secret`, and `organization_id` from the airbyte.ai bootstrap endpoints and writes them to `~/.airbyte-agent/settings.json` with `0600` permissions. You never see or paste the values yourself.

```bash
airbyte-agent login
```

If you belong to more than one organization, the CLI prints a numbered picker on stderr and asks you to choose. To skip it on subsequent runs (or in scripted setups), pass `--org-id`:

```bash
airbyte-agent login --org-id <organization-uuid>
```

Get the organization UUID from the **Your API Credentials** card in the web app, or from the URL of any organization page (the UUID after `/organizations/`).

The browser flow does not prompt for a default workspace. Set one with [`workspaces use`](./workspaces#set-a-default-workspace) once you're signed in, or edit `workspace` in `~/.airbyte-agent/settings.json` directly.

This is the right choice on a developer laptop or any machine where the credentials should persist across sessions and a browser is available.

#### Headless machines: `--manual`

On a server, a remote shell, or any machine where no browser is reachable, pass `--manual` to fall back to the legacy prompt-based flow. The CLI asks for the three values plus an optional default workspace, with `client_secret` masked on a terminal:

```bash
airbyte-agent login --manual
```

Get the three values from the **Your API Credentials** card on [app.airbyte.ai](https://app.airbyte.ai/). New accounts see this card on the onboarding screen; if you've already finished onboarding, it's available alongside your other account details. If the card isn't visible, copy the organization ID from the URL of any organization page (the UUID after `/organizations/`).

### Environment variables

Environment variables are the preferred way to authenticate whenever the CLI runs somewhere there's no browser and no persistent settings file: agent sandboxes, scheduled jobs, container deployments, and serverless platforms like Modal, AWS Lambda, or Cloud Run. They also work for CI and one-off overrides on a developer machine. All three must be set; if any is missing, the CLI falls through to the settings file.

```bash title=".env"
AIRBYTE_CLIENT_ID=<your_client_id>
AIRBYTE_CLIENT_SECRET=<your_client_secret>
AIRBYTE_ORGANIZATION_ID=<your_organization_id>
```

```bash
export $(grep -v '^#' .env | xargs)
airbyte-agent workspaces list
```

In a sandbox or any other long-lived deployment, supply the three values through whatever secret mechanism your platform offers (a `modal.Secret`, GitHub Actions secrets, Kubernetes secrets, AWS Secrets Manager, and so on). Once the values land in the process environment, the CLI picks them up automatically.

#### Example: scheduled job on Modal

On [Modal](https://modal.com/), bake the binary into the image and attach a `modal.Secret` to the function so the three values are present at runtime. The same pattern (image + secret) applies to most container and serverless platforms.

```python
import os
import subprocess

import modal

image = (
    modal.Image.debian_slim()
    .apt_install("curl", "ca-certificates")
    .run_commands(
        # Install the latest linux_amd64 build of airbyte-agent.
        "curl -sL https://api.github.com/repos/airbytehq/airbyte-agent-cli/releases/latest "
        "| grep 'browser_download_url.*linux_amd64.tar.gz' | cut -d '\"' -f 4 "
        "| xargs curl -sL | tar -xz -C /usr/local/bin airbyte-agent",
    )
)

app = modal.App("airbyte-agent-sync")

@app.function(
    image=image,
    schedule=modal.Period(hours=1),
    # Secret holds AIRBYTE_CLIENT_ID, AIRBYTE_CLIENT_SECRET, AIRBYTE_ORGANIZATION_ID.
    secrets=[modal.Secret.from_name("airbyte-agent")],
)
def list_workspaces() -> None:
    subprocess.run(
        ["airbyte-agent", "workspaces", "list"],
        check=True,
        env={"AIRBYTE_VERSION_CHECK": "disabled", **os.environ},
    )
```

`AIRBYTE_VERSION_CHECK=disabled` opts the run out of the daily GitHub check for a newer release. The binary version is pinned by the image, so the network call adds latency and noise without any actionable nudge for the operator. See the [settings file table](#settings-file) for the rest of the per-deployment knobs (`AIRBYTE_ALLOW_DESTRUCTIVE`, `AIRBYTE_TELEMETRY_MODE`).

Environment-variable resolution is all-or-nothing: the CLI uses env vars only when **all three** of `AIRBYTE_CLIENT_ID`, `AIRBYTE_CLIENT_SECRET`, and `AIRBYTE_ORGANIZATION_ID` are set. If any one is missing, it falls back to `~/.airbyte-agent/settings.json` and the env values are ignored. There's no partial override: setting only `AIRBYTE_ORGANIZATION_ID` alongside a populated settings file will use the file's org ID, not the env var.

To flip orgs for a single invocation, pass all three:

```bash
AIRBYTE_CLIENT_ID=<other_client_id> \
AIRBYTE_CLIENT_SECRET=<other_client_secret> \
AIRBYTE_ORGANIZATION_ID=<other_org_id> \
  airbyte-agent organizations list
```

### Settings file

You can also write `~/.airbyte-agent/settings.json` directly. `login` writes the same shape (the browser flow populates `credentials` and `organization_id`; `--manual` also writes `workspace`):

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
    "telemetry_enabled": true,
    "is_internal_user": false,
    "version_check_enabled": true
  }
}
```

Only the `credentials` block and `organization_id` are required. The rest are optional and have safe defaults:

| Field | Default | What it does | Env override |
| --- | --- | --- | --- |
| `workspace` | `"default"` | Default workspace for commands that take a `workspace` parameter without receiving one. Set it with [`workspaces use`](./workspaces#set-a-default-workspace) so the CLI verifies the workspace exists and writes the canonical name. | `AIRBYTE_WORKSPACE` |
| `allow_destructive` | `false` | When `true`, destructive commands like [`connectors delete`](./command-reference#connectors-delete) skip the interactive confirmation prompt. Useful for agent harnesses that can't answer a TTY prompt. | `AIRBYTE_ALLOW_DESTRUCTIVE=true` |
| `telemetry_enabled` | `true` | Anonymous usage telemetry. Set to `false` to opt out. | `AIRBYTE_TELEMETRY_MODE=disabled` |
| `is_internal_user` | `false` | Marks the invocation as an Airbyte employee so internal events can be filtered out of customer analytics. Leave at `false` outside of Airbyte. | `AIRBYTE_INTERNAL_USER` |
| `version_check_enabled` | `true` | Once per day, the CLI checks GitHub for a newer release and prints a nudge. Set to `false` to disable the network call. **Recommended for sandboxed agents, long-running automations, and any deployment where the binary version is pinned by the image.** | `AIRBYTE_VERSION_CHECK=disabled` |

See [Troubleshooting](./troubleshooting) for when you'd flip `allow_destructive` or `telemetry_enabled`.

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
    { "id": "...", "organization_name": "...", "first_workspace_id": "..." }
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
