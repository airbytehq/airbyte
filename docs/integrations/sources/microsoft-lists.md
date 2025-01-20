# Microsoft Lists
Microsoft Lists connector enables seamless data integration and synchronization between Microsoft Lists and other destination. The connector leverages Microsoft Graph API to retrieve list items efficiently, ensuring smooth workflows and real-time data accessibility

## Authentication

  ### 1. Register a New Application(If you don't have already)
  Go to the [Azure Portal](https://portal.azure.com)
  Navigate to Azure Active Directory > App registrations > New registration.
  Provide the following details:
  Name: Enter a name for your app (e.g., Airbyte Lists Connector).
  Supported account types: Choose the option that suits your needs (e.g., Single tenant or Multitenant).
  Redirect URI: Leave it blank for now or provide one if needed.
  Click Register.

  ### 2. Configure API Permissions
  In the App Overview page, go to API Permissions > Add a permission.
  Select Microsoft Graph.
  Choose  Application Permissions:
  `Sites.Read.All`,
 ` Sites.ReadWrite.All`
  After adding the permissions, click Grant admin consent to allow these permissions.

  ### 3. Create Client Secret
  In your registered app, go to Certificates & secrets > New client secret.
  Add a description and select an expiration period.
  Click Add and copy the client secret value (you won’t be able to see it again).

  ### 4. Obtain Client ID and Tenant ID
  Go to the Overview tab in your registered app.
  Copy the Application (client) ID and Directory (tenant) ID – you’ll need these for authentication.

  ### 5. Set Redirect URI 
  Go to Authentication > Add a platform.
  Select Web and enter your redirect URI (e.g., http://localhost:3000).
  Enable Access tokens and ID tokens if using OAuth2 for authentication.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `site_id` | `string` | Site Id.  |  |
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `application_id_uri` | `string` | Application Id URI.  |  |
| `tenant_id` | `string` | Tenant Id.  |  |
| `domain` | `string` | Domain.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| lists | id | DefaultPaginator | ✅ |  ❌  |
| listcontenttypes | id | DefaultPaginator | ✅ |  ❌  |
| listitems |  | DefaultPaginator | ✅ |  ❌  |
| items |  | DefaultPaginator | ✅ |  ❌  |
| columnvalues | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.11 | 2025-01-18 | [51824](https://github.com/airbytehq/airbyte/pull/51824) | Update dependencies |
| 0.0.10 | 2025-01-11 | [51148](https://github.com/airbytehq/airbyte/pull/51148) | Update dependencies |
| 0.0.9 | 2024-12-28 | [50613](https://github.com/airbytehq/airbyte/pull/50613) | Update dependencies |
| 0.0.8 | 2024-12-21 | [50117](https://github.com/airbytehq/airbyte/pull/50117) | Update dependencies |
| 0.0.7 | 2024-12-14 | [49598](https://github.com/airbytehq/airbyte/pull/49598) | Update dependencies |
| 0.0.6 | 2024-12-12 | [49229](https://github.com/airbytehq/airbyte/pull/49229) | Update dependencies |
| 0.0.5 | 2024-12-11 | [48952](https://github.com/airbytehq/airbyte/pull/48952) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.4 | 2024-11-04 | [48202](https://github.com/airbytehq/airbyte/pull/48202) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47925](https://github.com/airbytehq/airbyte/pull/47925) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47544](https://github.com/airbytehq/airbyte/pull/47544) | Update dependencies |
| 0.0.1 | 2024-10-18 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
