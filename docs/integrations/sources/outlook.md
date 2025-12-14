# Outlook

Outlook is the email service provided by Microsoft. This connector enables you to sync emails, mailboxes, and conversations from Microsoft Outlook/Exchange Online using Microsoft Graph API with delegated permissions for multi-tenant support.

## Prerequisites

To use this connector, you need:

- A Microsoft Entra ID (formerly Azure AD) tenant
- An account with at least the Cloud Application Administrator role
- An Azure App Registration with the required API permissions

## Setup Guide

### Step 1: Register an Application in Azure

1. Sign in to the [Microsoft Entra admin center](https://entra.microsoft.com)
2. Navigate to **Identity** > **Applications** > **App registrations**
3. Select **New registration**
4. Enter a display name for your application (for example, "Airbyte Outlook Connector")
5. Under **Supported account types**, select the appropriate option:
   - **Accounts in this organizational directory only**: Single-tenant (your organization only)
   - **Accounts in any organizational directory**: Multi-tenant (any Microsoft Entra organization)
   - **Accounts in any organizational directory and personal Microsoft accounts**: Multi-tenant with personal accounts
6. Leave **Redirect URI** blank for now (you'll configure this in Step 3)
7. Click **Register**

After registration, note the **Application (client) ID** displayed on the Overview page.

### Step 2: Configure API Permissions

The connector requires the following Microsoft Graph API permissions:

1. In your app registration, navigate to **API permissions**
2. Click **Add a permission** > **Microsoft Graph** > **Delegated permissions**
3. Add the following permissions:
   - `Mail.Read`: Allows the app to read the signed-in user's mailbox. This permission is required to access email messages and their attachments.
   - `User.Read`: Allows users to sign in to the app and allows the app to read the profile of signed-in users.
4. Click **Add permissions**

**Note**: Admin consent is not required for `Mail.Read` delegated permission when used with the signed-in user's own mailbox. However, your organization's policies may require admin consent for all permissions.

For more information about these permissions, see the [Microsoft Graph permissions reference](https://learn.microsoft.com/en-us/graph/permissions-reference).

### Step 3: Configure Redirect URI

1. In your app registration, navigate to **Authentication**
2. Under **Platform configurations**, click **Add a platform**
3. Select **Web**
4. Enter the redirect URI provided by Airbyte during the OAuth configuration process
5. Click **Configure**

The redirect URI is where Microsoft will send the authentication response after the user signs in. Airbyte provides this URI when you configure the connector.

### Step 4: Create a Client Secret

1. In your app registration, navigate to **Certificates & secrets**
2. Under **Client secrets**, click **New client secret**
3. Add a description (for example, "Airbyte Outlook Connector Secret")
4. Select an expiration period (Microsoft recommends less than 12 months)
5. Click **Add**
6. **Important**: Copy the secret value immediately. This value is never displayed again after you leave this page.

### Step 5: Obtain OAuth Credentials

To obtain the refresh token needed for Airbyte configuration:

1. Use the OAuth 2.0 authorization flow with your Client ID and Client Secret
2. Request the following scopes: `https://graph.microsoft.com/Mail.Read https://graph.microsoft.com/User.Read offline_access`
3. After user consent, exchange the authorization code for an access token and refresh token
4. Save the refresh token for use in Airbyte configuration

For detailed instructions on the OAuth flow, see [Get access on behalf of a user](https://learn.microsoft.com/en-us/graph/auth-v2-user).

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | OAuth Client ID. The Client ID of your Microsoft Azure application |  |
| `tenant_id` | `string` | Tenant ID (Optional). Azure AD Tenant ID (optional for multi-tenant apps, defaults to &#39;common&#39;) | common |
| `client_secret` | `string` | OAuth Client Secret. The Client Secret of your Microsoft Azure application |  |
| `refresh_token` | `string` | Refresh Token. Refresh token obtained from Microsoft OAuth flow |  |

## Streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| profile |  | No pagination | ✅ |  ❌  |
| mailboxes | id | DefaultPaginator | ✅ |  ❌  |
| messages | id | DefaultPaginator | ✅ |  ❌  |
| messages_details | id | No pagination | ✅ |  ❌  |
| conversations | conversationId | DefaultPaginator | ✅ |  ❌  |

### Stream Details

`messages`: Retrieves all messages from the signed-in user's mailbox using the `/me/messages` endpoint. This stream fetches messages from all folders including Inbox, Sent Items, Deleted Items, and other mail folders.

`mailboxes`: Retrieves information about mail folders in the user's mailbox.

`profile`: Retrieves the signed-in user's profile information.

`conversations`: Retrieves conversation threads from the user's mailbox.

`messages_details`: Retrieves detailed information for individual messages.

## Filtering and Limitations

This connector does not currently support filtering emails by specific criteria such as:

- Specific mailbox or folder path
- Email subject
- Sender or recipient
- Date ranges

The connector retrieves all messages from the signed-in user's mailbox via the `/me/messages` endpoint. The Microsoft Graph API does support filtering via OData query parameters (such as `$filter`), but these are not currently exposed as configuration options in this connector.

To filter messages after extraction, you can:

- Use [Airbyte Mappings](/platform/using-airbyte/mappings) to filter rows based on field values
- Apply filters in your data warehouse or transformation tool after sync
- Use the Microsoft Graph API directly with custom filtering parameters

For more information about Microsoft Graph Mail API capabilities, see the [Microsoft Graph Mail API documentation](https://learn.microsoft.com/en-us/graph/api/user-list-messages).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.12 | 2025-12-09 | [70526](https://github.com/airbytehq/airbyte/pull/70526) | Update dependencies |
| 0.0.11 | 2025-11-25 | [70123](https://github.com/airbytehq/airbyte/pull/70123) | Update dependencies |
| 0.0.10 | 2025-11-18 | [69707](https://github.com/airbytehq/airbyte/pull/69707) | Update dependencies |
| 0.0.9 | 2025-10-29 | [69010](https://github.com/airbytehq/airbyte/pull/69010) | Update dependencies |
| 0.0.8 | 2025-10-21 | [68311](https://github.com/airbytehq/airbyte/pull/68311) | Update dependencies |
| 0.0.7 | 2025-10-14 | [67772](https://github.com/airbytehq/airbyte/pull/67772) | Update dependencies |
| 0.0.6 | 2025-10-07 | [67343](https://github.com/airbytehq/airbyte/pull/67343) | Update dependencies |
| 0.0.5 | 2025-09-30 | [66389](https://github.com/airbytehq/airbyte/pull/66389) | Update dependencies |
| 0.0.4 | 2025-09-09 | [65826](https://github.com/airbytehq/airbyte/pull/65826) | Update dependencies |
| 0.0.3 | 2025-08-23 | [65161](https://github.com/airbytehq/airbyte/pull/65161) | Update dependencies |
| 0.0.2 | 2025-08-14 | [64942](https://github.com/airbytehq/airbyte/pull/64942) | Fix docker image entrypoint for platform syncs |
| 0.0.1 | 2025-08-14 | | Initial release by [@saif-qureshi-341](https://github.com/saif-qureshi-341) via Connector Builder |

</details>
