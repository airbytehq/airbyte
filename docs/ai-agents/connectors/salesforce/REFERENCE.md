# Salesforce full reference

This is the full reference documentation for the Salesforce agent connector.

## Supported entities and actions

The Salesforce connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Sobjects | [List](#sobjects-list), [Create](#sobjects-create), [Get](#sobjects-get), [Update](#sobjects-update), [Delete](#sobjects-delete) |
| Accounts | [List](#accounts-list), [Create](#accounts-create), [Get](#accounts-get), [Update](#accounts-update), [Delete](#accounts-delete), [API Search](#accounts-api-search), [Context Store Search](#accounts-context-store-search) |
| Contacts | [List](#contacts-list), [Create](#contacts-create), [Get](#contacts-get), [Update](#contacts-update), [Delete](#contacts-delete), [API Search](#contacts-api-search), [Context Store Search](#contacts-context-store-search) |
| Leads | [List](#leads-list), [Create](#leads-create), [Get](#leads-get), [Update](#leads-update), [Delete](#leads-delete), [API Search](#leads-api-search), [Context Store Search](#leads-context-store-search) |
| Opportunities | [List](#opportunities-list), [Create](#opportunities-create), [Get](#opportunities-get), [Update](#opportunities-update), [Delete](#opportunities-delete), [API Search](#opportunities-api-search), [Context Store Search](#opportunities-context-store-search) |
| Tasks | [List](#tasks-list), [Create](#tasks-create), [Get](#tasks-get), [Update](#tasks-update), [Delete](#tasks-delete), [API Search](#tasks-api-search), [Context Store Search](#tasks-context-store-search) |
| Events | [List](#events-list), [Create](#events-create), [Get](#events-get), [Update](#events-update), [Delete](#events-delete), [API Search](#events-api-search) |
| Campaigns | [List](#campaigns-list), [Create](#campaigns-create), [Get](#campaigns-get), [Update](#campaigns-update), [Delete](#campaigns-delete), [API Search](#campaigns-api-search) |
| Cases | [List](#cases-list), [Create](#cases-create), [Get](#cases-get), [Update](#cases-update), [Delete](#cases-delete), [API Search](#cases-api-search) |
| Notes | [List](#notes-list), [Create](#notes-create), [Get](#notes-get), [Update](#notes-update), [Delete](#notes-delete), [API Search](#notes-api-search) |
| Content Versions | [List](#content-versions-list), [Get](#content-versions-get), [Download](#content-versions-download) |
| Attachments | [List](#attachments-list), [Get](#attachments-get), [Download](#attachments-download) |
| Reports | [List](#reports-list), [Get](#reports-get) |
| Users | [List](#users-list), [Create](#users-create), [Get](#users-get), [Update](#users-update), [Context Store Search](#users-context-store-search) |
| Opportunity Stages | [List](#opportunity-stages-list), [Get](#opportunity-stages-get), [Context Store Search](#opportunity-stages-context-store-search) |
| Query | [List](#query-list) |

## Sobjects

### Sobjects List

Returns a list of all available Salesforce objects (sObjects) in the organization.
This endpoint is used for health checks to verify authentication and connectivity.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "sobjects",
  "action": "list"
}'
```

#### Python SDK

```python
await salesforce.sobjects.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sobjects",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `name` | `string` |  |
| `label` | `null \| string` |  |
| `labelPlural` | `null \| string` |  |
| `keyPrefix` | `null \| string` |  |
| `custom` | `null \| boolean` |  |
| `queryable` | `null \| boolean` |  |
| `searchable` | `null \| boolean` |  |
| `createable` | `null \| boolean` |  |
| `updateable` | `null \| boolean` |  |
| `deletable` | `null \| boolean` |  |
| `urls` | `null \| object` |  |


</details>

### Sobjects Create

Create a record for any Salesforce SObject by name. Works for standard
objects (Account, Contact, ...) and custom objects (e.g. `MyObject__c`).
Pass the SObject's API name in the `sobjectType` path parameter and the
field values as a free-form JSON body.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "sobjects",
  "action": "create",
  "params": {
    "sobjectType": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.sobjects.create(
    sobject_type="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sobjects",
    "action": "create",
    "params": {
        "sobjectType": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sobjectType` | `string` | Yes | SObject API name (e.g., `Account`, `MyCustomObject__c`). |


### Sobjects Get

Fetch a single record from any SObject by id. Works for standard and
custom objects.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "sobjects",
  "action": "get",
  "params": {
    "sobjectType": "<str>",
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.sobjects.get(
    sobject_type="<str>",
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sobjects",
    "action": "get",
    "params": {
        "sobjectType": "<str>",
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sobjectType` | `string` | Yes | SObject API name. |
| `id` | `string` | Yes | Salesforce record Id. |
| `fields` | `string` | No | Comma-separated field names to return. Omit for default fields. |


### Sobjects Update

Update fields on an existing record. Pass only the fields you want to
change in the JSON body; Salesforce leaves the rest untouched.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "sobjects",
  "action": "update",
  "params": {
    "sobjectType": "<str>",
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.sobjects.update(
    sobject_type="<str>",
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sobjects",
    "action": "update",
    "params": {
        "sobjectType": "<str>",
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sobjectType` | `string` | Yes | SObject API name. |
| `id` | `string` | Yes | Salesforce record Id. |


### Sobjects Delete

Delete a record by id. Salesforce moves the record to the Recycle Bin
(15-day retention) for most objects.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "sobjects",
  "action": "delete",
  "params": {
    "sobjectType": "<str>",
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.sobjects.delete(
    sobject_type="<str>",
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sobjects",
    "action": "delete",
    "params": {
        "sobjectType": "<str>",
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sobjectType` | `string` | Yes | SObject API name. |
| `id` | `string` | Yes | Salesforce record Id. |


## Accounts

### Accounts List

Returns a list of accounts via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.
For "top", "largest", or "highest-value" account requests, rank by a financial account value field
such as ARR, annual recurring revenue, revenue, annual revenue, amount, or value. ARR is often a
Salesforce custom field, so prefer the customer's org-specific ARR or account value field when
available. If no better org-specific field is visible, `AnnualRevenue` is the standard Account
fallback. Do not use `NumberOfEmployees` unless the user asks for employee count, headcount,
company size, or largest employer.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "accounts",
  "action": "list",
  "params": {
    "q": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.accounts.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "list",
    "params": {
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query for accounts. Default returns up to 200 records.
To change the limit, provide your own query with a LIMIT clause.

Examples:
  SELECT FIELDS(STANDARD) FROM Account ORDER BY LastModifiedDate DESC LIMIT 50
  SELECT Id, Name, Owner.Name, Owner.Email FROM Account LIMIT 50
  SELECT Id, Name, Parent.Name, Owner.Name FROM Account WHERE Industry = 'Technology' LIMIT 50
  SELECT Id, Name, AnnualRevenue FROM Account ORDER BY AnnualRevenue DESC LIMIT 10
  SELECT Id, Name, NumberOfEmployees FROM Account ORDER BY NumberOfEmployees DESC LIMIT 10

Use dot-path traversal (Owner.Name, Parent.Name) to resolve relationship
fields inline instead of returning raw IDs.
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Name` | `string` |  |
| `attributes` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |

</details>

### Accounts Create

Create an account

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "accounts",
  "action": "create",
  "params": {
    "Name": "<str>",
    "AccountNumber": "<str>",
    "Type": "<str>",
    "Industry": "<str>",
    "Phone": "<str>",
    "Website": "<str>",
    "BillingStreet": "<str>",
    "BillingCity": "<str>",
    "BillingState": "<str>",
    "BillingPostalCode": "<str>",
    "BillingCountry": "<str>",
    "AnnualRevenue": 0.0,
    "NumberOfEmployees": 0,
    "Description": "<str>",
    "OwnerId": "<str>",
    "ParentId": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.accounts.create(
    name="<str>",
    account_number="<str>",
    type="<str>",
    industry="<str>",
    phone="<str>",
    website="<str>",
    billing_street="<str>",
    billing_city="<str>",
    billing_state="<str>",
    billing_postal_code="<str>",
    billing_country="<str>",
    annual_revenue=0.0,
    number_of_employees=0,
    description="<str>",
    owner_id="<str>",
    parent_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "create",
    "params": {
        "Name": "<str>",
        "AccountNumber": "<str>",
        "Type": "<str>",
        "Industry": "<str>",
        "Phone": "<str>",
        "Website": "<str>",
        "BillingStreet": "<str>",
        "BillingCity": "<str>",
        "BillingState": "<str>",
        "BillingPostalCode": "<str>",
        "BillingCountry": "<str>",
        "AnnualRevenue": 0.0,
        "NumberOfEmployees": 0,
        "Description": "<str>",
        "OwnerId": "<str>",
        "ParentId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `Name` | `string` | Yes | Account name. |
| `AccountNumber` | `string` | No |  |
| `Type` | `string` | No |  |
| `Industry` | `string` | No |  |
| `Phone` | `string` | No |  |
| `Website` | `string` | No |  |
| `BillingStreet` | `string` | No |  |
| `BillingCity` | `string` | No |  |
| `BillingState` | `string` | No |  |
| `BillingPostalCode` | `string` | No |  |
| `BillingCountry` | `string` | No |  |
| `AnnualRevenue` | `number` | No |  |
| `NumberOfEmployees` | `integer` | No |  |
| `Description` | `string` | No |  |
| `OwnerId` | `string` | No |  |
| `ParentId` | `string` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `success` | `boolean` |  |
| `errors` | `array<object>` |  |


</details>

### Accounts Get

Get a single account by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "accounts",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.accounts.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce Account ID (18-character ID starting with '001') |
| `fields` | `string` | No | Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
Example: "Id,Name,Industry,AnnualRevenue,Website"
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Name` | `string` |  |
| `attributes` | `object` |  |


</details>

### Accounts Update

Update an account

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "accounts",
  "action": "update",
  "params": {
    "Name": "<str>",
    "AccountNumber": "<str>",
    "Type": "<str>",
    "Industry": "<str>",
    "Phone": "<str>",
    "Website": "<str>",
    "BillingStreet": "<str>",
    "BillingCity": "<str>",
    "BillingState": "<str>",
    "BillingPostalCode": "<str>",
    "BillingCountry": "<str>",
    "AnnualRevenue": 0.0,
    "NumberOfEmployees": 0,
    "Description": "<str>",
    "OwnerId": "<str>",
    "ParentId": "<str>",
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.accounts.update(
    name="<str>",
    account_number="<str>",
    type="<str>",
    industry="<str>",
    phone="<str>",
    website="<str>",
    billing_street="<str>",
    billing_city="<str>",
    billing_state="<str>",
    billing_postal_code="<str>",
    billing_country="<str>",
    annual_revenue=0.0,
    number_of_employees=0,
    description="<str>",
    owner_id="<str>",
    parent_id="<str>",
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "update",
    "params": {
        "Name": "<str>",
        "AccountNumber": "<str>",
        "Type": "<str>",
        "Industry": "<str>",
        "Phone": "<str>",
        "Website": "<str>",
        "BillingStreet": "<str>",
        "BillingCity": "<str>",
        "BillingState": "<str>",
        "BillingPostalCode": "<str>",
        "BillingCountry": "<str>",
        "AnnualRevenue": 0.0,
        "NumberOfEmployees": 0,
        "Description": "<str>",
        "OwnerId": "<str>",
        "ParentId": "<str>",
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `Name` | `string` | Yes | Account name. |
| `AccountNumber` | `string` | No |  |
| `Type` | `string` | No |  |
| `Industry` | `string` | No |  |
| `Phone` | `string` | No |  |
| `Website` | `string` | No |  |
| `BillingStreet` | `string` | No |  |
| `BillingCity` | `string` | No |  |
| `BillingState` | `string` | No |  |
| `BillingPostalCode` | `string` | No |  |
| `BillingCountry` | `string` | No |  |
| `AnnualRevenue` | `number` | No |  |
| `NumberOfEmployees` | `integer` | No |  |
| `Description` | `string` | No |  |
| `OwnerId` | `string` | No |  |
| `ParentId` | `string` | No |  |
| `id` | `string` | Yes |  |


### Accounts Delete

Delete an account

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "accounts",
  "action": "delete",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.accounts.delete(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "delete",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes |  |


### Accounts API Search

Search for accounts using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields and objects.
Use SOQL (list action) for structured queries with specific field conditions.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "accounts",
  "action": "api_search",
  "params": {
    "q": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.accounts.api_search(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "api_search",
    "params": {
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOSL search query. Format: FIND \{searchTerm\} IN scope RETURNING Object(fields) [LIMIT n]
Examples:
- "FIND \{Acme\} IN ALL FIELDS RETURNING Account(Id,Name)"
- "FIND \{tech*\} IN NAME FIELDS RETURNING Account(Id,Name,Industry) LIMIT 50"
- "FIND \{\"exact phrase\"\} RETURNING Account(Id,Name,Website)"
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `searchRecords` | `array<object>` |  |


</details>

### Accounts Context Store Search

Search and filter accounts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "accounts",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "Id": "<str>"
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await salesforce.accounts.context_store_search(
    query={"filter": {"eq": {"Id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"Id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` | Unique identifier for the account record |
| `Name` | `string` | Name of the account or company |
| `AccountSource` | `string` | Source of the account record (e.g., Web, Referral) |
| `BillingAddress` | `object` | Complete billing address as a compound field |
| `BillingCity` | `string` | City portion of the billing address |
| `BillingCountry` | `string` | Country portion of the billing address |
| `BillingPostalCode` | `string` | Postal code portion of the billing address |
| `BillingState` | `string` | State or province portion of the billing address |
| `BillingStreet` | `string` | Street address portion of the billing address |
| `CreatedById` | `string` | ID of the user who created this account |
| `CreatedDate` | `string` | Date and time when the account was created |
| `Description` | `string` | Text description of the account |
| `Industry` | `string` | Primary business industry of the account |
| `IsDeleted` | `boolean` | Whether the account has been moved to the Recycle Bin |
| `LastActivityDate` | `string` | Date of the last activity associated with this account |
| `LastModifiedById` | `string` | ID of the user who last modified this account |
| `LastModifiedDate` | `string` | Date and time when the account was last modified |
| `NumberOfEmployees` | `integer` | Number of employees at the account |
| `OwnerId` | `string` | ID of the user who owns this account |
| `ParentId` | `string` | ID of the parent account, if this is a subsidiary |
| `Phone` | `string` | Primary phone number for the account |
| `ShippingAddress` | `object` | Complete shipping address as a compound field |
| `ShippingCity` | `string` | City portion of the shipping address |
| `ShippingCountry` | `string` | Country portion of the shipping address |
| `ShippingPostalCode` | `string` | Postal code portion of the shipping address |
| `ShippingState` | `string` | State or province portion of the shipping address |
| `ShippingStreet` | `string` | Street address portion of the shipping address |
| `Type` | `string` | Type of account (e.g., Customer, Partner, Competitor) |
| `Website` | `string` | Website URL for the account |
| `SystemModstamp` | `string` | System timestamp when the record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].Id` | `string` | Unique identifier for the account record |
| `data[].Name` | `string` | Name of the account or company |
| `data[].AccountSource` | `string` | Source of the account record (e.g., Web, Referral) |
| `data[].BillingAddress` | `object` | Complete billing address as a compound field |
| `data[].BillingCity` | `string` | City portion of the billing address |
| `data[].BillingCountry` | `string` | Country portion of the billing address |
| `data[].BillingPostalCode` | `string` | Postal code portion of the billing address |
| `data[].BillingState` | `string` | State or province portion of the billing address |
| `data[].BillingStreet` | `string` | Street address portion of the billing address |
| `data[].CreatedById` | `string` | ID of the user who created this account |
| `data[].CreatedDate` | `string` | Date and time when the account was created |
| `data[].Description` | `string` | Text description of the account |
| `data[].Industry` | `string` | Primary business industry of the account |
| `data[].IsDeleted` | `boolean` | Whether the account has been moved to the Recycle Bin |
| `data[].LastActivityDate` | `string` | Date of the last activity associated with this account |
| `data[].LastModifiedById` | `string` | ID of the user who last modified this account |
| `data[].LastModifiedDate` | `string` | Date and time when the account was last modified |
| `data[].NumberOfEmployees` | `integer` | Number of employees at the account |
| `data[].OwnerId` | `string` | ID of the user who owns this account |
| `data[].ParentId` | `string` | ID of the parent account, if this is a subsidiary |
| `data[].Phone` | `string` | Primary phone number for the account |
| `data[].ShippingAddress` | `object` | Complete shipping address as a compound field |
| `data[].ShippingCity` | `string` | City portion of the shipping address |
| `data[].ShippingCountry` | `string` | Country portion of the shipping address |
| `data[].ShippingPostalCode` | `string` | Postal code portion of the shipping address |
| `data[].ShippingState` | `string` | State or province portion of the shipping address |
| `data[].ShippingStreet` | `string` | Street address portion of the shipping address |
| `data[].Type` | `string` | Type of account (e.g., Customer, Partner, Competitor) |
| `data[].Website` | `string` | Website URL for the account |
| `data[].SystemModstamp` | `string` | System timestamp when the record was last modified |

</details>

## Contacts

### Contacts List

Returns a list of contacts via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "contacts",
  "action": "list",
  "params": {
    "q": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.contacts.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contacts",
    "action": "list",
    "params": {
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query for contacts. Default returns up to 200 records.
To change the limit, provide your own query with a LIMIT clause.

Examples:
  SELECT FIELDS(STANDARD) FROM Contact WHERE AccountId = '001xx...' LIMIT 50
  SELECT Id, FirstName, LastName, Account.Name, Owner.Name FROM Contact LIMIT 50
  SELECT Id, Name, Email, Account.Name, ReportsTo.Name FROM Contact WHERE AccountId != null LIMIT 50

Use dot-path traversal (Account.Name, Owner.Name, ReportsTo.Name) to resolve
relationship fields inline instead of returning raw IDs.
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Name` | `string` |  |
| `attributes` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |

</details>

### Contacts Create

Create a contact

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "contacts",
  "action": "create",
  "params": {
    "FirstName": "<str>",
    "LastName": "<str>",
    "Email": "<str>",
    "Phone": "<str>",
    "MobilePhone": "<str>",
    "Title": "<str>",
    "Department": "<str>",
    "AccountId": "<str>",
    "MailingStreet": "<str>",
    "MailingCity": "<str>",
    "MailingState": "<str>",
    "MailingPostalCode": "<str>",
    "MailingCountry": "<str>",
    "Description": "<str>",
    "OwnerId": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.contacts.create(
    first_name="<str>",
    last_name="<str>",
    email="<str>",
    phone="<str>",
    mobile_phone="<str>",
    title="<str>",
    department="<str>",
    account_id="<str>",
    mailing_street="<str>",
    mailing_city="<str>",
    mailing_state="<str>",
    mailing_postal_code="<str>",
    mailing_country="<str>",
    description="<str>",
    owner_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contacts",
    "action": "create",
    "params": {
        "FirstName": "<str>",
        "LastName": "<str>",
        "Email": "<str>",
        "Phone": "<str>",
        "MobilePhone": "<str>",
        "Title": "<str>",
        "Department": "<str>",
        "AccountId": "<str>",
        "MailingStreet": "<str>",
        "MailingCity": "<str>",
        "MailingState": "<str>",
        "MailingPostalCode": "<str>",
        "MailingCountry": "<str>",
        "Description": "<str>",
        "OwnerId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `FirstName` | `string` | No |  |
| `LastName` | `string` | Yes |  |
| `Email` | `string` | No |  |
| `Phone` | `string` | No |  |
| `MobilePhone` | `string` | No |  |
| `Title` | `string` | No |  |
| `Department` | `string` | No |  |
| `AccountId` | `string` | No |  |
| `MailingStreet` | `string` | No |  |
| `MailingCity` | `string` | No |  |
| `MailingState` | `string` | No |  |
| `MailingPostalCode` | `string` | No |  |
| `MailingCountry` | `string` | No |  |
| `Description` | `string` | No |  |
| `OwnerId` | `string` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `success` | `boolean` |  |
| `errors` | `array<object>` |  |


</details>

### Contacts Get

Get a single contact by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "contacts",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.contacts.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contacts",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce Contact ID (18-character ID starting with '003') |
| `fields` | `string` | No | Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
Example: "Id,FirstName,LastName,Email,Phone,AccountId"
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Name` | `string` |  |
| `attributes` | `object` |  |


</details>

### Contacts Update

Update a contact

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "contacts",
  "action": "update",
  "params": {
    "FirstName": "<str>",
    "LastName": "<str>",
    "Email": "<str>",
    "Phone": "<str>",
    "MobilePhone": "<str>",
    "Title": "<str>",
    "Department": "<str>",
    "AccountId": "<str>",
    "MailingStreet": "<str>",
    "MailingCity": "<str>",
    "MailingState": "<str>",
    "MailingPostalCode": "<str>",
    "MailingCountry": "<str>",
    "Description": "<str>",
    "OwnerId": "<str>",
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.contacts.update(
    first_name="<str>",
    last_name="<str>",
    email="<str>",
    phone="<str>",
    mobile_phone="<str>",
    title="<str>",
    department="<str>",
    account_id="<str>",
    mailing_street="<str>",
    mailing_city="<str>",
    mailing_state="<str>",
    mailing_postal_code="<str>",
    mailing_country="<str>",
    description="<str>",
    owner_id="<str>",
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contacts",
    "action": "update",
    "params": {
        "FirstName": "<str>",
        "LastName": "<str>",
        "Email": "<str>",
        "Phone": "<str>",
        "MobilePhone": "<str>",
        "Title": "<str>",
        "Department": "<str>",
        "AccountId": "<str>",
        "MailingStreet": "<str>",
        "MailingCity": "<str>",
        "MailingState": "<str>",
        "MailingPostalCode": "<str>",
        "MailingCountry": "<str>",
        "Description": "<str>",
        "OwnerId": "<str>",
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `FirstName` | `string` | No |  |
| `LastName` | `string` | Yes |  |
| `Email` | `string` | No |  |
| `Phone` | `string` | No |  |
| `MobilePhone` | `string` | No |  |
| `Title` | `string` | No |  |
| `Department` | `string` | No |  |
| `AccountId` | `string` | No |  |
| `MailingStreet` | `string` | No |  |
| `MailingCity` | `string` | No |  |
| `MailingState` | `string` | No |  |
| `MailingPostalCode` | `string` | No |  |
| `MailingCountry` | `string` | No |  |
| `Description` | `string` | No |  |
| `OwnerId` | `string` | No |  |
| `id` | `string` | Yes |  |


### Contacts Delete

Delete a contact

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "contacts",
  "action": "delete",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.contacts.delete(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contacts",
    "action": "delete",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes |  |


### Contacts API Search

Search for contacts using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "contacts",
  "action": "api_search",
  "params": {
    "q": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.contacts.api_search(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contacts",
    "action": "api_search",
    "params": {
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOSL search query. Format: FIND \{searchTerm\} RETURNING Contact(fields) [LIMIT n]
Examples:
- "FIND \{John\} IN NAME FIELDS RETURNING Contact(Id,FirstName,LastName,Email)"
- "FIND \{*@example.com\} IN EMAIL FIELDS RETURNING Contact(Id,Name,Email) LIMIT 25"
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `searchRecords` | `array<object>` |  |


</details>

### Contacts Context Store Search

Search and filter contacts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "contacts",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "Id": "<str>"
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await salesforce.contacts.context_store_search(
    query={"filter": {"eq": {"Id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contacts",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"Id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` | Unique identifier for the contact record |
| `AccountId` | `string` | ID of the account this contact is associated with |
| `CreatedById` | `string` | ID of the user who created this contact |
| `CreatedDate` | `string` | Date and time when the contact was created |
| `Department` | `string` | Department within the account where the contact works |
| `Email` | `string` | Email address of the contact |
| `FirstName` | `string` | First name of the contact |
| `IsDeleted` | `boolean` | Whether the contact has been moved to the Recycle Bin |
| `LastActivityDate` | `string` | Date of the last activity associated with this contact |
| `LastModifiedById` | `string` | ID of the user who last modified this contact |
| `LastModifiedDate` | `string` | Date and time when the contact was last modified |
| `LastName` | `string` | Last name of the contact |
| `LeadSource` | `string` | Source from which this contact originated |
| `MailingAddress` | `object` | Complete mailing address as a compound field |
| `MailingCity` | `string` | City portion of the mailing address |
| `MailingCountry` | `string` | Country portion of the mailing address |
| `MailingPostalCode` | `string` | Postal code portion of the mailing address |
| `MailingState` | `string` | State or province portion of the mailing address |
| `MailingStreet` | `string` | Street address portion of the mailing address |
| `MobilePhone` | `string` | Mobile phone number of the contact |
| `Name` | `string` | Full name of the contact (read-only, concatenation of first and last name) |
| `OwnerId` | `string` | ID of the user who owns this contact |
| `Phone` | `string` | Business phone number of the contact |
| `ReportsToId` | `string` | ID of the contact this contact reports to |
| `Title` | `string` | Job title of the contact |
| `SystemModstamp` | `string` | System timestamp when the record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].Id` | `string` | Unique identifier for the contact record |
| `data[].AccountId` | `string` | ID of the account this contact is associated with |
| `data[].CreatedById` | `string` | ID of the user who created this contact |
| `data[].CreatedDate` | `string` | Date and time when the contact was created |
| `data[].Department` | `string` | Department within the account where the contact works |
| `data[].Email` | `string` | Email address of the contact |
| `data[].FirstName` | `string` | First name of the contact |
| `data[].IsDeleted` | `boolean` | Whether the contact has been moved to the Recycle Bin |
| `data[].LastActivityDate` | `string` | Date of the last activity associated with this contact |
| `data[].LastModifiedById` | `string` | ID of the user who last modified this contact |
| `data[].LastModifiedDate` | `string` | Date and time when the contact was last modified |
| `data[].LastName` | `string` | Last name of the contact |
| `data[].LeadSource` | `string` | Source from which this contact originated |
| `data[].MailingAddress` | `object` | Complete mailing address as a compound field |
| `data[].MailingCity` | `string` | City portion of the mailing address |
| `data[].MailingCountry` | `string` | Country portion of the mailing address |
| `data[].MailingPostalCode` | `string` | Postal code portion of the mailing address |
| `data[].MailingState` | `string` | State or province portion of the mailing address |
| `data[].MailingStreet` | `string` | Street address portion of the mailing address |
| `data[].MobilePhone` | `string` | Mobile phone number of the contact |
| `data[].Name` | `string` | Full name of the contact (read-only, concatenation of first and last name) |
| `data[].OwnerId` | `string` | ID of the user who owns this contact |
| `data[].Phone` | `string` | Business phone number of the contact |
| `data[].ReportsToId` | `string` | ID of the contact this contact reports to |
| `data[].Title` | `string` | Job title of the contact |
| `data[].SystemModstamp` | `string` | System timestamp when the record was last modified |

</details>

## Leads

### Leads List

Returns a list of leads via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "leads",
  "action": "list",
  "params": {
    "q": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.leads.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "leads",
    "action": "list",
    "params": {
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query for leads. Default returns up to 200 records.
To change the limit, provide your own query with a LIMIT clause.

Examples:
  SELECT FIELDS(STANDARD) FROM Lead WHERE Status = 'Open' LIMIT 100
  SELECT Id, Name, Company, Owner.Name FROM Lead LIMIT 50
  SELECT Id, Name, Owner.Name, ConvertedAccount.Name, ConvertedContact.Name, ConvertedOpportunity.Name FROM Lead WHERE IsConverted = true LIMIT 50

Use dot-path traversal (Owner.Name, ConvertedAccount.Name, ConvertedContact.Name,
ConvertedOpportunity.Name) to resolve relationship fields inline instead of returning raw IDs.
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Name` | `string` |  |
| `attributes` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |

</details>

### Leads Create

Create a lead

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "leads",
  "action": "create",
  "params": {
    "FirstName": "<str>",
    "LastName": "<str>",
    "Company": "<str>",
    "Title": "<str>",
    "Email": "<str>",
    "Phone": "<str>",
    "MobilePhone": "<str>",
    "Website": "<str>",
    "Status": "<str>",
    "LeadSource": "<str>",
    "Industry": "<str>",
    "Rating": "<str>",
    "AnnualRevenue": 0.0,
    "NumberOfEmployees": 0,
    "Street": "<str>",
    "City": "<str>",
    "State": "<str>",
    "PostalCode": "<str>",
    "Country": "<str>",
    "Description": "<str>",
    "OwnerId": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.leads.create(
    first_name="<str>",
    last_name="<str>",
    company="<str>",
    title="<str>",
    email="<str>",
    phone="<str>",
    mobile_phone="<str>",
    website="<str>",
    status="<str>",
    lead_source="<str>",
    industry="<str>",
    rating="<str>",
    annual_revenue=0.0,
    number_of_employees=0,
    street="<str>",
    city="<str>",
    state="<str>",
    postal_code="<str>",
    country="<str>",
    description="<str>",
    owner_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "leads",
    "action": "create",
    "params": {
        "FirstName": "<str>",
        "LastName": "<str>",
        "Company": "<str>",
        "Title": "<str>",
        "Email": "<str>",
        "Phone": "<str>",
        "MobilePhone": "<str>",
        "Website": "<str>",
        "Status": "<str>",
        "LeadSource": "<str>",
        "Industry": "<str>",
        "Rating": "<str>",
        "AnnualRevenue": 0.0,
        "NumberOfEmployees": 0,
        "Street": "<str>",
        "City": "<str>",
        "State": "<str>",
        "PostalCode": "<str>",
        "Country": "<str>",
        "Description": "<str>",
        "OwnerId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `FirstName` | `string` | No |  |
| `LastName` | `string` | Yes |  |
| `Company` | `string` | Yes |  |
| `Title` | `string` | No |  |
| `Email` | `string` | No |  |
| `Phone` | `string` | No |  |
| `MobilePhone` | `string` | No |  |
| `Website` | `string` | No |  |
| `Status` | `string` | No |  |
| `LeadSource` | `string` | No |  |
| `Industry` | `string` | No |  |
| `Rating` | `string` | No |  |
| `AnnualRevenue` | `number` | No |  |
| `NumberOfEmployees` | `integer` | No |  |
| `Street` | `string` | No |  |
| `City` | `string` | No |  |
| `State` | `string` | No |  |
| `PostalCode` | `string` | No |  |
| `Country` | `string` | No |  |
| `Description` | `string` | No |  |
| `OwnerId` | `string` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `success` | `boolean` |  |
| `errors` | `array<object>` |  |


</details>

### Leads Get

Get a single lead by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "leads",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.leads.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "leads",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce Lead ID (18-character ID starting with '00Q') |
| `fields` | `string` | No | Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
Example: "Id,FirstName,LastName,Email,Company,Status,LeadSource"
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Name` | `string` |  |
| `attributes` | `object` |  |


</details>

### Leads Update

Update a lead

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "leads",
  "action": "update",
  "params": {
    "FirstName": "<str>",
    "LastName": "<str>",
    "Company": "<str>",
    "Title": "<str>",
    "Email": "<str>",
    "Phone": "<str>",
    "MobilePhone": "<str>",
    "Website": "<str>",
    "Status": "<str>",
    "LeadSource": "<str>",
    "Industry": "<str>",
    "Rating": "<str>",
    "AnnualRevenue": 0.0,
    "NumberOfEmployees": 0,
    "Street": "<str>",
    "City": "<str>",
    "State": "<str>",
    "PostalCode": "<str>",
    "Country": "<str>",
    "Description": "<str>",
    "OwnerId": "<str>",
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.leads.update(
    first_name="<str>",
    last_name="<str>",
    company="<str>",
    title="<str>",
    email="<str>",
    phone="<str>",
    mobile_phone="<str>",
    website="<str>",
    status="<str>",
    lead_source="<str>",
    industry="<str>",
    rating="<str>",
    annual_revenue=0.0,
    number_of_employees=0,
    street="<str>",
    city="<str>",
    state="<str>",
    postal_code="<str>",
    country="<str>",
    description="<str>",
    owner_id="<str>",
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "leads",
    "action": "update",
    "params": {
        "FirstName": "<str>",
        "LastName": "<str>",
        "Company": "<str>",
        "Title": "<str>",
        "Email": "<str>",
        "Phone": "<str>",
        "MobilePhone": "<str>",
        "Website": "<str>",
        "Status": "<str>",
        "LeadSource": "<str>",
        "Industry": "<str>",
        "Rating": "<str>",
        "AnnualRevenue": 0.0,
        "NumberOfEmployees": 0,
        "Street": "<str>",
        "City": "<str>",
        "State": "<str>",
        "PostalCode": "<str>",
        "Country": "<str>",
        "Description": "<str>",
        "OwnerId": "<str>",
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `FirstName` | `string` | No |  |
| `LastName` | `string` | Yes |  |
| `Company` | `string` | Yes |  |
| `Title` | `string` | No |  |
| `Email` | `string` | No |  |
| `Phone` | `string` | No |  |
| `MobilePhone` | `string` | No |  |
| `Website` | `string` | No |  |
| `Status` | `string` | No |  |
| `LeadSource` | `string` | No |  |
| `Industry` | `string` | No |  |
| `Rating` | `string` | No |  |
| `AnnualRevenue` | `number` | No |  |
| `NumberOfEmployees` | `integer` | No |  |
| `Street` | `string` | No |  |
| `City` | `string` | No |  |
| `State` | `string` | No |  |
| `PostalCode` | `string` | No |  |
| `Country` | `string` | No |  |
| `Description` | `string` | No |  |
| `OwnerId` | `string` | No |  |
| `id` | `string` | Yes |  |


### Leads Delete

Delete a lead

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "leads",
  "action": "delete",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.leads.delete(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "leads",
    "action": "delete",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes |  |


### Leads API Search

Search for leads using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "leads",
  "action": "api_search",
  "params": {
    "q": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.leads.api_search(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "leads",
    "action": "api_search",
    "params": {
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOSL search query. Format: FIND \{searchTerm\} RETURNING Lead(fields) [LIMIT n]
Examples:
- "FIND \{Smith\} IN NAME FIELDS RETURNING Lead(Id,FirstName,LastName,Company,Status)"
- "FIND \{marketing\} IN ALL FIELDS RETURNING Lead(Id,Name,LeadSource) LIMIT 50"
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `searchRecords` | `array<object>` |  |


</details>

### Leads Context Store Search

Search and filter leads records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "leads",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "Id": "<str>"
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await salesforce.leads.context_store_search(
    query={"filter": {"eq": {"Id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "leads",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"Id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` | Unique identifier for the lead record |
| `Address` | `object` | Complete address as a compound field |
| `City` | `string` | City portion of the address |
| `Company` | `string` | Company or organization the lead works for |
| `ConvertedAccountId` | `string` | ID of the account created when lead was converted |
| `ConvertedContactId` | `string` | ID of the contact created when lead was converted |
| `ConvertedDate` | `string` | Date when the lead was converted |
| `ConvertedOpportunityId` | `string` | ID of the opportunity created when lead was converted |
| `Country` | `string` | Country portion of the address |
| `CreatedById` | `string` | ID of the user who created this lead |
| `CreatedDate` | `string` | Date and time when the lead was created |
| `Email` | `string` | Email address of the lead |
| `FirstName` | `string` | First name of the lead |
| `Industry` | `string` | Industry the lead's company operates in |
| `IsConverted` | `boolean` | Whether the lead has been converted to an account, contact, and opportunity |
| `IsDeleted` | `boolean` | Whether the lead has been moved to the Recycle Bin |
| `LastActivityDate` | `string` | Date of the last activity associated with this lead |
| `LastModifiedById` | `string` | ID of the user who last modified this lead |
| `LastModifiedDate` | `string` | Date and time when the lead was last modified |
| `LastName` | `string` | Last name of the lead |
| `LeadSource` | `string` | Source from which this lead originated |
| `MobilePhone` | `string` | Mobile phone number of the lead |
| `Name` | `string` | Full name of the lead (read-only, concatenation of first and last name) |
| `NumberOfEmployees` | `integer` | Number of employees at the lead's company |
| `OwnerId` | `string` | ID of the user who owns this lead |
| `Phone` | `string` | Phone number of the lead |
| `PostalCode` | `string` | Postal code portion of the address |
| `Rating` | `string` | Rating of the lead (e.g., Hot, Warm, Cold) |
| `State` | `string` | State or province portion of the address |
| `Status` | `string` | Current status of the lead in the sales process |
| `Street` | `string` | Street address portion of the address |
| `Title` | `string` | Job title of the lead |
| `Website` | `string` | Website URL for the lead's company |
| `SystemModstamp` | `string` | System timestamp when the record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].Id` | `string` | Unique identifier for the lead record |
| `data[].Address` | `object` | Complete address as a compound field |
| `data[].City` | `string` | City portion of the address |
| `data[].Company` | `string` | Company or organization the lead works for |
| `data[].ConvertedAccountId` | `string` | ID of the account created when lead was converted |
| `data[].ConvertedContactId` | `string` | ID of the contact created when lead was converted |
| `data[].ConvertedDate` | `string` | Date when the lead was converted |
| `data[].ConvertedOpportunityId` | `string` | ID of the opportunity created when lead was converted |
| `data[].Country` | `string` | Country portion of the address |
| `data[].CreatedById` | `string` | ID of the user who created this lead |
| `data[].CreatedDate` | `string` | Date and time when the lead was created |
| `data[].Email` | `string` | Email address of the lead |
| `data[].FirstName` | `string` | First name of the lead |
| `data[].Industry` | `string` | Industry the lead's company operates in |
| `data[].IsConverted` | `boolean` | Whether the lead has been converted to an account, contact, and opportunity |
| `data[].IsDeleted` | `boolean` | Whether the lead has been moved to the Recycle Bin |
| `data[].LastActivityDate` | `string` | Date of the last activity associated with this lead |
| `data[].LastModifiedById` | `string` | ID of the user who last modified this lead |
| `data[].LastModifiedDate` | `string` | Date and time when the lead was last modified |
| `data[].LastName` | `string` | Last name of the lead |
| `data[].LeadSource` | `string` | Source from which this lead originated |
| `data[].MobilePhone` | `string` | Mobile phone number of the lead |
| `data[].Name` | `string` | Full name of the lead (read-only, concatenation of first and last name) |
| `data[].NumberOfEmployees` | `integer` | Number of employees at the lead's company |
| `data[].OwnerId` | `string` | ID of the user who owns this lead |
| `data[].Phone` | `string` | Phone number of the lead |
| `data[].PostalCode` | `string` | Postal code portion of the address |
| `data[].Rating` | `string` | Rating of the lead (e.g., Hot, Warm, Cold) |
| `data[].State` | `string` | State or province portion of the address |
| `data[].Status` | `string` | Current status of the lead in the sales process |
| `data[].Street` | `string` | Street address portion of the address |
| `data[].Title` | `string` | Job title of the lead |
| `data[].Website` | `string` | Website URL for the lead's company |
| `data[].SystemModstamp` | `string` | System timestamp when the record was last modified |

</details>

## Opportunities

### Opportunities List

Returns a list of opportunities via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.
For "top", "largest", or "highest-value" opportunity requests, first choose a
visible financial opportunity field. Standard candidates include `Amount` for
total deal value and `ExpectedRevenue` for expected, weighted, or forecast revenue.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "opportunities",
  "action": "list",
  "params": {
    "q": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.opportunities.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "opportunities",
    "action": "list",
    "params": {
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query for opportunities. Default returns up to 200 records.
To change the limit, provide your own query with a LIMIT clause.

Examples:
  SELECT FIELDS(STANDARD) FROM Opportunity WHERE StageName = 'Closed Won' LIMIT 50
  SELECT Id, Name, Amount, Account.Name, Owner.Name FROM Opportunity LIMIT 50
  SELECT Id, Name, Amount, StageName, Account.Name FROM Opportunity ORDER BY Amount DESC LIMIT 10
  SELECT Id, Name, ExpectedRevenue, Probability, Amount FROM Opportunity ORDER BY ExpectedRevenue DESC LIMIT 10
  SELECT Id, Name, StageName, Account.Name, Account.Industry, Owner.Name, Campaign.Name FROM Opportunity WHERE CloseDate = THIS_QUARTER LIMIT 50

Use dot-path traversal (Account.Name, Owner.Name, Campaign.Name) to resolve
relationship fields inline instead of returning raw IDs.
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Name` | `string` |  |
| `attributes` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |

</details>

### Opportunities Create

Create an opportunity

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "opportunities",
  "action": "create",
  "params": {
    "Name": "<str>",
    "AccountId": "<str>",
    "StageName": "<str>",
    "CloseDate": "<str>",
    "Amount": 0.0,
    "Probability": 0.0,
    "Type": "<str>",
    "LeadSource": "<str>",
    "NextStep": "<str>",
    "CampaignId": "<str>",
    "ForecastCategoryName": "<str>",
    "Description": "<str>",
    "OwnerId": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.opportunities.create(
    name="<str>",
    account_id="<str>",
    stage_name="<str>",
    close_date="<str>",
    amount=0.0,
    probability=0.0,
    type="<str>",
    lead_source="<str>",
    next_step="<str>",
    campaign_id="<str>",
    forecast_category_name="<str>",
    description="<str>",
    owner_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "opportunities",
    "action": "create",
    "params": {
        "Name": "<str>",
        "AccountId": "<str>",
        "StageName": "<str>",
        "CloseDate": "<str>",
        "Amount": 0.0,
        "Probability": 0.0,
        "Type": "<str>",
        "LeadSource": "<str>",
        "NextStep": "<str>",
        "CampaignId": "<str>",
        "ForecastCategoryName": "<str>",
        "Description": "<str>",
        "OwnerId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `Name` | `string` | Yes |  |
| `AccountId` | `string` | No |  |
| `StageName` | `string` | Yes | Opportunity stage (e.g., Prospecting, Qualification, Closed Won). |
| `CloseDate` | `string` | Yes |  |
| `Amount` | `number` | No |  |
| `Probability` | `number` | No |  |
| `Type` | `string` | No |  |
| `LeadSource` | `string` | No |  |
| `NextStep` | `string` | No |  |
| `CampaignId` | `string` | No |  |
| `ForecastCategoryName` | `string` | No |  |
| `Description` | `string` | No |  |
| `OwnerId` | `string` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `success` | `boolean` |  |
| `errors` | `array<object>` |  |


</details>

### Opportunities Get

Get a single opportunity by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "opportunities",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.opportunities.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "opportunities",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce Opportunity ID (18-character ID starting with '006') |
| `fields` | `string` | No | Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
Example: "Id,Name,Amount,StageName,CloseDate,AccountId"
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Name` | `string` |  |
| `attributes` | `object` |  |


</details>

### Opportunities Update

Update an opportunity

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "opportunities",
  "action": "update",
  "params": {
    "Name": "<str>",
    "AccountId": "<str>",
    "StageName": "<str>",
    "CloseDate": "<str>",
    "Amount": 0.0,
    "Probability": 0.0,
    "Type": "<str>",
    "LeadSource": "<str>",
    "NextStep": "<str>",
    "CampaignId": "<str>",
    "ForecastCategoryName": "<str>",
    "Description": "<str>",
    "OwnerId": "<str>",
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.opportunities.update(
    name="<str>",
    account_id="<str>",
    stage_name="<str>",
    close_date="<str>",
    amount=0.0,
    probability=0.0,
    type="<str>",
    lead_source="<str>",
    next_step="<str>",
    campaign_id="<str>",
    forecast_category_name="<str>",
    description="<str>",
    owner_id="<str>",
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "opportunities",
    "action": "update",
    "params": {
        "Name": "<str>",
        "AccountId": "<str>",
        "StageName": "<str>",
        "CloseDate": "<str>",
        "Amount": 0.0,
        "Probability": 0.0,
        "Type": "<str>",
        "LeadSource": "<str>",
        "NextStep": "<str>",
        "CampaignId": "<str>",
        "ForecastCategoryName": "<str>",
        "Description": "<str>",
        "OwnerId": "<str>",
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `Name` | `string` | Yes |  |
| `AccountId` | `string` | No |  |
| `StageName` | `string` | Yes | Opportunity stage (e.g., Prospecting, Qualification, Closed Won). |
| `CloseDate` | `string` | Yes |  |
| `Amount` | `number` | No |  |
| `Probability` | `number` | No |  |
| `Type` | `string` | No |  |
| `LeadSource` | `string` | No |  |
| `NextStep` | `string` | No |  |
| `CampaignId` | `string` | No |  |
| `ForecastCategoryName` | `string` | No |  |
| `Description` | `string` | No |  |
| `OwnerId` | `string` | No |  |
| `id` | `string` | Yes |  |


### Opportunities Delete

Delete an opportunity

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "opportunities",
  "action": "delete",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.opportunities.delete(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "opportunities",
    "action": "delete",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes |  |


### Opportunities API Search

Search for opportunities using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "opportunities",
  "action": "api_search",
  "params": {
    "q": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.opportunities.api_search(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "opportunities",
    "action": "api_search",
    "params": {
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOSL search query. Format: FIND \{searchTerm\} RETURNING Opportunity(fields) [LIMIT n]
Examples:
- "FIND \{Enterprise\} IN NAME FIELDS RETURNING Opportunity(Id,Name,Amount,StageName)"
- "FIND \{renewal\} IN ALL FIELDS RETURNING Opportunity(Id,Name,CloseDate) LIMIT 25"
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `searchRecords` | `array<object>` |  |


</details>

### Opportunities Context Store Search

Search and filter opportunities records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "opportunities",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "Id": "<str>"
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await salesforce.opportunities.context_store_search(
    query={"filter": {"eq": {"Id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "opportunities",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"Id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` | Unique identifier for the opportunity record |
| `AccountId` | `string` | ID of the account associated with this opportunity |
| `Amount` | `number` | Estimated total sale amount |
| `CampaignId` | `string` | ID of the campaign that generated this opportunity |
| `CloseDate` | `string` | Expected close date for the opportunity |
| `ContactId` | `string` | ID of the primary contact for this opportunity |
| `CreatedById` | `string` | ID of the user who created this opportunity |
| `CreatedDate` | `string` | Date and time when the opportunity was created |
| `Description` | `string` | Text description of the opportunity |
| `ExpectedRevenue` | `number` | Expected revenue based on amount and probability |
| `ForecastCategory` | `string` | Forecast category for this opportunity |
| `ForecastCategoryName` | `string` | Name of the forecast category |
| `IsClosed` | `boolean` | Whether the opportunity is closed |
| `IsDeleted` | `boolean` | Whether the opportunity has been moved to the Recycle Bin |
| `IsWon` | `boolean` | Whether the opportunity was won |
| `LastActivityDate` | `string` | Date of the last activity associated with this opportunity |
| `LastModifiedById` | `string` | ID of the user who last modified this opportunity |
| `LastModifiedDate` | `string` | Date and time when the opportunity was last modified |
| `LeadSource` | `string` | Source from which this opportunity originated |
| `Name` | `string` | Name of the opportunity |
| `NextStep` | `string` | Description of the next step in closing the opportunity |
| `OwnerId` | `string` | ID of the user who owns this opportunity |
| `Probability` | `number` | Likelihood of closing the opportunity (percentage) |
| `StageName` | `string` | Current stage of the opportunity in the sales process |
| `Type` | `string` | Type of opportunity (e.g., New Business, Existing Business) |
| `SystemModstamp` | `string` | System timestamp when the record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].Id` | `string` | Unique identifier for the opportunity record |
| `data[].AccountId` | `string` | ID of the account associated with this opportunity |
| `data[].Amount` | `number` | Estimated total sale amount |
| `data[].CampaignId` | `string` | ID of the campaign that generated this opportunity |
| `data[].CloseDate` | `string` | Expected close date for the opportunity |
| `data[].ContactId` | `string` | ID of the primary contact for this opportunity |
| `data[].CreatedById` | `string` | ID of the user who created this opportunity |
| `data[].CreatedDate` | `string` | Date and time when the opportunity was created |
| `data[].Description` | `string` | Text description of the opportunity |
| `data[].ExpectedRevenue` | `number` | Expected revenue based on amount and probability |
| `data[].ForecastCategory` | `string` | Forecast category for this opportunity |
| `data[].ForecastCategoryName` | `string` | Name of the forecast category |
| `data[].IsClosed` | `boolean` | Whether the opportunity is closed |
| `data[].IsDeleted` | `boolean` | Whether the opportunity has been moved to the Recycle Bin |
| `data[].IsWon` | `boolean` | Whether the opportunity was won |
| `data[].LastActivityDate` | `string` | Date of the last activity associated with this opportunity |
| `data[].LastModifiedById` | `string` | ID of the user who last modified this opportunity |
| `data[].LastModifiedDate` | `string` | Date and time when the opportunity was last modified |
| `data[].LeadSource` | `string` | Source from which this opportunity originated |
| `data[].Name` | `string` | Name of the opportunity |
| `data[].NextStep` | `string` | Description of the next step in closing the opportunity |
| `data[].OwnerId` | `string` | ID of the user who owns this opportunity |
| `data[].Probability` | `number` | Likelihood of closing the opportunity (percentage) |
| `data[].StageName` | `string` | Current stage of the opportunity in the sales process |
| `data[].Type` | `string` | Type of opportunity (e.g., New Business, Existing Business) |
| `data[].SystemModstamp` | `string` | System timestamp when the record was last modified |

</details>

## Tasks

### Tasks List

Returns a list of tasks via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "tasks",
  "action": "list",
  "params": {
    "q": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.tasks.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "list",
    "params": {
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query for tasks. Default returns up to 200 records.
To change the limit, provide your own query with a LIMIT clause.

Examples:
  SELECT FIELDS(STANDARD) FROM Task WHERE Status = 'Not Started' LIMIT 100
  SELECT Id, Subject, Status, Owner.Name, Account.Name FROM Task LIMIT 50
  SELECT Id, Subject, Status, Owner.Name, Who.Name, What.Name FROM Task WHERE ActivityDate = THIS_WEEK LIMIT 50

Use dot-path traversal (Owner.Name, Account.Name) to resolve relationship
fields inline instead of returning raw IDs. Who.Name and What.Name resolve
polymorphic WhoId/WhatId references to the related record's name.
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Subject` | `string` |  |
| `attributes` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |

</details>

### Tasks Create

Create a task

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "tasks",
  "action": "create",
  "params": {
    "Subject": "<str>",
    "Status": "<str>",
    "Priority": "<str>",
    "ActivityDate": "<str>",
    "WhoId": "<str>",
    "WhatId": "<str>",
    "Description": "<str>",
    "Type": "<str>",
    "IsReminderSet": true,
    "ReminderDateTime": "2025-01-01T00:00:00Z",
    "OwnerId": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.tasks.create(
    subject="<str>",
    status="<str>",
    priority="<str>",
    activity_date="<str>",
    who_id="<str>",
    what_id="<str>",
    description="<str>",
    type="<str>",
    is_reminder_set=True,
    reminder_date_time="2025-01-01T00:00:00Z",
    owner_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "create",
    "params": {
        "Subject": "<str>",
        "Status": "<str>",
        "Priority": "<str>",
        "ActivityDate": "<str>",
        "WhoId": "<str>",
        "WhatId": "<str>",
        "Description": "<str>",
        "Type": "<str>",
        "IsReminderSet": True,
        "ReminderDateTime": "2025-01-01T00:00:00Z",
        "OwnerId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `Subject` | `string` | Yes |  |
| `Status` | `string` | No | Task status (e.g., Not Started, In Progress, Completed). |
| `Priority` | `string` | No |  |
| `ActivityDate` | `string` | No |  |
| `WhoId` | `string` | No | Related contact or lead Id. |
| `WhatId` | `string` | No | Related Account, Opportunity, or other object Id. |
| `Description` | `string` | No |  |
| `Type` | `string` | No |  |
| `IsReminderSet` | `boolean` | No |  |
| `ReminderDateTime` | `string` | No |  |
| `OwnerId` | `string` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `success` | `boolean` |  |
| `errors` | `array<object>` |  |


</details>

### Tasks Get

Get a single task by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "tasks",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.tasks.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce Task ID (18-character ID starting with '00T') |
| `fields` | `string` | No | Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
Example: "Id,Subject,Status,Priority,ActivityDate,WhoId,WhatId"
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Subject` | `string` |  |
| `attributes` | `object` |  |


</details>

### Tasks Update

Update a task

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "tasks",
  "action": "update",
  "params": {
    "Subject": "<str>",
    "Status": "<str>",
    "Priority": "<str>",
    "ActivityDate": "<str>",
    "WhoId": "<str>",
    "WhatId": "<str>",
    "Description": "<str>",
    "Type": "<str>",
    "IsReminderSet": true,
    "ReminderDateTime": "2025-01-01T00:00:00Z",
    "OwnerId": "<str>",
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.tasks.update(
    subject="<str>",
    status="<str>",
    priority="<str>",
    activity_date="<str>",
    who_id="<str>",
    what_id="<str>",
    description="<str>",
    type="<str>",
    is_reminder_set=True,
    reminder_date_time="2025-01-01T00:00:00Z",
    owner_id="<str>",
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "update",
    "params": {
        "Subject": "<str>",
        "Status": "<str>",
        "Priority": "<str>",
        "ActivityDate": "<str>",
        "WhoId": "<str>",
        "WhatId": "<str>",
        "Description": "<str>",
        "Type": "<str>",
        "IsReminderSet": True,
        "ReminderDateTime": "2025-01-01T00:00:00Z",
        "OwnerId": "<str>",
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `Subject` | `string` | Yes |  |
| `Status` | `string` | No | Task status (e.g., Not Started, In Progress, Completed). |
| `Priority` | `string` | No |  |
| `ActivityDate` | `string` | No |  |
| `WhoId` | `string` | No | Related contact or lead Id. |
| `WhatId` | `string` | No | Related Account, Opportunity, or other object Id. |
| `Description` | `string` | No |  |
| `Type` | `string` | No |  |
| `IsReminderSet` | `boolean` | No |  |
| `ReminderDateTime` | `string` | No |  |
| `OwnerId` | `string` | No |  |
| `id` | `string` | Yes |  |


### Tasks Delete

Delete a task

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "tasks",
  "action": "delete",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.tasks.delete(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "delete",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes |  |


### Tasks API Search

Search for tasks using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "tasks",
  "action": "api_search",
  "params": {
    "q": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.tasks.api_search(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "api_search",
    "params": {
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOSL search query. Format: FIND \{searchTerm\} RETURNING Task(fields) [LIMIT n]
Examples:
- "FIND \{follow up\} IN ALL FIELDS RETURNING Task(Id,Subject,Status,Priority)"
- "FIND \{call\} IN NAME FIELDS RETURNING Task(Id,Subject,ActivityDate) LIMIT 50"
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `searchRecords` | `array<object>` |  |


</details>

### Tasks Context Store Search

Search and filter tasks records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "tasks",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "Id": "<str>"
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await salesforce.tasks.context_store_search(
    query={"filter": {"eq": {"Id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"Id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` | Unique identifier for the task record |
| `AccountId` | `string` | ID of the account associated with this task |
| `ActivityDate` | `string` | Due date for the task |
| `CallDisposition` | `string` | Result of the call, if this task represents a call |
| `CallDurationInSeconds` | `integer` | Duration of the call in seconds |
| `CallType` | `string` | Type of call (Inbound, Outbound, Internal) |
| `CompletedDateTime` | `string` | Date and time when the task was completed |
| `CreatedById` | `string` | ID of the user who created this task |
| `CreatedDate` | `string` | Date and time when the task was created |
| `Description` | `string` | Text description or notes about the task |
| `IsClosed` | `boolean` | Whether the task has been completed |
| `IsDeleted` | `boolean` | Whether the task has been moved to the Recycle Bin |
| `IsHighPriority` | `boolean` | Whether the task is marked as high priority |
| `LastModifiedById` | `string` | ID of the user who last modified this task |
| `LastModifiedDate` | `string` | Date and time when the task was last modified |
| `OwnerId` | `string` | ID of the user who owns this task |
| `Priority` | `string` | Priority level of the task (High, Normal, Low) |
| `Status` | `string` | Current status of the task |
| `Subject` | `string` | Subject or title of the task |
| `TaskSubtype` | `string` | Subtype of the task (e.g., Call, Email, Task) |
| `Type` | `string` | Type of task |
| `WhatId` | `string` | ID of the related object (Account, Opportunity, etc.) |
| `WhoId` | `string` | ID of the related person (Contact or Lead) |
| `SystemModstamp` | `string` | System timestamp when the record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].Id` | `string` | Unique identifier for the task record |
| `data[].AccountId` | `string` | ID of the account associated with this task |
| `data[].ActivityDate` | `string` | Due date for the task |
| `data[].CallDisposition` | `string` | Result of the call, if this task represents a call |
| `data[].CallDurationInSeconds` | `integer` | Duration of the call in seconds |
| `data[].CallType` | `string` | Type of call (Inbound, Outbound, Internal) |
| `data[].CompletedDateTime` | `string` | Date and time when the task was completed |
| `data[].CreatedById` | `string` | ID of the user who created this task |
| `data[].CreatedDate` | `string` | Date and time when the task was created |
| `data[].Description` | `string` | Text description or notes about the task |
| `data[].IsClosed` | `boolean` | Whether the task has been completed |
| `data[].IsDeleted` | `boolean` | Whether the task has been moved to the Recycle Bin |
| `data[].IsHighPriority` | `boolean` | Whether the task is marked as high priority |
| `data[].LastModifiedById` | `string` | ID of the user who last modified this task |
| `data[].LastModifiedDate` | `string` | Date and time when the task was last modified |
| `data[].OwnerId` | `string` | ID of the user who owns this task |
| `data[].Priority` | `string` | Priority level of the task (High, Normal, Low) |
| `data[].Status` | `string` | Current status of the task |
| `data[].Subject` | `string` | Subject or title of the task |
| `data[].TaskSubtype` | `string` | Subtype of the task (e.g., Call, Email, Task) |
| `data[].Type` | `string` | Type of task |
| `data[].WhatId` | `string` | ID of the related object (Account, Opportunity, etc.) |
| `data[].WhoId` | `string` | ID of the related person (Contact or Lead) |
| `data[].SystemModstamp` | `string` | System timestamp when the record was last modified |

</details>

## Events

### Events List

Returns a list of events via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "events",
  "action": "list",
  "params": {
    "q": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.events.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "events",
    "action": "list",
    "params": {
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query for events. Default returns up to 200 records.
To change the limit, provide your own query with a LIMIT clause.

Examples:
  SELECT FIELDS(STANDARD) FROM Event WHERE StartDateTime \> TODAY LIMIT 50
  SELECT Id, Subject, StartDateTime, Owner.Name, Account.Name FROM Event LIMIT 50
  SELECT Id, Subject, StartDateTime, Owner.Name, Who.Name, What.Name FROM Event WHERE StartDateTime = THIS_WEEK LIMIT 50

Use dot-path traversal (Owner.Name, Account.Name) to resolve relationship
fields inline instead of returning raw IDs. Who.Name and What.Name resolve
polymorphic WhoId/WhatId references to the related record's name.
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Subject` | `string` |  |
| `attributes` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |

</details>

### Events Create

Create an event

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "events",
  "action": "create",
  "params": {
    "Subject": "<str>",
    "StartDateTime": "2025-01-01T00:00:00Z",
    "EndDateTime": "2025-01-01T00:00:00Z",
    "DurationInMinutes": 0,
    "Location": "<str>",
    "Description": "<str>",
    "WhoId": "<str>",
    "WhatId": "<str>",
    "IsAllDayEvent": true,
    "ShowAs": "<str>",
    "OwnerId": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.events.create(
    subject="<str>",
    start_date_time="2025-01-01T00:00:00Z",
    end_date_time="2025-01-01T00:00:00Z",
    duration_in_minutes=0,
    location="<str>",
    description="<str>",
    who_id="<str>",
    what_id="<str>",
    is_all_day_event=True,
    show_as="<str>",
    owner_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "events",
    "action": "create",
    "params": {
        "Subject": "<str>",
        "StartDateTime": "2025-01-01T00:00:00Z",
        "EndDateTime": "2025-01-01T00:00:00Z",
        "DurationInMinutes": 0,
        "Location": "<str>",
        "Description": "<str>",
        "WhoId": "<str>",
        "WhatId": "<str>",
        "IsAllDayEvent": True,
        "ShowAs": "<str>",
        "OwnerId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `Subject` | `string` | Yes |  |
| `StartDateTime` | `string` | Yes |  |
| `EndDateTime` | `string` | No |  |
| `DurationInMinutes` | `integer` | Yes |  |
| `Location` | `string` | No |  |
| `Description` | `string` | No |  |
| `WhoId` | `string` | No |  |
| `WhatId` | `string` | No |  |
| `IsAllDayEvent` | `boolean` | No |  |
| `ShowAs` | `string` | No |  |
| `OwnerId` | `string` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `success` | `boolean` |  |
| `errors` | `array<object>` |  |


</details>

### Events Get

Get a single event by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "events",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.events.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "events",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce Event ID (18-character ID starting with '00U') |
| `fields` | `string` | No | Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
Example: "Id,Subject,StartDateTime,EndDateTime,Location,WhoId,WhatId"
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Subject` | `string` |  |
| `attributes` | `object` |  |


</details>

### Events Update

Update an event

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "events",
  "action": "update",
  "params": {
    "Subject": "<str>",
    "StartDateTime": "2025-01-01T00:00:00Z",
    "EndDateTime": "2025-01-01T00:00:00Z",
    "DurationInMinutes": 0,
    "Location": "<str>",
    "Description": "<str>",
    "WhoId": "<str>",
    "WhatId": "<str>",
    "IsAllDayEvent": true,
    "ShowAs": "<str>",
    "OwnerId": "<str>",
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.events.update(
    subject="<str>",
    start_date_time="2025-01-01T00:00:00Z",
    end_date_time="2025-01-01T00:00:00Z",
    duration_in_minutes=0,
    location="<str>",
    description="<str>",
    who_id="<str>",
    what_id="<str>",
    is_all_day_event=True,
    show_as="<str>",
    owner_id="<str>",
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "events",
    "action": "update",
    "params": {
        "Subject": "<str>",
        "StartDateTime": "2025-01-01T00:00:00Z",
        "EndDateTime": "2025-01-01T00:00:00Z",
        "DurationInMinutes": 0,
        "Location": "<str>",
        "Description": "<str>",
        "WhoId": "<str>",
        "WhatId": "<str>",
        "IsAllDayEvent": True,
        "ShowAs": "<str>",
        "OwnerId": "<str>",
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `Subject` | `string` | Yes |  |
| `StartDateTime` | `string` | Yes |  |
| `EndDateTime` | `string` | No |  |
| `DurationInMinutes` | `integer` | Yes |  |
| `Location` | `string` | No |  |
| `Description` | `string` | No |  |
| `WhoId` | `string` | No |  |
| `WhatId` | `string` | No |  |
| `IsAllDayEvent` | `boolean` | No |  |
| `ShowAs` | `string` | No |  |
| `OwnerId` | `string` | No |  |
| `id` | `string` | Yes |  |


### Events Delete

Delete an event

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "events",
  "action": "delete",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.events.delete(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "events",
    "action": "delete",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes |  |


### Events API Search

Search for events using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "events",
  "action": "api_search",
  "params": {
    "q": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.events.api_search(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "events",
    "action": "api_search",
    "params": {
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOSL search query. Format: FIND \{searchTerm\} RETURNING Event(fields) [LIMIT n]
Examples:
- "FIND \{meeting\} IN ALL FIELDS RETURNING Event(Id,Subject,StartDateTime,Location)"
- "FIND \{demo\} IN NAME FIELDS RETURNING Event(Id,Subject,EndDateTime) LIMIT 25"
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `searchRecords` | `array<object>` |  |


</details>

## Campaigns

### Campaigns List

Returns a list of campaigns via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "campaigns",
  "action": "list",
  "params": {
    "q": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.campaigns.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
    "action": "list",
    "params": {
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query for campaigns. Default returns up to 200 records.
To change the limit, provide your own query with a LIMIT clause.

Examples:
  SELECT FIELDS(STANDARD) FROM Campaign WHERE IsActive = true LIMIT 50
  SELECT Id, Name, Type, Status, Owner.Name FROM Campaign LIMIT 50
  SELECT Id, Name, Owner.Name, Owner.Email, StartDate FROM Campaign WHERE IsActive = true LIMIT 50

Use dot-path traversal (Owner.Name) to resolve relationship fields inline
instead of returning raw IDs.
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Name` | `string` |  |
| `attributes` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |

</details>

### Campaigns Create

Create a campaign

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "campaigns",
  "action": "create",
  "params": {
    "Name": "<str>",
    "Type": "<str>",
    "Status": "<str>",
    "StartDate": "<str>",
    "EndDate": "<str>",
    "IsActive": true,
    "Description": "<str>",
    "ExpectedRevenue": 0.0,
    "BudgetedCost": 0.0,
    "ActualCost": 0.0,
    "ExpectedResponse": 0.0,
    "NumberSent": 0.0,
    "ParentId": "<str>",
    "OwnerId": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.campaigns.create(
    name="<str>",
    type="<str>",
    status="<str>",
    start_date="<str>",
    end_date="<str>",
    is_active=True,
    description="<str>",
    expected_revenue=0.0,
    budgeted_cost=0.0,
    actual_cost=0.0,
    expected_response=0.0,
    number_sent=0.0,
    parent_id="<str>",
    owner_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
    "action": "create",
    "params": {
        "Name": "<str>",
        "Type": "<str>",
        "Status": "<str>",
        "StartDate": "<str>",
        "EndDate": "<str>",
        "IsActive": True,
        "Description": "<str>",
        "ExpectedRevenue": 0.0,
        "BudgetedCost": 0.0,
        "ActualCost": 0.0,
        "ExpectedResponse": 0.0,
        "NumberSent": 0.0,
        "ParentId": "<str>",
        "OwnerId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `Name` | `string` | Yes |  |
| `Type` | `string` | No |  |
| `Status` | `string` | No |  |
| `StartDate` | `string` | No |  |
| `EndDate` | `string` | No |  |
| `IsActive` | `boolean` | No |  |
| `Description` | `string` | No |  |
| `ExpectedRevenue` | `number` | No |  |
| `BudgetedCost` | `number` | No |  |
| `ActualCost` | `number` | No |  |
| `ExpectedResponse` | `number` | No |  |
| `NumberSent` | `number` | No |  |
| `ParentId` | `string` | No |  |
| `OwnerId` | `string` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `success` | `boolean` |  |
| `errors` | `array<object>` |  |


</details>

### Campaigns Get

Get a single campaign by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "campaigns",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.campaigns.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce Campaign ID (18-character ID starting with '701') |
| `fields` | `string` | No | Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
Example: "Id,Name,Type,Status,StartDate,EndDate,IsActive"
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Name` | `string` |  |
| `attributes` | `object` |  |


</details>

### Campaigns Update

Update a campaign

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "campaigns",
  "action": "update",
  "params": {
    "Name": "<str>",
    "Type": "<str>",
    "Status": "<str>",
    "StartDate": "<str>",
    "EndDate": "<str>",
    "IsActive": true,
    "Description": "<str>",
    "ExpectedRevenue": 0.0,
    "BudgetedCost": 0.0,
    "ActualCost": 0.0,
    "ExpectedResponse": 0.0,
    "NumberSent": 0.0,
    "ParentId": "<str>",
    "OwnerId": "<str>",
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.campaigns.update(
    name="<str>",
    type="<str>",
    status="<str>",
    start_date="<str>",
    end_date="<str>",
    is_active=True,
    description="<str>",
    expected_revenue=0.0,
    budgeted_cost=0.0,
    actual_cost=0.0,
    expected_response=0.0,
    number_sent=0.0,
    parent_id="<str>",
    owner_id="<str>",
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
    "action": "update",
    "params": {
        "Name": "<str>",
        "Type": "<str>",
        "Status": "<str>",
        "StartDate": "<str>",
        "EndDate": "<str>",
        "IsActive": True,
        "Description": "<str>",
        "ExpectedRevenue": 0.0,
        "BudgetedCost": 0.0,
        "ActualCost": 0.0,
        "ExpectedResponse": 0.0,
        "NumberSent": 0.0,
        "ParentId": "<str>",
        "OwnerId": "<str>",
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `Name` | `string` | Yes |  |
| `Type` | `string` | No |  |
| `Status` | `string` | No |  |
| `StartDate` | `string` | No |  |
| `EndDate` | `string` | No |  |
| `IsActive` | `boolean` | No |  |
| `Description` | `string` | No |  |
| `ExpectedRevenue` | `number` | No |  |
| `BudgetedCost` | `number` | No |  |
| `ActualCost` | `number` | No |  |
| `ExpectedResponse` | `number` | No |  |
| `NumberSent` | `number` | No |  |
| `ParentId` | `string` | No |  |
| `OwnerId` | `string` | No |  |
| `id` | `string` | Yes |  |


### Campaigns Delete

Delete a campaign

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "campaigns",
  "action": "delete",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.campaigns.delete(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
    "action": "delete",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes |  |


### Campaigns API Search

Search for campaigns using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "campaigns",
  "action": "api_search",
  "params": {
    "q": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.campaigns.api_search(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
    "action": "api_search",
    "params": {
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOSL search query. Format: FIND \{searchTerm\} RETURNING Campaign(fields) [LIMIT n]
Examples:
- "FIND \{webinar\} IN ALL FIELDS RETURNING Campaign(Id,Name,Type,Status)"
- "FIND \{2024\} IN NAME FIELDS RETURNING Campaign(Id,Name,StartDate,IsActive) LIMIT 50"
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `searchRecords` | `array<object>` |  |


</details>

## Cases

### Cases List

Returns a list of cases via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "cases",
  "action": "list",
  "params": {
    "q": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.cases.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "cases",
    "action": "list",
    "params": {
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query for cases. Default returns up to 200 records.
To change the limit, provide your own query with a LIMIT clause.

Examples:
  SELECT FIELDS(STANDARD) FROM Case WHERE Status = 'New' LIMIT 100
  SELECT Id, CaseNumber, Subject, Account.Name, Owner.Name, Contact.Name FROM Case LIMIT 50
  SELECT Id, CaseNumber, Subject, Status, Account.Name, Owner.Name FROM Case WHERE Status = 'Escalated' LIMIT 50

Use dot-path traversal (Account.Name, Owner.Name, Contact.Name) to resolve
relationship fields inline instead of returning raw IDs.
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `CaseNumber` | `string` |  |
| `Subject` | `string` |  |
| `attributes` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |

</details>

### Cases Create

Create a case

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "cases",
  "action": "create",
  "params": {
    "Subject": "<str>",
    "Status": "<str>",
    "Priority": "<str>",
    "Origin": "<str>",
    "Type": "<str>",
    "Reason": "<str>",
    "Description": "<str>",
    "AccountId": "<str>",
    "ContactId": "<str>",
    "SuppliedName": "<str>",
    "SuppliedEmail": "<str>",
    "SuppliedPhone": "<str>",
    "SuppliedCompany": "<str>",
    "OwnerId": "<str>",
    "ParentId": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.cases.create(
    subject="<str>",
    status="<str>",
    priority="<str>",
    origin="<str>",
    type="<str>",
    reason="<str>",
    description="<str>",
    account_id="<str>",
    contact_id="<str>",
    supplied_name="<str>",
    supplied_email="<str>",
    supplied_phone="<str>",
    supplied_company="<str>",
    owner_id="<str>",
    parent_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "cases",
    "action": "create",
    "params": {
        "Subject": "<str>",
        "Status": "<str>",
        "Priority": "<str>",
        "Origin": "<str>",
        "Type": "<str>",
        "Reason": "<str>",
        "Description": "<str>",
        "AccountId": "<str>",
        "ContactId": "<str>",
        "SuppliedName": "<str>",
        "SuppliedEmail": "<str>",
        "SuppliedPhone": "<str>",
        "SuppliedCompany": "<str>",
        "OwnerId": "<str>",
        "ParentId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `Subject` | `string` | No |  |
| `Status` | `string` | No |  |
| `Priority` | `string` | No |  |
| `Origin` | `string` | No |  |
| `Type` | `string` | No |  |
| `Reason` | `string` | No |  |
| `Description` | `string` | No |  |
| `AccountId` | `string` | No |  |
| `ContactId` | `string` | No |  |
| `SuppliedName` | `string` | No |  |
| `SuppliedEmail` | `string` | No |  |
| `SuppliedPhone` | `string` | No |  |
| `SuppliedCompany` | `string` | No |  |
| `OwnerId` | `string` | No |  |
| `ParentId` | `string` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `success` | `boolean` |  |
| `errors` | `array<object>` |  |


</details>

### Cases Get

Get a single case by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "cases",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.cases.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "cases",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce Case ID (18-character ID starting with '500') |
| `fields` | `string` | No | Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
Example: "Id,CaseNumber,Subject,Status,Priority,ContactId,AccountId"
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `CaseNumber` | `string` |  |
| `Subject` | `string` |  |
| `attributes` | `object` |  |


</details>

### Cases Update

Update a case

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "cases",
  "action": "update",
  "params": {
    "Subject": "<str>",
    "Status": "<str>",
    "Priority": "<str>",
    "Origin": "<str>",
    "Type": "<str>",
    "Reason": "<str>",
    "Description": "<str>",
    "AccountId": "<str>",
    "ContactId": "<str>",
    "SuppliedName": "<str>",
    "SuppliedEmail": "<str>",
    "SuppliedPhone": "<str>",
    "SuppliedCompany": "<str>",
    "OwnerId": "<str>",
    "ParentId": "<str>",
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.cases.update(
    subject="<str>",
    status="<str>",
    priority="<str>",
    origin="<str>",
    type="<str>",
    reason="<str>",
    description="<str>",
    account_id="<str>",
    contact_id="<str>",
    supplied_name="<str>",
    supplied_email="<str>",
    supplied_phone="<str>",
    supplied_company="<str>",
    owner_id="<str>",
    parent_id="<str>",
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "cases",
    "action": "update",
    "params": {
        "Subject": "<str>",
        "Status": "<str>",
        "Priority": "<str>",
        "Origin": "<str>",
        "Type": "<str>",
        "Reason": "<str>",
        "Description": "<str>",
        "AccountId": "<str>",
        "ContactId": "<str>",
        "SuppliedName": "<str>",
        "SuppliedEmail": "<str>",
        "SuppliedPhone": "<str>",
        "SuppliedCompany": "<str>",
        "OwnerId": "<str>",
        "ParentId": "<str>",
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `Subject` | `string` | No |  |
| `Status` | `string` | No |  |
| `Priority` | `string` | No |  |
| `Origin` | `string` | No |  |
| `Type` | `string` | No |  |
| `Reason` | `string` | No |  |
| `Description` | `string` | No |  |
| `AccountId` | `string` | No |  |
| `ContactId` | `string` | No |  |
| `SuppliedName` | `string` | No |  |
| `SuppliedEmail` | `string` | No |  |
| `SuppliedPhone` | `string` | No |  |
| `SuppliedCompany` | `string` | No |  |
| `OwnerId` | `string` | No |  |
| `ParentId` | `string` | No |  |
| `id` | `string` | Yes |  |


### Cases Delete

Delete a case

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "cases",
  "action": "delete",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.cases.delete(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "cases",
    "action": "delete",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes |  |


### Cases API Search

Search for cases using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "cases",
  "action": "api_search",
  "params": {
    "q": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.cases.api_search(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "cases",
    "action": "api_search",
    "params": {
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOSL search query. Format: FIND \{searchTerm\} RETURNING Case(fields) [LIMIT n]
Examples:
- "FIND \{login issue\} IN ALL FIELDS RETURNING Case(Id,CaseNumber,Subject,Status)"
- "FIND \{urgent\} IN NAME FIELDS RETURNING Case(Id,Subject,Priority) LIMIT 25"
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `searchRecords` | `array<object>` |  |


</details>

## Notes

### Notes List

Returns a list of notes via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "notes",
  "action": "list",
  "params": {
    "q": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.notes.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "notes",
    "action": "list",
    "params": {
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query for notes. Default returns up to 200 records.
To change the limit, provide your own query with a LIMIT clause.

Examples:
  SELECT FIELDS(STANDARD) FROM Note WHERE ParentId = '001xx...' LIMIT 50
  SELECT Id, Title, Body, Owner.Name FROM Note LIMIT 50
  SELECT Id, Title, Owner.Name, CreatedDate FROM Note ORDER BY CreatedDate DESC LIMIT 50

Use dot-path traversal (Owner.Name) to resolve relationship fields inline
instead of returning raw IDs.
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Title` | `string` |  |
| `attributes` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |

</details>

### Notes Create

Create a classic Salesforce Note attached to a parent record (Account, Contact,
Lead, Opportunity, Case, custom object, etc.). `Title` and `ParentId` are required.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "notes",
  "action": "create",
  "params": {
    "Title": "<str>",
    "Body": "<str>",
    "ParentId": "<str>",
    "IsPrivate": true,
    "OwnerId": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.notes.create(
    title="<str>",
    body="<str>",
    parent_id="<str>",
    is_private=True,
    owner_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "notes",
    "action": "create",
    "params": {
        "Title": "<str>",
        "Body": "<str>",
        "ParentId": "<str>",
        "IsPrivate": True,
        "OwnerId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `Title` | `string` | Yes | Note title, up to 80 characters. |
| `Body` | `string` | No | Note body content (up to ~32,000 characters). |
| `ParentId` | `string` | Yes | Id of the parent record this note is attached to (Account, Contact, Lead, Opportunity, Case, custom object, etc.). |
| `IsPrivate` | `boolean` | No | When true, the note is visible only to its owner and admins. |
| `OwnerId` | `string` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `success` | `boolean` |  |
| `errors` | `array<object>` |  |


</details>

### Notes Get

Get a single note by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "notes",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.notes.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "notes",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce Note ID (18-character ID starting with '002') |
| `fields` | `string` | No | Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
Example: "Id,Title,Body,ParentId,OwnerId"
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Title` | `string` |  |
| `attributes` | `object` |  |


</details>

### Notes Update

Update a note

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "notes",
  "action": "update",
  "params": {
    "Title": "<str>",
    "Body": "<str>",
    "IsPrivate": true,
    "OwnerId": "<str>",
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.notes.update(
    title="<str>",
    body="<str>",
    is_private=True,
    owner_id="<str>",
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "notes",
    "action": "update",
    "params": {
        "Title": "<str>",
        "Body": "<str>",
        "IsPrivate": True,
        "OwnerId": "<str>",
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `Title` | `string` | No | Note title, up to 80 characters. |
| `Body` | `string` | No | Note body content (up to ~32,000 characters). |
| `IsPrivate` | `boolean` | No | When true, the note is visible only to its owner and admins. |
| `OwnerId` | `string` | No |  |
| `id` | `string` | Yes |  |


### Notes Delete

Delete a note

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "notes",
  "action": "delete",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.notes.delete(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "notes",
    "action": "delete",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes |  |


### Notes API Search

Search for notes using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "notes",
  "action": "api_search",
  "params": {
    "q": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.notes.api_search(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "notes",
    "action": "api_search",
    "params": {
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOSL search query. Format: FIND \{searchTerm\} RETURNING Note(fields) [LIMIT n]
Examples:
- "FIND \{important\} IN ALL FIELDS RETURNING Note(Id,Title,ParentId)"
- "FIND \{action items\} IN NAME FIELDS RETURNING Note(Id,Title,Body) LIMIT 50"
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `searchRecords` | `array<object>` |  |


</details>

## Content Versions

### Content Versions List

Returns a list of content versions (file metadata) via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.
Note: ContentVersion does not support FIELDS(STANDARD), so specific fields must be listed.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "content_versions",
  "action": "list",
  "params": {
    "q": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.content_versions.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "content_versions",
    "action": "list",
    "params": {
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query for content versions. Default returns up to 200 records.
To change the limit, provide your own query with a LIMIT clause.
Example: "SELECT Id, Title, FileExtension, ContentSize FROM ContentVersion WHERE IsLatest = true LIMIT 50"
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Title` | `string` |  |
| `FileExtension` | `string` |  |
| `ContentSize` | `integer` |  |
| `ContentDocumentId` | `string` |  |
| `VersionNumber` | `string` |  |
| `IsLatest` | `boolean` |  |
| `attributes` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |

</details>

### Content Versions Get

Get a single content version's metadata by ID. Returns file metadata, not the file content.
Use the download action to retrieve the actual file binary.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "content_versions",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.content_versions.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "content_versions",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce ContentVersion ID (18-character ID starting with '068') |
| `fields` | `string` | No | Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
Example: "Id,Title,FileExtension,ContentSize,ContentDocumentId,IsLatest"
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Title` | `string` |  |
| `FileExtension` | `string` |  |
| `ContentSize` | `integer` |  |
| `ContentDocumentId` | `string` |  |
| `VersionNumber` | `string` |  |
| `IsLatest` | `boolean` |  |
| `attributes` | `object` |  |


</details>

### Content Versions Download

Downloads the binary file content of a content version.
First use the list or get action to retrieve the ContentVersion ID and file metadata (size, type, etc.),
then use this action to download the actual file content.
The response is the raw binary file data.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "content_versions",
  "action": "download",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
async for chunk in salesforce.content_versions.download(    id="<str>"):# Process each chunk (e.g., write to file)
    file.write(chunk)
```

> **Note**: Download operations return an async iterator of bytes chunks for memory-efficient streaming. Use `async for` to process chunks as they arrive.

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "content_versions",
    "action": "download",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce ContentVersion ID (18-character ID starting with '068').
Obtain this ID from the list or get action.
 |
| `range_header` | `string` | No | Optional Range header for partial downloads (e.g., 'bytes=0-99') |


## Attachments

### Attachments List

Returns a list of attachments (legacy) via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.
Note: Attachments are a legacy feature; consider using ContentVersion (Salesforce Files) for new implementations.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "attachments",
  "action": "list",
  "params": {
    "q": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.attachments.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "attachments",
    "action": "list",
    "params": {
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query for attachments. Default returns up to 200 records.
To change the limit, provide your own query with a LIMIT clause.
Example: "SELECT Id, Name, ContentType, BodyLength, ParentId FROM Attachment WHERE ParentId = '001xx...' LIMIT 50"
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Name` | `string` |  |
| `ContentType` | `string` |  |
| `BodyLength` | `integer` |  |
| `ParentId` | `string` |  |
| `attributes` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |

</details>

### Attachments Get

Get a single attachment's metadata by ID. Returns file metadata, not the file content.
Use the download action to retrieve the actual file binary.
Note: Attachments are a legacy feature; consider using ContentVersion for new implementations.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "attachments",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.attachments.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "attachments",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce Attachment ID (18-character ID starting with '00P') |
| `fields` | `string` | No | Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
Example: "Id,Name,ContentType,BodyLength,ParentId"
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Name` | `string` |  |
| `ContentType` | `string` |  |
| `BodyLength` | `integer` |  |
| `ParentId` | `string` |  |
| `attributes` | `object` |  |


</details>

### Attachments Download

Downloads the binary file content of an attachment (legacy).
First use the list or get action to retrieve the Attachment ID and file metadata,
then use this action to download the actual file content.
Note: Attachments are a legacy feature; consider using ContentVersion for new implementations.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "attachments",
  "action": "download",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
async for chunk in salesforce.attachments.download(    id="<str>"):# Process each chunk (e.g., write to file)
    file.write(chunk)
```

> **Note**: Download operations return an async iterator of bytes chunks for memory-efficient streaming. Use `async for` to process chunks as they arrive.

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "attachments",
    "action": "download",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce Attachment ID (18-character ID starting with '00P').
Obtain this ID from the list or get action.
 |
| `range_header` | `string` | No | Optional Range header for partial downloads (e.g., 'bytes=0-99') |


## Reports

### Reports List

Returns a list of reports available in the Salesforce org.
Each report includes metadata such as Id, Name, Format, Description, and URL.
This uses the Analytics REST API, not SOQL.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "reports",
  "action": "list"
}'
```

#### Python SDK

```python
await salesforce.reports.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "reports",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `null \| string` |  |
| `url` | `null \| string` |  |
| `describeUrl` | `null \| string` |  |
| `instancesUrl` | `null \| string` |  |


</details>

### Reports Get

Executes a report synchronously and returns the report data results.
Returns both metadata and the executed data including fact maps, aggregates, and detail rows.
First use the list action to find available reports, then use this action to run a report and get its data.
Note: Large reports may be truncated. For reports with more than 2,000 detail rows, consider using async report runs.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "reports",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.reports.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "reports",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce Report ID (18-character ID starting with '00O').
Obtain this ID from the list action.
 |
| `includeDetails` | `boolean` | No | Whether to include detail rows in the report results. Defaults to true.
Set to false to get only summary/aggregate data.
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `attributes` | `null \| object` |  |
| `reportMetadata` | `null \| object` |  |
| `reportExtendedMetadata` | `null \| object` |  |
| `factMap` | `null \| object` |  |
| `groupingsDown` | `null \| object` |  |
| `groupingsAcross` | `null \| object` |  |
| `hasDetailRows` | `null \| boolean` |  |
| `allData` | `null \| boolean` |  |


</details>

## Users

### Users List

Returns a list of users via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "users",
  "action": "list",
  "params": {
    "q": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.users.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "list",
    "params": {
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query for users. Default returns up to 200 records.
To change the limit, provide your own query with a LIMIT clause.

Examples:
  SELECT FIELDS(STANDARD) FROM User WHERE IsActive = true ORDER BY LastModifiedDate DESC LIMIT 50
  SELECT Id, Name, Email, Manager.Name, Profile.Name FROM User WHERE IsActive = true LIMIT 50
  SELECT Id, Name, Email, Department, UserRole.Name FROM User LIMIT 50

Use dot-path traversal (Manager.Name, Profile.Name, UserRole.Name) to resolve
relationship fields inline instead of returning raw IDs.
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Name` | `string` |  |
| `attributes` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |

</details>

### Users Create

Create a Salesforce User. Consumes a paid user-license seat. Requires the
"Manage Internal Users" permission on the running OAuth identity.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "users",
  "action": "create",
  "params": {
    "Username": "<str>",
    "FirstName": "<str>",
    "LastName": "<str>",
    "Email": "<str>",
    "Alias": "<str>",
    "ProfileId": "<str>",
    "UserRoleId": "<str>",
    "ManagerId": "<str>",
    "TimeZoneSidKey": "<str>",
    "LocaleSidKey": "<str>",
    "EmailEncodingKey": "<str>",
    "LanguageLocaleKey": "<str>",
    "IsActive": true,
    "Title": "<str>",
    "Department": "<str>",
    "Phone": "<str>",
    "MobilePhone": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.users.create(
    username="<str>",
    first_name="<str>",
    last_name="<str>",
    email="<str>",
    alias="<str>",
    profile_id="<str>",
    user_role_id="<str>",
    manager_id="<str>",
    time_zone_sid_key="<str>",
    locale_sid_key="<str>",
    email_encoding_key="<str>",
    language_locale_key="<str>",
    is_active=True,
    title="<str>",
    department="<str>",
    phone="<str>",
    mobile_phone="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "create",
    "params": {
        "Username": "<str>",
        "FirstName": "<str>",
        "LastName": "<str>",
        "Email": "<str>",
        "Alias": "<str>",
        "ProfileId": "<str>",
        "UserRoleId": "<str>",
        "ManagerId": "<str>",
        "TimeZoneSidKey": "<str>",
        "LocaleSidKey": "<str>",
        "EmailEncodingKey": "<str>",
        "LanguageLocaleKey": "<str>",
        "IsActive": True,
        "Title": "<str>",
        "Department": "<str>",
        "Phone": "<str>",
        "MobilePhone": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `Username` | `string` | Yes | Login name (email-format, must be unique across all Salesforce orgs). |
| `FirstName` | `string` | No |  |
| `LastName` | `string` | Yes |  |
| `Email` | `string` | Yes |  |
| `Alias` | `string` | Yes | 1-8 character alias. |
| `ProfileId` | `string` | Yes | Salesforce profile that determines the user's base permissions. |
| `UserRoleId` | `string` | No |  |
| `ManagerId` | `string` | No |  |
| `TimeZoneSidKey` | `string` | Yes | e.g., "America/Los_Angeles". |
| `LocaleSidKey` | `string` | Yes | e.g., "en_US". |
| `EmailEncodingKey` | `string` | Yes | e.g., "UTF-8". |
| `LanguageLocaleKey` | `string` | Yes | e.g., "en_US". |
| `IsActive` | `boolean` | No | Set to false to deactivate the user (Salesforce does not support delete). |
| `Title` | `string` | No |  |
| `Department` | `string` | No |  |
| `Phone` | `string` | No |  |
| `MobilePhone` | `string` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `success` | `boolean` |  |
| `errors` | `array<object>` |  |


</details>

### Users Get

Get a single user by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "users",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.users.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce User ID (18-character ID starting with '005') |
| `fields` | `string` | No | Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
Example: "Id,Name,Email,Username,IsActive,ProfileId,UserRoleId"
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Name` | `string` |  |
| `attributes` | `object` |  |


</details>

### Users Update

Update a Salesforce User. To deactivate a user (Salesforce does not allow
delete), send `\{ "IsActive": false \}`.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "users",
  "action": "update",
  "params": {
    "Username": "<str>",
    "FirstName": "<str>",
    "LastName": "<str>",
    "Email": "<str>",
    "Alias": "<str>",
    "ProfileId": "<str>",
    "UserRoleId": "<str>",
    "ManagerId": "<str>",
    "TimeZoneSidKey": "<str>",
    "LocaleSidKey": "<str>",
    "EmailEncodingKey": "<str>",
    "LanguageLocaleKey": "<str>",
    "IsActive": true,
    "Title": "<str>",
    "Department": "<str>",
    "Phone": "<str>",
    "MobilePhone": "<str>",
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.users.update(
    username="<str>",
    first_name="<str>",
    last_name="<str>",
    email="<str>",
    alias="<str>",
    profile_id="<str>",
    user_role_id="<str>",
    manager_id="<str>",
    time_zone_sid_key="<str>",
    locale_sid_key="<str>",
    email_encoding_key="<str>",
    language_locale_key="<str>",
    is_active=True,
    title="<str>",
    department="<str>",
    phone="<str>",
    mobile_phone="<str>",
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "update",
    "params": {
        "Username": "<str>",
        "FirstName": "<str>",
        "LastName": "<str>",
        "Email": "<str>",
        "Alias": "<str>",
        "ProfileId": "<str>",
        "UserRoleId": "<str>",
        "ManagerId": "<str>",
        "TimeZoneSidKey": "<str>",
        "LocaleSidKey": "<str>",
        "EmailEncodingKey": "<str>",
        "LanguageLocaleKey": "<str>",
        "IsActive": True,
        "Title": "<str>",
        "Department": "<str>",
        "Phone": "<str>",
        "MobilePhone": "<str>",
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `Username` | `string` | No | Login name (email-format, must be unique across all Salesforce orgs). |
| `FirstName` | `string` | No |  |
| `LastName` | `string` | No |  |
| `Email` | `string` | No |  |
| `Alias` | `string` | No | 1-8 character alias. |
| `ProfileId` | `string` | No | Salesforce profile that determines the user's base permissions. |
| `UserRoleId` | `string` | No |  |
| `ManagerId` | `string` | No |  |
| `TimeZoneSidKey` | `string` | No | e.g., "America/Los_Angeles". |
| `LocaleSidKey` | `string` | No | e.g., "en_US". |
| `EmailEncodingKey` | `string` | No | e.g., "UTF-8". |
| `LanguageLocaleKey` | `string` | No | e.g., "en_US". |
| `IsActive` | `boolean` | No | Set to false to deactivate the user (Salesforce does not support delete). |
| `Title` | `string` | No |  |
| `Department` | `string` | No |  |
| `Phone` | `string` | No |  |
| `MobilePhone` | `string` | No |  |
| `id` | `string` | Yes |  |


### Users Context Store Search

Search and filter users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "users",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "Id": "<str>"
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await salesforce.users.context_store_search(
    query={"filter": {"eq": {"Id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"Id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` | Unique identifier for the user record |
| `AccountId` | `string` | ID of the account associated with this user (for portal users) |
| `Alias` | `string` | Short name used to identify the user in list views and reports |
| `City` | `string` | City portion of the user's address |
| `CompanyName` | `string` | Name of the user's company |
| `ContactId` | `string` | ID of the contact associated with this user (for portal users) |
| `Country` | `string` | Country portion of the user's address |
| `CreatedById` | `string` | ID of the user who created this user record |
| `CreatedDate` | `string` | Date and time when the user was created |
| `Department` | `string` | Department within the organization |
| `Division` | `string` | Division within the organization |
| `Email` | `string` | Email address of the user |
| `EmployeeNumber` | `string` | Employee number or ID assigned by the organization |
| `FirstName` | `string` | First name of the user |
| `IsActive` | `boolean` | Whether the user is active and can log in |
| `LastLoginDate` | `string` | Date and time of the user's most recent login |
| `LastModifiedById` | `string` | ID of the user who last modified this user record |
| `LastModifiedDate` | `string` | Date and time when the user was last modified |
| `LastName` | `string` | Last name of the user |
| `ManagerId` | `string` | ID of the user's manager |
| `MobilePhone` | `string` | Mobile phone number of the user |
| `Name` | `string` | Full name of the user |
| `Phone` | `string` | Business phone number of the user |
| `PostalCode` | `string` | Postal code portion of the user's address |
| `ProfileId` | `string` | ID of the user's profile |
| `State` | `string` | State or province portion of the user's address |
| `Street` | `string` | Street address of the user |
| `Title` | `string` | Job title of the user |
| `UserRoleId` | `string` | ID of the user's role in the organization |
| `UserType` | `string` | Type of user license (e.g., Standard, PowerPartner) |
| `Username` | `string` | Username for logging into Salesforce (unique across all orgs) |
| `SystemModstamp` | `string` | System timestamp when the record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].Id` | `string` | Unique identifier for the user record |
| `data[].AccountId` | `string` | ID of the account associated with this user (for portal users) |
| `data[].Alias` | `string` | Short name used to identify the user in list views and reports |
| `data[].City` | `string` | City portion of the user's address |
| `data[].CompanyName` | `string` | Name of the user's company |
| `data[].ContactId` | `string` | ID of the contact associated with this user (for portal users) |
| `data[].Country` | `string` | Country portion of the user's address |
| `data[].CreatedById` | `string` | ID of the user who created this user record |
| `data[].CreatedDate` | `string` | Date and time when the user was created |
| `data[].Department` | `string` | Department within the organization |
| `data[].Division` | `string` | Division within the organization |
| `data[].Email` | `string` | Email address of the user |
| `data[].EmployeeNumber` | `string` | Employee number or ID assigned by the organization |
| `data[].FirstName` | `string` | First name of the user |
| `data[].IsActive` | `boolean` | Whether the user is active and can log in |
| `data[].LastLoginDate` | `string` | Date and time of the user's most recent login |
| `data[].LastModifiedById` | `string` | ID of the user who last modified this user record |
| `data[].LastModifiedDate` | `string` | Date and time when the user was last modified |
| `data[].LastName` | `string` | Last name of the user |
| `data[].ManagerId` | `string` | ID of the user's manager |
| `data[].MobilePhone` | `string` | Mobile phone number of the user |
| `data[].Name` | `string` | Full name of the user |
| `data[].Phone` | `string` | Business phone number of the user |
| `data[].PostalCode` | `string` | Postal code portion of the user's address |
| `data[].ProfileId` | `string` | ID of the user's profile |
| `data[].State` | `string` | State or province portion of the user's address |
| `data[].Street` | `string` | Street address of the user |
| `data[].Title` | `string` | Job title of the user |
| `data[].UserRoleId` | `string` | ID of the user's role in the organization |
| `data[].UserType` | `string` | Type of user license (e.g., Standard, PowerPartner) |
| `data[].Username` | `string` | Username for logging into Salesforce (unique across all orgs) |
| `data[].SystemModstamp` | `string` | System timestamp when the record was last modified |

</details>

## Opportunity Stages

### Opportunity Stages List

Returns a list of opportunity stages via SOQL query. Default returns all stages.
OpportunityStage defines the sales process stages that opportunities move through.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "opportunity_stages",
  "action": "list",
  "params": {
    "q": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.opportunity_stages.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "opportunity_stages",
    "action": "list",
    "params": {
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query for opportunity stages. Default returns all stages.

Examples:
  SELECT FIELDS(STANDARD) FROM OpportunityStage ORDER BY SortOrder ASC
  SELECT Id, MasterLabel, ApiName, DefaultProbability, IsClosed, IsWon, IsActive, ForecastCategoryName FROM OpportunityStage WHERE IsActive = true ORDER BY SortOrder ASC
  SELECT Id, MasterLabel, DefaultProbability, CreatedBy.Name FROM OpportunityStage ORDER BY SortOrder ASC

Use dot-path traversal (CreatedBy.Name, LastModifiedBy.Name) to resolve
relationship fields inline instead of returning raw IDs.
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `MasterLabel` | `string` |  |
| `attributes` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |

</details>

### Opportunity Stages Get

Get a single opportunity stage by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "opportunity_stages",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.opportunity_stages.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "opportunity_stages",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce OpportunityStage ID |
| `fields` | `string` | No | Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
Example: "Id,MasterLabel,ApiName,DefaultProbability,IsClosed,IsWon,IsActive"
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `MasterLabel` | `string` |  |
| `attributes` | `object` |  |


</details>

### Opportunity Stages Context Store Search

Search and filter opportunity stages records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "opportunity_stages",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "Id": "<str>"
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await salesforce.opportunity_stages.context_store_search(
    query={"filter": {"eq": {"Id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "opportunity_stages",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"Id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` | Unique identifier for the opportunity stage record |
| `ApiName` | `string` | API name of the stage used in code and integrations |
| `CreatedById` | `string` | ID of the user who created this stage |
| `CreatedDate` | `string` | Date and time when the stage was created |
| `DefaultProbability` | `number` | Default probability percentage for opportunities at this stage |
| `Description` | `string` | Description of the stage |
| `ForecastCategory` | `string` | Forecast category for opportunities at this stage |
| `ForecastCategoryName` | `string` | Display name of the forecast category |
| `IsActive` | `boolean` | Whether the stage is currently active and can be used |
| `IsClosed` | `boolean` | Whether opportunities at this stage are considered closed |
| `IsWon` | `boolean` | Whether opportunities at this stage are considered won |
| `LastModifiedById` | `string` | ID of the user who last modified this stage |
| `LastModifiedDate` | `string` | Date and time when the stage was last modified |
| `MasterLabel` | `string` | Display label for the stage |
| `SortOrder` | `integer` | Order in which the stage appears in the sales process |
| `SystemModstamp` | `string` | System timestamp when the record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].Id` | `string` | Unique identifier for the opportunity stage record |
| `data[].ApiName` | `string` | API name of the stage used in code and integrations |
| `data[].CreatedById` | `string` | ID of the user who created this stage |
| `data[].CreatedDate` | `string` | Date and time when the stage was created |
| `data[].DefaultProbability` | `number` | Default probability percentage for opportunities at this stage |
| `data[].Description` | `string` | Description of the stage |
| `data[].ForecastCategory` | `string` | Forecast category for opportunities at this stage |
| `data[].ForecastCategoryName` | `string` | Display name of the forecast category |
| `data[].IsActive` | `boolean` | Whether the stage is currently active and can be used |
| `data[].IsClosed` | `boolean` | Whether opportunities at this stage are considered closed |
| `data[].IsWon` | `boolean` | Whether opportunities at this stage are considered won |
| `data[].LastModifiedById` | `string` | ID of the user who last modified this stage |
| `data[].LastModifiedDate` | `string` | Date and time when the stage was last modified |
| `data[].MasterLabel` | `string` | Display label for the stage |
| `data[].SortOrder` | `integer` | Order in which the stage appears in the sales process |
| `data[].SystemModstamp` | `string` | System timestamp when the record was last modified |

</details>

## Query

### Query List

Execute a custom SOQL query and return results. Use this for querying any Salesforce object.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "query",
  "action": "list",
  "params": {
    "q": "<str>"
  }
}'
```

#### Python SDK

```python
await salesforce.query.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "query",
    "action": "list",
    "params": {
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query string. Include LIMIT clause to control the number of records returned.
Examples:
- "SELECT Id, Name FROM Account LIMIT 100"
- "SELECT FIELDS(STANDARD) FROM Contact WHERE AccountId = '001xx...' LIMIT 50"
- "SELECT Id, Subject, Status FROM Case WHERE CreatedDate = TODAY"
- "SELECT Id, Name, Account.Name, Owner.Name FROM Opportunity LIMIT 50"

Use dot-path traversal (e.g. Owner.Name, Account.Name) to resolve relationship
fields inline instead of returning raw IDs.
 |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |

</details>

