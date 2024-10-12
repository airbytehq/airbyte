# Zoho Desk
This directory contains the manifest-only connector for source-zoho-desk

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `organization_Id` | `string` | organization_Id. Organization ID |  |
| `include_custom_domain` | `boolean` | include Custom Domain. Key that denotes if the customDomain field must be included in the API response |  |
| `api_key` | `string` | API Key.  |  |
| `agent_id` | `string` | agent_id. Agent unique id |  |
| `include` | `string` | include. Secondary information related to the agent. Values allowed are profile, role, associatedDepartments, associatedChatDepartments and verifiedEmails. You can include all four values by separating them with commas in the API request. |  |
| `status` | `string` | status. Parameter that filters agents based on their activation status: ACTIVE or DISABLED |  |
| `isconfirmed` | `boolean` | isConfirmed. Filters Confirmed &amp; Unconfirmed agents |  |
| `include_light_agent` | `string` | include Light Agent. count Light Agent |  |
| `agent_ids` | `string` | agent_ids. agent ids |  |
| `profile_id` | `string` | profile_id. Profile ID |  |
| `limit` | `integer` | limit. Number of roles to display. The default value is 15 and the maximum value allowed is 500. |  |
| `isvisible` | `boolean` | isVisible.  Key that filters roles according to their visibility in the UI |  |
| `isdefault` | `boolean` | isDefault. Key that denotes whether the roles must be default roles or custom roles |  |
| `searchstr` | `string` | searchStr. String to search for roles by name or description. The string must contain at least one character. Three search methods are supported: 1) string* - Searches for roles whose name or description start with the string, 2) *string* - Searches for roles whose name or description contain the string, 3) string - Searches for roles whose name or description is an exact match for the string |  |
| `team_id` | `string` | team_id. Team ID |  |
| `department_id` | `string` | department_id. Department Id |  |
| `ticket_id` | `string` | ticket_id. ticket id |  |
| `account_id` | `string` | account_id. Account ID |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| organization |  | No pagination | ✅ |  ❌  |
| organizations |  | No pagination | ✅ |  ❌  |
| accessible_organizations |  | DefaultPaginator | ✅ |  ❌  |
| agent |  | DefaultPaginator | ✅ |  ❌  |
| agents | id | DefaultPaginator | ✅ |  ❌  |
| agent_details_by_id | id | DefaultPaginator | ✅ |  ❌  |
| profiles | id | DefaultPaginator | ✅ |  ❌  |
| roles | id | DefaultPaginator | ✅ |  ❌  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| team_members | id | DefaultPaginator | ✅ |  ❌  |
| departments |  | DefaultPaginator | ✅ |  ❌  |
| channels | code | DefaultPaginator | ✅ |  ❌  |
| tickets | id | DefaultPaginator | ✅ |  ❌  |
| all_threads | id | DefaultPaginator | ✅ |  ❌  |
| get_latest_thread | id | DefaultPaginator | ✅ |  ❌  |
| list_contacts | id | DefaultPaginator | ✅ |  ❌  |
| webhooks |  | DefaultPaginator | ✅ |  ❌  |
| accounts | id | DefaultPaginator | ✅ |  ❌  |
| contracts | id | DefaultPaginator | ✅ |  ❌  |
| tasks | id | DefaultPaginator | ✅ |  ❌  |
| products | id | DefaultPaginator | ✅ |  ❌  |
| articles | id | DefaultPaginator | ✅ |  ❌  |
| events | id | DefaultPaginator | ✅ |  ❌  |
| modules | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| ticket_activities | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-12 | | Initial release by [@itsxdamdam](https://github.com/itsxdamdam) via Connector Builder |

</details>
