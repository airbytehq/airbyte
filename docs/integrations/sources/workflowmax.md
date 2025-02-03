# Workflowmax
This directory contains the manifest-only connector for [`source-workflowmax`](https://app.workflowmax2.com/).

## Documentation reference:
Visit `https://app.swaggerhub.com/apis-docs/WorkflowMax-BlueRock/WorkflowMax-BlueRock-OpenAPI3/0.1#/` for V1 API documentation

## Authentication setup
`Workflowmax` uses bearer token authentication, You have to input your bearer access_token in the field of API key for authentication.

### Using postman to get access token 
- Move to Authorization tab of an empty http request and selected Oauth 2.0
- Set use token type as `access token`
- Set header prefix as `Bearer`
- Set grant type as `Authorization code`
- Check `Authorize using browser`
- Set Auth URL as `https://oauth.workflowmax2.com/oauth/authorize`
- Set Access token URL as `https://oauth.workflowmax2.com/oauth/token`
- Set Client ID, Client secret, Scope defined as your Workflowmax settings, Example Scope: `openid profile email workflowmax offline_access`
- Set state as any number, Example: `1`
- Set Client Authentication as `Send as Basic Auth Header`
  Click `Get New Access Token` for retrieving access token

Then authorize your source with the required information. 
1. Go to set up `The Source` page.
2. Enter your Workflowmax application's access token.
3. Click Save button.
 

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key_2` | `string` | API Key.  |  |
| `account_id` | `string` | Account ID. The account id for workflowmax |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| stafflist | UUID | DefaultPaginator | ✅ |  ❌  |
| clientlist | UUID | DefaultPaginator | ✅ |  ❌  |
| clients_documents | uuid | No pagination | ✅ |  ❌  |
| clientgrouplist | UUID | DefaultPaginator | ✅ |  ❌  |
| costlist | UUID | DefaultPaginator | ✅ |  ❌  |
| invoice_current | UUID | DefaultPaginator | ✅ |  ❌  |
| invoicelist | UUID | DefaultPaginator | ✅ |  ✅  |
| joblist | UUID | DefaultPaginator | ✅ |  ✅  |
| job_tasks | UUID | DefaultPaginator | ✅ |  ✅  |
| leadlist | UUID | DefaultPaginator | ✅ |  ✅  |
| purchaseorderlist | ID | DefaultPaginator | ✅ |  ✅  |
| tasklist | UUID | DefaultPaginator | ✅ |  ❌  |
| quotelist | UUID | DefaultPaginator | ✅ |  ✅  |
| supplierlist | UUID | DefaultPaginator | ✅ |  ❌  |
| timelist | UUID | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.9 | 2025-02-01 | [53070](https://github.com/airbytehq/airbyte/pull/53070) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52441](https://github.com/airbytehq/airbyte/pull/52441) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51947](https://github.com/airbytehq/airbyte/pull/51947) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51422](https://github.com/airbytehq/airbyte/pull/51422) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50782](https://github.com/airbytehq/airbyte/pull/50782) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50324](https://github.com/airbytehq/airbyte/pull/50324) | Update dependencies |
| 0.0.3 | 2024-12-14 | [47888](https://github.com/airbytehq/airbyte/pull/47888) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47527](https://github.com/airbytehq/airbyte/pull/47527) | Update dependencies |
| 0.0.1 | 2024-10-13 | [46866](https://github.com/airbytehq/airbyte/pull/46866) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
