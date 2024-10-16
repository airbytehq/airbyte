# Sigma Computing
This is the setup for the Sigma Computing source that ingests data from the sigma API. 

Sigma is next-generation analytics and business intelligence that scales billions of records using spreadsheets, SQL, Python, or AI—without compromising speed and security https://www.sigmacomputing.com/

In order to use this source, you must first create an account on Sigma Computing. Go to Account General Settings and review the Site section for the Cloud provider, this will be used to find the base url of your API. Compare it at https://help.sigmacomputing.com/reference/get-started-sigma-api

Next, head over to Developer Access and click on create. This will generate your Client ID and Client Secret required by the API. You can learn more about the API here https://help.sigmacomputing.com/reference


## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `client_refresh_token` | `string` | Refresh token.  |  |
| `oauth_access_token` | `string` | Access token. The current access token. This field might be overridden by the connector based on the token refresh endpoint response. |  |
| `oauth_token_expiry_date` | `string` | Token expiry date. The date the current access token expires in. This field might be overridden by the connector based on the token refresh endpoint response. |  |
| `base_url` | `string` | Base URL. The base url of your sigma organization |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| files | id | DefaultPaginator | ✅ |  ❌  |
| connections | connectionId | DefaultPaginator | ✅ |  ❌  |
| datasets | datasetId | DefaultPaginator | ✅ |  ❌  |
| members | memberId | DefaultPaginator | ✅ |  ❌  |
| teams | teamId | DefaultPaginator | ✅ |  ❌  |
| templates | templateId | DefaultPaginator | ✅ |  ❌  |
| workspaces | workspaceId | DefaultPaginator | ✅ |  ❌  |
| workbooks | workbookId | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-13 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
