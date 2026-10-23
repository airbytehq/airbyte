---
plan: team, custom
sidebar_position: 5
---

# Single sign-on (SSO)

Single sign-on lets your organization's members sign in to Airbyte Agents through your identity provider instead of using individual passwords. SSO is available on the [Team and Custom plans](./billing.md#team).

## Prerequisites

Before you begin, make sure you have the following:

- An Airbyte Agents organization on the Team or Custom plan.
- Administrator access to your identity provider (for example, Okta, Microsoft Entra ID, Google Workspace, or any provider that supports OIDC).
- Access to your domain's DNS settings so you can add a TXT record for domain verification.

## Set up SSO

Setting up SSO is a three-part process: create a configuration, verify your domain, and activate.

### Step 1: Create an SSO configuration

1. In the Airbyte Agents web app, open **SSO** from the sidebar.
2. Fill in the configuration form:
   - **Company identifier**: A short, URL-safe slug for your organization (for example, `my-company`). Your members use this identifier when they sign in with SSO.
   - **Client ID**: The client ID from your identity provider's application registration.
   - **Client secret**: The client secret from your identity provider's application registration.
   - **Discovery URL**: The OpenID Connect discovery endpoint for your identity provider. This is typically a URL ending in `/.well-known/openid-configuration` (for example, `https://example.okta.com/.well-known/openid-configuration`).
3. Click **Configure SSO**.

After submitting, Airbyte creates the configuration in **Draft** status. SSO is not active yet — you need to verify at least one domain first.

:::tip Finding your discovery URL
Most identity providers publish their discovery URL in their admin console under OIDC or SSO settings. Common patterns:

- **Okta**: `https://<your-domain>.okta.com/.well-known/openid-configuration`
- **Microsoft Entra ID**: `https://login.microsoftonline.com/<tenant-id>/v2.0/.well-known/openid-configuration`
- **Google Workspace**: `https://accounts.google.com/.well-known/openid-configuration`
:::

### Step 2: Verify your domain

Domain verification proves that you own the email domain whose users will sign in with SSO. You need at least one verified domain before you can activate SSO.

1. On the SSO page, in the **Verified domains** section, click **Add domain**.
2. Enter the domain (for example, `example.com`) and click **Add domain**.
3. Airbyte generates a DNS TXT record for verification. Copy the **Record name** and **Record value** shown on the page.
4. Go to your DNS provider and add a new TXT record using the record name and value from the previous step.
5. Return to the SSO page and click **Check now** to verify the record.

Domain verification status:

| Status | Meaning |
|---|---|
| **Pending verification** | The DNS record hasn't been detected yet. DNS changes can take up to 48 hours to propagate. |
| **Verified** | The DNS record was found and the domain is verified. |
| **Failed** | Verification failed. Check that the TXT record is correct and click **Reset and retry**. |
| **Expired** | The verification window expired. Click **Reset and retry** to generate a new record. |

You can add multiple domains. Each domain requires its own TXT record.

### Step 3: Activate SSO

Once you have at least one verified domain:

1. On the SSO page, click **Activate SSO**.

The configuration status changes from **Draft** to **Active**. Members whose email addresses match a verified domain can now sign in with SSO.

## Sign in with SSO

Once SSO is active, members sign in at [app.airbyte.ai](https://app.airbyte.ai):

1. On the sign-in page, click **Continue with SSO**.
2. Enter the **company identifier** that your administrator set during SSO configuration.
3. Click **Continue with SSO**. Airbyte redirects you to your identity provider.
4. Authenticate with your identity provider. After successful authentication, you are redirected back to Airbyte Agents.

Share the company identifier with your team so they know what to enter during sign-in.

## Manage your SSO configuration

After SSO is active, the SSO page shows your current configuration and provides these actions:

- **Update credentials**: Change the client ID and client secret without deleting and recreating the configuration.
- **Validate token**: Paste an access token from your identity provider to test whether Airbyte can validate it. Use this to troubleshoot authentication issues.
- **Delete configuration**: Permanently remove the SSO configuration. Members will no longer be able to sign in with SSO. This action cannot be undone.

## Troubleshooting

### "Domain verification required" banner

This banner appears when your SSO configuration is in Draft status and no domains are verified yet. Add and verify at least one domain before activating SSO.

### Domain verification is stuck on "Pending"

DNS propagation can take up to 48 hours. Verify that the TXT record name and value in your DNS provider match exactly what Airbyte shows on the SSO page. Click **Check now** to retry.

### "Failed to activate SSO"

Activation requires at least one verified domain. If your domain shows **Failed** or **Expired**, click **Reset and retry** to generate a new DNS record and re-verify.

### Members can't sign in

- Confirm SSO status is **Active** on the SSO page.
- Confirm the member's email domain matches one of the verified domains.
- Confirm the member is using the correct company identifier.
- Use **Validate token** to test whether tokens from your identity provider are accepted.
