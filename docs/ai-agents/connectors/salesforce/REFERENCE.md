# Salesforce full reference

This is the full reference documentation for the Salesforce agent connector.

## Supported entities and actions

The Salesforce connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Accounts | [List](#accounts-list), [Get](#accounts-get), [API Search](#accounts-api-search), [Search](#accounts-search) |
| Contacts | [List](#contacts-list), [Get](#contacts-get), [API Search](#contacts-api-search), [Search](#contacts-search) |
| Leads | [List](#leads-list), [Get](#leads-get), [API Search](#leads-api-search), [Search](#leads-search) |
| Opportunities | [List](#opportunities-list), [Get](#opportunities-get), [API Search](#opportunities-api-search), [Search](#opportunities-search) |
| Tasks | [List](#tasks-list), [Get](#tasks-get), [API Search](#tasks-api-search), [Search](#tasks-search) |
| Events | [List](#events-list), [Get](#events-get), [API Search](#events-api-search) |
| Campaigns | [List](#campaigns-list), [Get](#campaigns-get), [API Search](#campaigns-api-search) |
| Cases | [List](#cases-list), [Get](#cases-get), [API Search](#cases-api-search) |
| Notes | [List](#notes-list), [Get](#notes-get), [API Search](#notes-api-search) |
| Content Versions | [List](#content-versions-list), [Get](#content-versions-get), [Download](#content-versions-download) |
| Attachments | [List](#attachments-list), [Get](#attachments-get), [Download](#attachments-download) |
| Query | [List](#query-list) |

## Accounts

### Accounts List

Returns a list of accounts via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


#### Python SDK

```python
await salesforce.accounts.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
Example: "SELECT FIELDS(STANDARD) FROM Account ORDER BY LastModifiedDate DESC LIMIT 50"
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

### Accounts Get

Get a single account by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


#### Python SDK

```python
await salesforce.accounts.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Accounts API Search

Search for accounts using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields and objects.
Use SOQL (list action) for structured queries with specific field conditions.


#### Python SDK

```python
await salesforce.accounts.api_search(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Accounts Search

Search and filter accounts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await salesforce.accounts.search(
    query={"filter": {"eq": {"Id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "search",
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
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
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
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.Id` | `string` | Unique identifier for the account record |
| `hits[].data.Name` | `string` | Name of the account or company |
| `hits[].data.AccountSource` | `string` | Source of the account record (e.g., Web, Referral) |
| `hits[].data.BillingAddress` | `object` | Complete billing address as a compound field |
| `hits[].data.BillingCity` | `string` | City portion of the billing address |
| `hits[].data.BillingCountry` | `string` | Country portion of the billing address |
| `hits[].data.BillingPostalCode` | `string` | Postal code portion of the billing address |
| `hits[].data.BillingState` | `string` | State or province portion of the billing address |
| `hits[].data.BillingStreet` | `string` | Street address portion of the billing address |
| `hits[].data.CreatedById` | `string` | ID of the user who created this account |
| `hits[].data.CreatedDate` | `string` | Date and time when the account was created |
| `hits[].data.Description` | `string` | Text description of the account |
| `hits[].data.Industry` | `string` | Primary business industry of the account |
| `hits[].data.IsDeleted` | `boolean` | Whether the account has been moved to the Recycle Bin |
| `hits[].data.LastActivityDate` | `string` | Date of the last activity associated with this account |
| `hits[].data.LastModifiedById` | `string` | ID of the user who last modified this account |
| `hits[].data.LastModifiedDate` | `string` | Date and time when the account was last modified |
| `hits[].data.NumberOfEmployees` | `integer` | Number of employees at the account |
| `hits[].data.OwnerId` | `string` | ID of the user who owns this account |
| `hits[].data.ParentId` | `string` | ID of the parent account, if this is a subsidiary |
| `hits[].data.Phone` | `string` | Primary phone number for the account |
| `hits[].data.ShippingAddress` | `object` | Complete shipping address as a compound field |
| `hits[].data.ShippingCity` | `string` | City portion of the shipping address |
| `hits[].data.ShippingCountry` | `string` | Country portion of the shipping address |
| `hits[].data.ShippingPostalCode` | `string` | Postal code portion of the shipping address |
| `hits[].data.ShippingState` | `string` | State or province portion of the shipping address |
| `hits[].data.ShippingStreet` | `string` | Street address portion of the shipping address |
| `hits[].data.Type` | `string` | Type of account (e.g., Customer, Partner, Competitor) |
| `hits[].data.Website` | `string` | Website URL for the account |
| `hits[].data.SystemModstamp` | `string` | System timestamp when the record was last modified |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Contacts

### Contacts List

Returns a list of contacts via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


#### Python SDK

```python
await salesforce.contacts.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
Example: "SELECT FIELDS(STANDARD) FROM Contact WHERE AccountId = '001xx...' LIMIT 50"
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

### Contacts Get

Get a single contact by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


#### Python SDK

```python
await salesforce.contacts.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Contacts API Search

Search for contacts using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields.


#### Python SDK

```python
await salesforce.contacts.api_search(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Contacts Search

Search and filter contacts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await salesforce.contacts.search(
    query={"filter": {"eq": {"Id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contacts",
    "action": "search",
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
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
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
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.Id` | `string` | Unique identifier for the contact record |
| `hits[].data.AccountId` | `string` | ID of the account this contact is associated with |
| `hits[].data.CreatedById` | `string` | ID of the user who created this contact |
| `hits[].data.CreatedDate` | `string` | Date and time when the contact was created |
| `hits[].data.Department` | `string` | Department within the account where the contact works |
| `hits[].data.Email` | `string` | Email address of the contact |
| `hits[].data.FirstName` | `string` | First name of the contact |
| `hits[].data.IsDeleted` | `boolean` | Whether the contact has been moved to the Recycle Bin |
| `hits[].data.LastActivityDate` | `string` | Date of the last activity associated with this contact |
| `hits[].data.LastModifiedById` | `string` | ID of the user who last modified this contact |
| `hits[].data.LastModifiedDate` | `string` | Date and time when the contact was last modified |
| `hits[].data.LastName` | `string` | Last name of the contact |
| `hits[].data.LeadSource` | `string` | Source from which this contact originated |
| `hits[].data.MailingAddress` | `object` | Complete mailing address as a compound field |
| `hits[].data.MailingCity` | `string` | City portion of the mailing address |
| `hits[].data.MailingCountry` | `string` | Country portion of the mailing address |
| `hits[].data.MailingPostalCode` | `string` | Postal code portion of the mailing address |
| `hits[].data.MailingState` | `string` | State or province portion of the mailing address |
| `hits[].data.MailingStreet` | `string` | Street address portion of the mailing address |
| `hits[].data.MobilePhone` | `string` | Mobile phone number of the contact |
| `hits[].data.Name` | `string` | Full name of the contact (read-only, concatenation of first and last name) |
| `hits[].data.OwnerId` | `string` | ID of the user who owns this contact |
| `hits[].data.Phone` | `string` | Business phone number of the contact |
| `hits[].data.ReportsToId` | `string` | ID of the contact this contact reports to |
| `hits[].data.Title` | `string` | Job title of the contact |
| `hits[].data.SystemModstamp` | `string` | System timestamp when the record was last modified |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Leads

### Leads List

Returns a list of leads via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


#### Python SDK

```python
await salesforce.leads.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
Example: "SELECT FIELDS(STANDARD) FROM Lead WHERE Status = 'Open' LIMIT 100"
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

### Leads Get

Get a single lead by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


#### Python SDK

```python
await salesforce.leads.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Leads API Search

Search for leads using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields.


#### Python SDK

```python
await salesforce.leads.api_search(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Leads Search

Search and filter leads records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await salesforce.leads.search(
    query={"filter": {"eq": {"Id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "leads",
    "action": "search",
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
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
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
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.Id` | `string` | Unique identifier for the lead record |
| `hits[].data.Address` | `object` | Complete address as a compound field |
| `hits[].data.City` | `string` | City portion of the address |
| `hits[].data.Company` | `string` | Company or organization the lead works for |
| `hits[].data.ConvertedAccountId` | `string` | ID of the account created when lead was converted |
| `hits[].data.ConvertedContactId` | `string` | ID of the contact created when lead was converted |
| `hits[].data.ConvertedDate` | `string` | Date when the lead was converted |
| `hits[].data.ConvertedOpportunityId` | `string` | ID of the opportunity created when lead was converted |
| `hits[].data.Country` | `string` | Country portion of the address |
| `hits[].data.CreatedById` | `string` | ID of the user who created this lead |
| `hits[].data.CreatedDate` | `string` | Date and time when the lead was created |
| `hits[].data.Email` | `string` | Email address of the lead |
| `hits[].data.FirstName` | `string` | First name of the lead |
| `hits[].data.Industry` | `string` | Industry the lead's company operates in |
| `hits[].data.IsConverted` | `boolean` | Whether the lead has been converted to an account, contact, and opportunity |
| `hits[].data.IsDeleted` | `boolean` | Whether the lead has been moved to the Recycle Bin |
| `hits[].data.LastActivityDate` | `string` | Date of the last activity associated with this lead |
| `hits[].data.LastModifiedById` | `string` | ID of the user who last modified this lead |
| `hits[].data.LastModifiedDate` | `string` | Date and time when the lead was last modified |
| `hits[].data.LastName` | `string` | Last name of the lead |
| `hits[].data.LeadSource` | `string` | Source from which this lead originated |
| `hits[].data.MobilePhone` | `string` | Mobile phone number of the lead |
| `hits[].data.Name` | `string` | Full name of the lead (read-only, concatenation of first and last name) |
| `hits[].data.NumberOfEmployees` | `integer` | Number of employees at the lead's company |
| `hits[].data.OwnerId` | `string` | ID of the user who owns this lead |
| `hits[].data.Phone` | `string` | Phone number of the lead |
| `hits[].data.PostalCode` | `string` | Postal code portion of the address |
| `hits[].data.Rating` | `string` | Rating of the lead (e.g., Hot, Warm, Cold) |
| `hits[].data.State` | `string` | State or province portion of the address |
| `hits[].data.Status` | `string` | Current status of the lead in the sales process |
| `hits[].data.Street` | `string` | Street address portion of the address |
| `hits[].data.Title` | `string` | Job title of the lead |
| `hits[].data.Website` | `string` | Website URL for the lead's company |
| `hits[].data.SystemModstamp` | `string` | System timestamp when the record was last modified |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Opportunities

### Opportunities List

Returns a list of opportunities via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


#### Python SDK

```python
await salesforce.opportunities.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
Example: "SELECT FIELDS(STANDARD) FROM Opportunity WHERE StageName = 'Closed Won' LIMIT 50"
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

### Opportunities Get

Get a single opportunity by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


#### Python SDK

```python
await salesforce.opportunities.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Opportunities API Search

Search for opportunities using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields.


#### Python SDK

```python
await salesforce.opportunities.api_search(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Opportunities Search

Search and filter opportunities records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await salesforce.opportunities.search(
    query={"filter": {"eq": {"Id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "opportunities",
    "action": "search",
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
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
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
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.Id` | `string` | Unique identifier for the opportunity record |
| `hits[].data.AccountId` | `string` | ID of the account associated with this opportunity |
| `hits[].data.Amount` | `number` | Estimated total sale amount |
| `hits[].data.CampaignId` | `string` | ID of the campaign that generated this opportunity |
| `hits[].data.CloseDate` | `string` | Expected close date for the opportunity |
| `hits[].data.ContactId` | `string` | ID of the primary contact for this opportunity |
| `hits[].data.CreatedById` | `string` | ID of the user who created this opportunity |
| `hits[].data.CreatedDate` | `string` | Date and time when the opportunity was created |
| `hits[].data.Description` | `string` | Text description of the opportunity |
| `hits[].data.ExpectedRevenue` | `number` | Expected revenue based on amount and probability |
| `hits[].data.ForecastCategory` | `string` | Forecast category for this opportunity |
| `hits[].data.ForecastCategoryName` | `string` | Name of the forecast category |
| `hits[].data.IsClosed` | `boolean` | Whether the opportunity is closed |
| `hits[].data.IsDeleted` | `boolean` | Whether the opportunity has been moved to the Recycle Bin |
| `hits[].data.IsWon` | `boolean` | Whether the opportunity was won |
| `hits[].data.LastActivityDate` | `string` | Date of the last activity associated with this opportunity |
| `hits[].data.LastModifiedById` | `string` | ID of the user who last modified this opportunity |
| `hits[].data.LastModifiedDate` | `string` | Date and time when the opportunity was last modified |
| `hits[].data.LeadSource` | `string` | Source from which this opportunity originated |
| `hits[].data.Name` | `string` | Name of the opportunity |
| `hits[].data.NextStep` | `string` | Description of the next step in closing the opportunity |
| `hits[].data.OwnerId` | `string` | ID of the user who owns this opportunity |
| `hits[].data.Probability` | `number` | Likelihood of closing the opportunity (percentage) |
| `hits[].data.StageName` | `string` | Current stage of the opportunity in the sales process |
| `hits[].data.Type` | `string` | Type of opportunity (e.g., New Business, Existing Business) |
| `hits[].data.SystemModstamp` | `string` | System timestamp when the record was last modified |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Tasks

### Tasks List

Returns a list of tasks via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


#### Python SDK

```python
await salesforce.tasks.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
Example: "SELECT FIELDS(STANDARD) FROM Task WHERE Status = 'Not Started' LIMIT 100"
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

### Tasks Get

Get a single task by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


#### Python SDK

```python
await salesforce.tasks.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Tasks API Search

Search for tasks using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields.


#### Python SDK

```python
await salesforce.tasks.api_search(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Tasks Search

Search and filter tasks records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await salesforce.tasks.search(
    query={"filter": {"eq": {"Id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "search",
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
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
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
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.Id` | `string` | Unique identifier for the task record |
| `hits[].data.AccountId` | `string` | ID of the account associated with this task |
| `hits[].data.ActivityDate` | `string` | Due date for the task |
| `hits[].data.CallDisposition` | `string` | Result of the call, if this task represents a call |
| `hits[].data.CallDurationInSeconds` | `integer` | Duration of the call in seconds |
| `hits[].data.CallType` | `string` | Type of call (Inbound, Outbound, Internal) |
| `hits[].data.CompletedDateTime` | `string` | Date and time when the task was completed |
| `hits[].data.CreatedById` | `string` | ID of the user who created this task |
| `hits[].data.CreatedDate` | `string` | Date and time when the task was created |
| `hits[].data.Description` | `string` | Text description or notes about the task |
| `hits[].data.IsClosed` | `boolean` | Whether the task has been completed |
| `hits[].data.IsDeleted` | `boolean` | Whether the task has been moved to the Recycle Bin |
| `hits[].data.IsHighPriority` | `boolean` | Whether the task is marked as high priority |
| `hits[].data.LastModifiedById` | `string` | ID of the user who last modified this task |
| `hits[].data.LastModifiedDate` | `string` | Date and time when the task was last modified |
| `hits[].data.OwnerId` | `string` | ID of the user who owns this task |
| `hits[].data.Priority` | `string` | Priority level of the task (High, Normal, Low) |
| `hits[].data.Status` | `string` | Current status of the task |
| `hits[].data.Subject` | `string` | Subject or title of the task |
| `hits[].data.TaskSubtype` | `string` | Subtype of the task (e.g., Call, Email, Task) |
| `hits[].data.Type` | `string` | Type of task |
| `hits[].data.WhatId` | `string` | ID of the related object (Account, Opportunity, etc.) |
| `hits[].data.WhoId` | `string` | ID of the related person (Contact or Lead) |
| `hits[].data.SystemModstamp` | `string` | System timestamp when the record was last modified |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Events

### Events List

Returns a list of events via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


#### Python SDK

```python
await salesforce.events.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
Example: "SELECT FIELDS(STANDARD) FROM Event WHERE StartDateTime > TODAY LIMIT 50"
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

### Events Get

Get a single event by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


#### Python SDK

```python
await salesforce.events.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Events API Search

Search for events using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields.


#### Python SDK

```python
await salesforce.events.api_search(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Python SDK

```python
await salesforce.campaigns.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
Example: "SELECT FIELDS(STANDARD) FROM Campaign WHERE IsActive = true LIMIT 50"
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

### Campaigns Get

Get a single campaign by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


#### Python SDK

```python
await salesforce.campaigns.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Campaigns API Search

Search for campaigns using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields.


#### Python SDK

```python
await salesforce.campaigns.api_search(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Python SDK

```python
await salesforce.cases.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
Example: "SELECT FIELDS(STANDARD) FROM Case WHERE Status = 'New' LIMIT 100"
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

### Cases Get

Get a single case by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


#### Python SDK

```python
await salesforce.cases.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Cases API Search

Search for cases using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields.


#### Python SDK

```python
await salesforce.cases.api_search(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Python SDK

```python
await salesforce.notes.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
Example: "SELECT FIELDS(STANDARD) FROM Note WHERE ParentId = '001xx...' LIMIT 50"
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

### Notes Get

Get a single note by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


#### Python SDK

```python
await salesforce.notes.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Notes API Search

Search for notes using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields.


#### Python SDK

```python
await salesforce.notes.api_search(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Python SDK

```python
await salesforce.content_versions.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Python SDK

```python
await salesforce.content_versions.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Python SDK

```python
async for chunk in salesforce.content_versions.download(    id="<str>"):# Process each chunk (e.g., write to file)
    file.write(chunk)
```

> **Note**: Download operations return an async iterator of bytes chunks for memory-efficient streaming. Use `async for` to process chunks as they arrive.

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Python SDK

```python
await salesforce.attachments.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Python SDK

```python
await salesforce.attachments.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Python SDK

```python
async for chunk in salesforce.attachments.download(    id="<str>"):# Process each chunk (e.g., write to file)
    file.write(chunk)
```

> **Note**: Download operations return an async iterator of bytes chunks for memory-efficient streaming. Use `async for` to process chunks as they arrive.

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


## Query

### Query List

Execute a custom SOQL query and return results. Use this for querying any Salesforce object.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


#### Python SDK

```python
await salesforce.query.list(
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
 |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |

</details>

