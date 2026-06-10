---
plan: all
---

# Manage your user profile

Your Profile page contains your personal account details, your organization's name, and the API credentials Airbyte Agents uses to authenticate programmatic access. Go to the Profile page to review these details or make changes.

## Personal information

The Personal Information card shows the email address associated with your Airbyte Agents account. Airbyte sets this email when you sign up and uses it to identify you, send account notifications, and route support requests.

You can't change your email from the Profile page. It's a read-only field tied to the account you signed in with.

## Organization information

The Organization card shows the name of the organization you're currently managing. Airbyte displays this name across the app and on invoices.

### Rename your organization

1. On the Profile page, in the Organization card, update the value in **Organization Name**.
2. Click **Save Changes**.

The name must be between 1 and 256 characters. **Save Changes** stays disabled until you've made a valid change.

## API credentials

The API Credentials card contains the values you need to authenticate programmatic access to your organization. Use these credentials with the [SDK](../interfaces/sdk/readme.md) or the [MCP server](../interfaces/mcp/readme.md) to run agents outside of the chat UI.

Airbyte displays three values:

- **AIRBYTE_ORGANIZATION_ID**: The unique identifier for your organization.
- **AIRBYTE_CLIENT_ID**: The client ID for API authentication.
- **AIRBYTE_CLIENT_SECRET**: The client secret for API authentication.

Airbyte creates these credentials automatically for each organization. The client ID and client secret are sensitive values.

### View and copy credentials

To copy a single value, click the copy icon next to that value. To reveal a hidden value before copying, click the eye icon to toggle visibility on the client ID or client secret.

:::warning
Treat the client secret like a password. Anyone with your client ID and client secret can access your organization through the API or SDK. Don't commit these values to source control, share them in public channels, or paste them into untrusted tools.
:::
