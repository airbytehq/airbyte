# Zoho-Crm full reference

This is the full reference documentation for the Zoho-Crm agent connector.

## Supported entities and actions

The Zoho-Crm connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Leads | [List](#leads-list), [Create](#leads-create), [Get](#leads-get), [Update](#leads-update), [Context Store Search](#leads-context-store-search) |
| Contacts | [List](#contacts-list), [Create](#contacts-create), [Get](#contacts-get), [Update](#contacts-update), [Context Store Search](#contacts-context-store-search) |
| Accounts | [List](#accounts-list), [Create](#accounts-create), [Get](#accounts-get), [Update](#accounts-update), [Context Store Search](#accounts-context-store-search) |
| Deals | [List](#deals-list), [Create](#deals-create), [Get](#deals-get), [Update](#deals-update), [Context Store Search](#deals-context-store-search) |
| Campaigns | [List](#campaigns-list), [Get](#campaigns-get), [Context Store Search](#campaigns-context-store-search) |
| Tasks | [List](#tasks-list), [Create](#tasks-create), [Get](#tasks-get), [Update](#tasks-update), [Context Store Search](#tasks-context-store-search) |
| Events | [List](#events-list), [Get](#events-get), [Context Store Search](#events-context-store-search) |
| Calls | [List](#calls-list), [Get](#calls-get), [Context Store Search](#calls-context-store-search) |
| Products | [List](#products-list), [Get](#products-get), [Context Store Search](#products-context-store-search) |
| Quotes | [List](#quotes-list), [Get](#quotes-get), [Context Store Search](#quotes-context-store-search) |
| Invoices | [List](#invoices-list), [Get](#invoices-get), [Context Store Search](#invoices-context-store-search) |

## Leads

### Leads List

Returns a paginated list of leads

#### Python SDK

```python
await zoho_crm.leads.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "leads",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number |
| `per_page` | `integer` | No | Number of records per page |
| `page_token` | `string` | No | Page token for fetching beyond 2000 records |
| `sort_by` | `string` | No | Field to sort by |
| `sort_order` | `"asc" \| "desc"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `Owner` | `object \| any` |  |
| `Company` | `null \| string` |  |
| `First_Name` | `null \| string` |  |
| `Last_Name` | `null \| string` |  |
| `Full_Name` | `null \| string` |  |
| `Email` | `null \| string` |  |
| `Phone` | `null \| string` |  |
| `Mobile` | `null \| string` |  |
| `Fax` | `null \| string` |  |
| `Title` | `null \| string` |  |
| `Lead_Source` | `null \| string` |  |
| `Industry` | `null \| string` |  |
| `Annual_Revenue` | `null \| number` |  |
| `No_of_Employees` | `null \| integer` |  |
| `Rating` | `null \| string` |  |
| `Lead_Status` | `null \| string` |  |
| `Website` | `null \| string` |  |
| `Street` | `null \| string` |  |
| `City` | `null \| string` |  |
| `State` | `null \| string` |  |
| `Zip_Code` | `null \| string` |  |
| `Country` | `null \| string` |  |
| `Description` | `null \| string` |  |
| `Converted_Detail` | `null \| object` |  |
| `Created_Time` | `null \| string` |  |
| `Modified_Time` | `null \| string` |  |
| `Created_By` | `object \| any` |  |
| `Modified_By` | `object \| any` |  |
| `Record_Status__s` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `more_records` | `boolean` |  |
| `page` | `integer` |  |

</details>

### Leads Create

Creates a new lead record in Zoho CRM

#### Python SDK

```python
await zoho_crm.leads.create(
    data=[]
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
        "data": []
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data` | `array<object>` | Yes | Array containing the lead record to create |
| `data.First_Name` | `string` | No | Lead's first name |
| `data.Last_Name` | `string` | Yes | Lead's last name (required) |
| `data.Email` | `string` | No | Lead's email address |
| `data.Phone` | `string` | No | Lead's phone number |
| `data.Mobile` | `string` | No | Lead's mobile number |
| `data.Company` | `string` | No | Company the lead is associated with |
| `data.Title` | `string` | No | Lead's job title |
| `data.Lead_Source` | `string` | No | Source from which the lead was generated |
| `data.Industry` | `string` | No | Industry the lead belongs to |
| `data.Annual_Revenue` | `number` | No | Annual revenue of the lead's company |
| `data.No_of_Employees` | `integer` | No | Number of employees in the lead's company |
| `data.Rating` | `string` | No | Lead rating |
| `data.Lead_Status` | `string` | No | Current status of the lead |
| `data.Website` | `string` | No | Lead's website URL |
| `data.Street` | `string` | No | Street address |
| `data.City` | `string` | No | City |
| `data.State` | `string` | No | State or province |
| `data.Zip_Code` | `string` | No | ZIP/postal code |
| `data.Country` | `string` | No | Country |
| `data.Description` | `string` | No | Description or notes about the lead |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array<object>` |  |
| `data[].code` | `string` |  |
| `data[].details` | `object` |  |
| `data[].details.Modified_Time` | `null \| string` |  |
| `data[].details.Modified_By` | `object \| any` |  |
| `data[].details.Created_Time` | `null \| string` |  |
| `data[].details.id` | `string` |  |
| `data[].details.Created_By` | `object \| any` |  |
| `data[].message` | `string` |  |
| `data[].status` | `string` |  |


</details>

### Leads Get

Get a single lead by ID

#### Python SDK

```python
await zoho_crm.leads.get(
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
| `id` | `string` | Yes | Lead ID |


### Leads Update

Updates an existing lead record in Zoho CRM

#### Python SDK

```python
await zoho_crm.leads.update(
    data=[],
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
        "data": [],
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data` | `array<object>` | Yes | Array containing the lead fields to update |
| `data.First_Name` | `string` | No | Lead's first name |
| `data.Last_Name` | `string` | No | Lead's last name |
| `data.Email` | `string` | No | Lead's email address |
| `data.Phone` | `string` | No | Lead's phone number |
| `data.Mobile` | `string` | No | Lead's mobile number |
| `data.Company` | `string` | No | Company the lead is associated with |
| `data.Title` | `string` | No | Lead's job title |
| `data.Lead_Source` | `string` | No | Source from which the lead was generated |
| `data.Industry` | `string` | No | Industry the lead belongs to |
| `data.Annual_Revenue` | `number` | No | Annual revenue of the lead's company |
| `data.No_of_Employees` | `integer` | No | Number of employees in the lead's company |
| `data.Rating` | `string` | No | Lead rating |
| `data.Lead_Status` | `string` | No | Current status of the lead |
| `data.Website` | `string` | No | Lead's website URL |
| `data.Street` | `string` | No | Street address |
| `data.City` | `string` | No | City |
| `data.State` | `string` | No | State or province |
| `data.Zip_Code` | `string` | No | ZIP/postal code |
| `data.Country` | `string` | No | Country |
| `data.Description` | `string` | No | Description or notes about the lead |
| `id` | `string` | Yes | Lead ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array<object>` |  |
| `data[].code` | `string` |  |
| `data[].details` | `object` |  |
| `data[].details.Modified_Time` | `null \| string` |  |
| `data[].details.Modified_By` | `object \| any` |  |
| `data[].details.Created_Time` | `null \| string` |  |
| `data[].details.id` | `string` |  |
| `data[].details.Created_By` | `object \| any` |  |
| `data[].message` | `string` |  |
| `data[].status` | `string` |  |


</details>

### Leads Context Store Search

Search and filter leads records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zoho_crm.leads.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
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
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `id` | `string` | Unique record identifier |
| `First_Name` | `string` | Lead's first name |
| `Last_Name` | `string` | Lead's last name |
| `Full_Name` | `string` | Lead's full name |
| `Email` | `string` | Lead's email address |
| `Phone` | `string` | Lead's phone number |
| `Mobile` | `string` | Lead's mobile number |
| `Company` | `string` | Company the lead is associated with |
| `Title` | `string` | Lead's job title |
| `Lead_Source` | `string` | Source from which the lead was generated |
| `Industry` | `string` | Industry the lead belongs to |
| `Annual_Revenue` | `number` | Annual revenue of the lead's company |
| `No_of_Employees` | `integer` | Number of employees in the lead's company |
| `Rating` | `string` | Lead rating |
| `Lead_Status` | `string` | Current status of the lead |
| `Website` | `string` | Lead's website URL |
| `City` | `string` | Lead's city |
| `State` | `string` | Lead's state or province |
| `Country` | `string` | Lead's country |
| `Description` | `string` | Description or notes about the lead |
| `Created_Time` | `string` | Time the record was created |
| `Modified_Time` | `string` | Time the record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique record identifier |
| `data[].First_Name` | `string` | Lead's first name |
| `data[].Last_Name` | `string` | Lead's last name |
| `data[].Full_Name` | `string` | Lead's full name |
| `data[].Email` | `string` | Lead's email address |
| `data[].Phone` | `string` | Lead's phone number |
| `data[].Mobile` | `string` | Lead's mobile number |
| `data[].Company` | `string` | Company the lead is associated with |
| `data[].Title` | `string` | Lead's job title |
| `data[].Lead_Source` | `string` | Source from which the lead was generated |
| `data[].Industry` | `string` | Industry the lead belongs to |
| `data[].Annual_Revenue` | `number` | Annual revenue of the lead's company |
| `data[].No_of_Employees` | `integer` | Number of employees in the lead's company |
| `data[].Rating` | `string` | Lead rating |
| `data[].Lead_Status` | `string` | Current status of the lead |
| `data[].Website` | `string` | Lead's website URL |
| `data[].City` | `string` | Lead's city |
| `data[].State` | `string` | Lead's state or province |
| `data[].Country` | `string` | Lead's country |
| `data[].Description` | `string` | Description or notes about the lead |
| `data[].Created_Time` | `string` | Time the record was created |
| `data[].Modified_Time` | `string` | Time the record was last modified |

</details>

## Contacts

### Contacts List

Returns a paginated list of contacts

#### Python SDK

```python
await zoho_crm.contacts.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contacts",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number |
| `per_page` | `integer` | No | Number of records per page |
| `page_token` | `string` | No | Page token for fetching beyond 2000 records |
| `sort_by` | `string` | No | Field to sort by |
| `sort_order` | `"asc" \| "desc"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `Owner` | `object \| any` |  |
| `First_Name` | `null \| string` |  |
| `Last_Name` | `null \| string` |  |
| `Full_Name` | `null \| string` |  |
| `Email` | `null \| string` |  |
| `Phone` | `null \| string` |  |
| `Mobile` | `null \| string` |  |
| `Fax` | `null \| string` |  |
| `Title` | `null \| string` |  |
| `Department` | `null \| string` |  |
| `Account_Name` | `object \| any` |  |
| `Lead_Source` | `null \| string` |  |
| `Date_of_Birth` | `null \| string` |  |
| `Mailing_Street` | `null \| string` |  |
| `Mailing_City` | `null \| string` |  |
| `Mailing_State` | `null \| string` |  |
| `Mailing_Zip` | `null \| string` |  |
| `Mailing_Country` | `null \| string` |  |
| `Other_Street` | `null \| string` |  |
| `Other_City` | `null \| string` |  |
| `Other_State` | `null \| string` |  |
| `Other_Zip` | `null \| string` |  |
| `Other_Country` | `null \| string` |  |
| `Description` | `null \| string` |  |
| `Created_Time` | `null \| string` |  |
| `Modified_Time` | `null \| string` |  |
| `Created_By` | `object \| any` |  |
| `Modified_By` | `object \| any` |  |
| `Record_Status__s` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `more_records` | `boolean` |  |
| `page` | `integer` |  |

</details>

### Contacts Create

Creates a new contact record in Zoho CRM

#### Python SDK

```python
await zoho_crm.contacts.create(
    data=[]
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
        "data": []
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data` | `array<object>` | Yes | Array containing the contact record to create |
| `data.First_Name` | `string` | No | Contact's first name |
| `data.Last_Name` | `string` | Yes | Contact's last name (required) |
| `data.Email` | `string` | No | Contact's email address |
| `data.Phone` | `string` | No | Contact's phone number |
| `data.Mobile` | `string` | No | Contact's mobile number |
| `data.Title` | `string` | No | Contact's job title |
| `data.Department` | `string` | No | Department the contact belongs to |
| `data.Lead_Source` | `string` | No | Source from which the contact was generated |
| `data.Date_of_Birth` | `string` | No | Contact's date of birth (YYYY-MM-DD) |
| `data.Mailing_Street` | `string` | No | Mailing street address |
| `data.Mailing_City` | `string` | No | Mailing city |
| `data.Mailing_State` | `string` | No | Mailing state or province |
| `data.Mailing_Zip` | `string` | No | Mailing ZIP/postal code |
| `data.Mailing_Country` | `string` | No | Mailing country |
| `data.Description` | `string` | No | Description or notes about the contact |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array<object>` |  |
| `data[].code` | `string` |  |
| `data[].details` | `object` |  |
| `data[].details.Modified_Time` | `null \| string` |  |
| `data[].details.Modified_By` | `object \| any` |  |
| `data[].details.Created_Time` | `null \| string` |  |
| `data[].details.id` | `string` |  |
| `data[].details.Created_By` | `object \| any` |  |
| `data[].message` | `string` |  |
| `data[].status` | `string` |  |


</details>

### Contacts Get

Get a single contact by ID

#### Python SDK

```python
await zoho_crm.contacts.get(
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
| `id` | `string` | Yes | Contact ID |


### Contacts Update

Updates an existing contact record in Zoho CRM

#### Python SDK

```python
await zoho_crm.contacts.update(
    data=[],
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
        "data": [],
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data` | `array<object>` | Yes | Array containing the contact fields to update |
| `data.First_Name` | `string` | No | Contact's first name |
| `data.Last_Name` | `string` | No | Contact's last name |
| `data.Email` | `string` | No | Contact's email address |
| `data.Phone` | `string` | No | Contact's phone number |
| `data.Mobile` | `string` | No | Contact's mobile number |
| `data.Title` | `string` | No | Contact's job title |
| `data.Department` | `string` | No | Department the contact belongs to |
| `data.Lead_Source` | `string` | No | Source from which the contact was generated |
| `data.Date_of_Birth` | `string` | No | Contact's date of birth (YYYY-MM-DD) |
| `data.Mailing_Street` | `string` | No | Mailing street address |
| `data.Mailing_City` | `string` | No | Mailing city |
| `data.Mailing_State` | `string` | No | Mailing state or province |
| `data.Mailing_Zip` | `string` | No | Mailing ZIP/postal code |
| `data.Mailing_Country` | `string` | No | Mailing country |
| `data.Description` | `string` | No | Description or notes about the contact |
| `id` | `string` | Yes | Contact ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array<object>` |  |
| `data[].code` | `string` |  |
| `data[].details` | `object` |  |
| `data[].details.Modified_Time` | `null \| string` |  |
| `data[].details.Modified_By` | `object \| any` |  |
| `data[].details.Created_Time` | `null \| string` |  |
| `data[].details.id` | `string` |  |
| `data[].details.Created_By` | `object \| any` |  |
| `data[].message` | `string` |  |
| `data[].status` | `string` |  |


</details>

### Contacts Context Store Search

Search and filter contacts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zoho_crm.contacts.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
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
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `id` | `string` | Unique record identifier |
| `First_Name` | `string` | Contact's first name |
| `Last_Name` | `string` | Contact's last name |
| `Full_Name` | `string` | Contact's full name |
| `Email` | `string` | Contact's email address |
| `Phone` | `string` | Contact's phone number |
| `Mobile` | `string` | Contact's mobile number |
| `Title` | `string` | Contact's job title |
| `Department` | `string` | Department the contact belongs to |
| `Lead_Source` | `string` | Source from which the contact was generated |
| `Date_of_Birth` | `string` | Contact's date of birth |
| `Mailing_City` | `string` | Mailing address city |
| `Mailing_State` | `string` | Mailing address state or province |
| `Mailing_Country` | `string` | Mailing address country |
| `Description` | `string` | Description or notes about the contact |
| `Created_Time` | `string` | Time the record was created |
| `Modified_Time` | `string` | Time the record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique record identifier |
| `data[].First_Name` | `string` | Contact's first name |
| `data[].Last_Name` | `string` | Contact's last name |
| `data[].Full_Name` | `string` | Contact's full name |
| `data[].Email` | `string` | Contact's email address |
| `data[].Phone` | `string` | Contact's phone number |
| `data[].Mobile` | `string` | Contact's mobile number |
| `data[].Title` | `string` | Contact's job title |
| `data[].Department` | `string` | Department the contact belongs to |
| `data[].Lead_Source` | `string` | Source from which the contact was generated |
| `data[].Date_of_Birth` | `string` | Contact's date of birth |
| `data[].Mailing_City` | `string` | Mailing address city |
| `data[].Mailing_State` | `string` | Mailing address state or province |
| `data[].Mailing_Country` | `string` | Mailing address country |
| `data[].Description` | `string` | Description or notes about the contact |
| `data[].Created_Time` | `string` | Time the record was created |
| `data[].Modified_Time` | `string` | Time the record was last modified |

</details>

## Accounts

### Accounts List

Returns a paginated list of accounts

#### Python SDK

```python
await zoho_crm.accounts.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number |
| `per_page` | `integer` | No | Number of records per page |
| `page_token` | `string` | No | Page token for fetching beyond 2000 records |
| `sort_by` | `string` | No | Field to sort by |
| `sort_order` | `"asc" \| "desc"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `Owner` | `object \| any` |  |
| `Account_Name` | `null \| string` |  |
| `Account_Number` | `null \| string` |  |
| `Account_Type` | `null \| string` |  |
| `Industry` | `null \| string` |  |
| `Annual_Revenue` | `null \| number` |  |
| `Employees` | `null \| integer` |  |
| `Phone` | `null \| string` |  |
| `Fax` | `null \| string` |  |
| `Website` | `null \| string` |  |
| `Ownership` | `null \| string` |  |
| `Rating` | `null \| string` |  |
| `SIC_Code` | `null \| integer` |  |
| `Ticker_Symbol` | `null \| string` |  |
| `Parent_Account` | `object \| any` |  |
| `Billing_Street` | `null \| string` |  |
| `Billing_City` | `null \| string` |  |
| `Billing_State` | `null \| string` |  |
| `Billing_Code` | `null \| string` |  |
| `Billing_Country` | `null \| string` |  |
| `Shipping_Street` | `null \| string` |  |
| `Shipping_City` | `null \| string` |  |
| `Shipping_State` | `null \| string` |  |
| `Shipping_Code` | `null \| string` |  |
| `Shipping_Country` | `null \| string` |  |
| `Description` | `null \| string` |  |
| `Created_Time` | `null \| string` |  |
| `Modified_Time` | `null \| string` |  |
| `Created_By` | `object \| any` |  |
| `Modified_By` | `object \| any` |  |
| `Record_Status__s` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `more_records` | `boolean` |  |
| `page` | `integer` |  |

</details>

### Accounts Create

Creates a new account record in Zoho CRM

#### Python SDK

```python
await zoho_crm.accounts.create(
    data=[]
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
        "data": []
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data` | `array<object>` | Yes | Array containing the account record to create |
| `data.Account_Name` | `string` | Yes | Account/company name (required) |
| `data.Account_Number` | `string` | No | Account number |
| `data.Account_Type` | `string` | No | Type of account (e.g., Analyst, Competitor, Customer) |
| `data.Industry` | `string` | No | Industry the account belongs to |
| `data.Annual_Revenue` | `number` | No | Annual revenue of the account |
| `data.Employees` | `integer` | No | Number of employees |
| `data.Phone` | `string` | No | Account phone number |
| `data.Website` | `string` | No | Account website URL |
| `data.Ownership` | `string` | No | Ownership type (e.g., Public, Private) |
| `data.Rating` | `string` | No | Account rating |
| `data.Billing_Street` | `string` | No | Billing street address |
| `data.Billing_City` | `string` | No | Billing city |
| `data.Billing_State` | `string` | No | Billing state or province |
| `data.Billing_Code` | `string` | No | Billing ZIP/postal code |
| `data.Billing_Country` | `string` | No | Billing country |
| `data.Shipping_Street` | `string` | No | Shipping street address |
| `data.Shipping_City` | `string` | No | Shipping city |
| `data.Shipping_State` | `string` | No | Shipping state or province |
| `data.Shipping_Code` | `string` | No | Shipping ZIP/postal code |
| `data.Shipping_Country` | `string` | No | Shipping country |
| `data.Description` | `string` | No | Description or notes about the account |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array<object>` |  |
| `data[].code` | `string` |  |
| `data[].details` | `object` |  |
| `data[].details.Modified_Time` | `null \| string` |  |
| `data[].details.Modified_By` | `object \| any` |  |
| `data[].details.Created_Time` | `null \| string` |  |
| `data[].details.id` | `string` |  |
| `data[].details.Created_By` | `object \| any` |  |
| `data[].message` | `string` |  |
| `data[].status` | `string` |  |


</details>

### Accounts Get

Get a single account by ID

#### Python SDK

```python
await zoho_crm.accounts.get(
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
| `id` | `string` | Yes | Account ID |


### Accounts Update

Updates an existing account record in Zoho CRM

#### Python SDK

```python
await zoho_crm.accounts.update(
    data=[],
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
        "data": [],
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data` | `array<object>` | Yes | Array containing the account fields to update |
| `data.Account_Name` | `string` | No | Account/company name |
| `data.Account_Number` | `string` | No | Account number |
| `data.Account_Type` | `string` | No | Type of account (e.g., Analyst, Competitor, Customer) |
| `data.Industry` | `string` | No | Industry the account belongs to |
| `data.Annual_Revenue` | `number` | No | Annual revenue of the account |
| `data.Employees` | `integer` | No | Number of employees |
| `data.Phone` | `string` | No | Account phone number |
| `data.Website` | `string` | No | Account website URL |
| `data.Ownership` | `string` | No | Ownership type (e.g., Public, Private) |
| `data.Rating` | `string` | No | Account rating |
| `data.Billing_Street` | `string` | No | Billing street address |
| `data.Billing_City` | `string` | No | Billing city |
| `data.Billing_State` | `string` | No | Billing state or province |
| `data.Billing_Code` | `string` | No | Billing ZIP/postal code |
| `data.Billing_Country` | `string` | No | Billing country |
| `data.Shipping_Street` | `string` | No | Shipping street address |
| `data.Shipping_City` | `string` | No | Shipping city |
| `data.Shipping_State` | `string` | No | Shipping state or province |
| `data.Shipping_Code` | `string` | No | Shipping ZIP/postal code |
| `data.Shipping_Country` | `string` | No | Shipping country |
| `data.Description` | `string` | No | Description or notes about the account |
| `id` | `string` | Yes | Account ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array<object>` |  |
| `data[].code` | `string` |  |
| `data[].details` | `object` |  |
| `data[].details.Modified_Time` | `null \| string` |  |
| `data[].details.Modified_By` | `object \| any` |  |
| `data[].details.Created_Time` | `null \| string` |  |
| `data[].details.id` | `string` |  |
| `data[].details.Created_By` | `object \| any` |  |
| `data[].message` | `string` |  |
| `data[].status` | `string` |  |


</details>

### Accounts Context Store Search

Search and filter accounts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zoho_crm.accounts.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
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
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `id` | `string` | Unique record identifier |
| `Account_Name` | `string` | Name of the account or company |
| `Account_Number` | `string` | Account number |
| `Account_Type` | `string` | Type of account (e.g., Analyst, Competitor, Customer) |
| `Industry` | `string` | Industry the account belongs to |
| `Annual_Revenue` | `number` | Annual revenue of the account |
| `Employees` | `integer` | Number of employees |
| `Phone` | `string` | Account phone number |
| `Website` | `string` | Account website URL |
| `Ownership` | `string` | Ownership type (e.g., Public, Private) |
| `Rating` | `string` | Account rating |
| `Billing_City` | `string` | Billing address city |
| `Billing_State` | `string` | Billing address state or province |
| `Billing_Country` | `string` | Billing address country |
| `Description` | `string` | Description or notes about the account |
| `Created_Time` | `string` | Time the record was created |
| `Modified_Time` | `string` | Time the record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique record identifier |
| `data[].Account_Name` | `string` | Name of the account or company |
| `data[].Account_Number` | `string` | Account number |
| `data[].Account_Type` | `string` | Type of account (e.g., Analyst, Competitor, Customer) |
| `data[].Industry` | `string` | Industry the account belongs to |
| `data[].Annual_Revenue` | `number` | Annual revenue of the account |
| `data[].Employees` | `integer` | Number of employees |
| `data[].Phone` | `string` | Account phone number |
| `data[].Website` | `string` | Account website URL |
| `data[].Ownership` | `string` | Ownership type (e.g., Public, Private) |
| `data[].Rating` | `string` | Account rating |
| `data[].Billing_City` | `string` | Billing address city |
| `data[].Billing_State` | `string` | Billing address state or province |
| `data[].Billing_Country` | `string` | Billing address country |
| `data[].Description` | `string` | Description or notes about the account |
| `data[].Created_Time` | `string` | Time the record was created |
| `data[].Modified_Time` | `string` | Time the record was last modified |

</details>

## Deals

### Deals List

Returns a paginated list of deals

#### Python SDK

```python
await zoho_crm.deals.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "deals",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number |
| `per_page` | `integer` | No | Number of records per page |
| `page_token` | `string` | No | Page token for fetching beyond 2000 records |
| `sort_by` | `string` | No | Field to sort by |
| `sort_order` | `"asc" \| "desc"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `Owner` | `object \| any` |  |
| `Deal_Name` | `null \| string` |  |
| `Amount` | `null \| number` |  |
| `Stage` | `null \| string` |  |
| `Probability` | `null \| integer` |  |
| `Closing_Date` | `null \| string` |  |
| `Type` | `null \| string` |  |
| `Next_Step` | `null \| string` |  |
| `Lead_Source` | `null \| string` |  |
| `Contact_Name` | `object \| any` |  |
| `Account_Name` | `object \| any` |  |
| `Campaign_Source` | `object \| any` |  |
| `Pipeline` | `null \| object` |  |
| `Description` | `null \| string` |  |
| `Created_Time` | `null \| string` |  |
| `Modified_Time` | `null \| string` |  |
| `Created_By` | `object \| any` |  |
| `Modified_By` | `object \| any` |  |
| `Record_Status__s` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `more_records` | `boolean` |  |
| `page` | `integer` |  |

</details>

### Deals Create

Creates a new deal record in Zoho CRM

#### Python SDK

```python
await zoho_crm.deals.create(
    data=[]
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "deals",
    "action": "create",
    "params": {
        "data": []
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data` | `array<object>` | Yes | Array containing the deal record to create |
| `data.Deal_Name` | `string` | Yes | Deal name (required) |
| `data.Amount` | `number` | No | Monetary value of the deal |
| `data.Stage` | `string` | Yes | Current stage of the deal in the pipeline (required) |
| `data.Probability` | `integer` | No | Probability of closing the deal (percentage) |
| `data.Closing_Date` | `string` | Yes | Expected closing date (YYYY-MM-DD) |
| `data.Type` | `string` | No | Type of deal (e.g., New Business, Existing Business) |
| `data.Next_Step` | `string` | No | Next step in the deal process |
| `data.Lead_Source` | `string` | No | Source from which the deal originated |
| `data.Description` | `string` | No | Description or notes about the deal |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array<object>` |  |
| `data[].code` | `string` |  |
| `data[].details` | `object` |  |
| `data[].details.Modified_Time` | `null \| string` |  |
| `data[].details.Modified_By` | `object \| any` |  |
| `data[].details.Created_Time` | `null \| string` |  |
| `data[].details.id` | `string` |  |
| `data[].details.Created_By` | `object \| any` |  |
| `data[].message` | `string` |  |
| `data[].status` | `string` |  |


</details>

### Deals Get

Get a single deal by ID

#### Python SDK

```python
await zoho_crm.deals.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "deals",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Deal ID |


### Deals Update

Updates an existing deal record in Zoho CRM

#### Python SDK

```python
await zoho_crm.deals.update(
    data=[],
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "deals",
    "action": "update",
    "params": {
        "data": [],
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data` | `array<object>` | Yes | Array containing the deal fields to update |
| `data.Deal_Name` | `string` | No | Deal name |
| `data.Amount` | `number` | No | Monetary value of the deal |
| `data.Stage` | `string` | No | Current stage of the deal in the pipeline |
| `data.Probability` | `integer` | No | Probability of closing the deal (percentage) |
| `data.Closing_Date` | `string` | No | Expected closing date (YYYY-MM-DD) |
| `data.Type` | `string` | No | Type of deal (e.g., New Business, Existing Business) |
| `data.Next_Step` | `string` | No | Next step in the deal process |
| `data.Lead_Source` | `string` | No | Source from which the deal originated |
| `data.Description` | `string` | No | Description or notes about the deal |
| `id` | `string` | Yes | Deal ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array<object>` |  |
| `data[].code` | `string` |  |
| `data[].details` | `object` |  |
| `data[].details.Modified_Time` | `null \| string` |  |
| `data[].details.Modified_By` | `object \| any` |  |
| `data[].details.Created_Time` | `null \| string` |  |
| `data[].details.id` | `string` |  |
| `data[].details.Created_By` | `object \| any` |  |
| `data[].message` | `string` |  |
| `data[].status` | `string` |  |


</details>

### Deals Context Store Search

Search and filter deals records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zoho_crm.deals.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "deals",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `id` | `string` | Unique record identifier |
| `Deal_Name` | `string` | Name of the deal |
| `Amount` | `number` | Monetary value of the deal |
| `Stage` | `string` | Current stage of the deal in the pipeline |
| `Probability` | `integer` | Probability of closing the deal (percentage) |
| `Closing_Date` | `string` | Expected closing date |
| `Type` | `string` | Type of deal (e.g., New Business, Existing Business) |
| `Next_Step` | `string` | Next step in the deal process |
| `Lead_Source` | `string` | Source from which the deal originated |
| `Description` | `string` | Description or notes about the deal |
| `Created_Time` | `string` | Time the record was created |
| `Modified_Time` | `string` | Time the record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique record identifier |
| `data[].Deal_Name` | `string` | Name of the deal |
| `data[].Amount` | `number` | Monetary value of the deal |
| `data[].Stage` | `string` | Current stage of the deal in the pipeline |
| `data[].Probability` | `integer` | Probability of closing the deal (percentage) |
| `data[].Closing_Date` | `string` | Expected closing date |
| `data[].Type` | `string` | Type of deal (e.g., New Business, Existing Business) |
| `data[].Next_Step` | `string` | Next step in the deal process |
| `data[].Lead_Source` | `string` | Source from which the deal originated |
| `data[].Description` | `string` | Description or notes about the deal |
| `data[].Created_Time` | `string` | Time the record was created |
| `data[].Modified_Time` | `string` | Time the record was last modified |

</details>

## Campaigns

### Campaigns List

Returns a paginated list of campaigns

#### Python SDK

```python
await zoho_crm.campaigns.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number |
| `per_page` | `integer` | No | Number of records per page |
| `page_token` | `string` | No | Page token for fetching beyond 2000 records |
| `sort_by` | `string` | No | Field to sort by |
| `sort_order` | `"asc" \| "desc"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `Owner` | `object \| any` |  |
| `Campaign_Name` | `null \| string` |  |
| `Type` | `null \| string` |  |
| `Status` | `null \| string` |  |
| `Start_Date` | `null \| string` |  |
| `End_Date` | `null \| string` |  |
| `Expected_Revenue` | `null \| number` |  |
| `Budgeted_Cost` | `null \| number` |  |
| `Actual_Cost` | `null \| number` |  |
| `Num_sent` | `null \| string` |  |
| `Expected_Response` | `null \| integer` |  |
| `Description` | `null \| string` |  |
| `Created_Time` | `null \| string` |  |
| `Modified_Time` | `null \| string` |  |
| `Created_By` | `object \| any` |  |
| `Modified_By` | `object \| any` |  |
| `Record_Status__s` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `more_records` | `boolean` |  |
| `page` | `integer` |  |

</details>

### Campaigns Get

Get a single campaign by ID

#### Python SDK

```python
await zoho_crm.campaigns.get(
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
| `id` | `string` | Yes | Campaign ID |


### Campaigns Context Store Search

Search and filter campaigns records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zoho_crm.campaigns.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `id` | `string` | Unique record identifier |
| `Campaign_Name` | `string` | Name of the campaign |
| `Type` | `string` | Type of campaign (e.g., Email, Webinar, Conference) |
| `Status` | `string` | Current status of the campaign |
| `Start_Date` | `string` | Campaign start date |
| `End_Date` | `string` | Campaign end date |
| `Expected_Revenue` | `number` | Expected revenue from the campaign |
| `Budgeted_Cost` | `number` | Budget allocated for the campaign |
| `Actual_Cost` | `number` | Actual cost incurred |
| `Num_sent` | `string` | Number of campaign messages sent |
| `Expected_Response` | `integer` | Expected response count |
| `Description` | `string` | Description or notes about the campaign |
| `Created_Time` | `string` | Time the record was created |
| `Modified_Time` | `string` | Time the record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique record identifier |
| `data[].Campaign_Name` | `string` | Name of the campaign |
| `data[].Type` | `string` | Type of campaign (e.g., Email, Webinar, Conference) |
| `data[].Status` | `string` | Current status of the campaign |
| `data[].Start_Date` | `string` | Campaign start date |
| `data[].End_Date` | `string` | Campaign end date |
| `data[].Expected_Revenue` | `number` | Expected revenue from the campaign |
| `data[].Budgeted_Cost` | `number` | Budget allocated for the campaign |
| `data[].Actual_Cost` | `number` | Actual cost incurred |
| `data[].Num_sent` | `string` | Number of campaign messages sent |
| `data[].Expected_Response` | `integer` | Expected response count |
| `data[].Description` | `string` | Description or notes about the campaign |
| `data[].Created_Time` | `string` | Time the record was created |
| `data[].Modified_Time` | `string` | Time the record was last modified |

</details>

## Tasks

### Tasks List

Returns a paginated list of tasks

#### Python SDK

```python
await zoho_crm.tasks.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number |
| `per_page` | `integer` | No | Number of records per page |
| `page_token` | `string` | No | Page token for fetching beyond 2000 records |
| `sort_by` | `string` | No | Field to sort by |
| `sort_order` | `"asc" \| "desc"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `Owner` | `object \| any` |  |
| `Subject` | `null \| string` |  |
| `Due_Date` | `null \| string` |  |
| `Status` | `null \| string` |  |
| `Priority` | `null \| string` |  |
| `Send_Notification_Email` | `null \| boolean` |  |
| `Remind_At` | `null \| object` |  |
| `Who_Id` | `object \| any` |  |
| `What_Id` | `object \| any` |  |
| `Recurring_Activity` | `null \| object` |  |
| `Description` | `null \| string` |  |
| `Created_Time` | `null \| string` |  |
| `Modified_Time` | `null \| string` |  |
| `Created_By` | `object \| any` |  |
| `Modified_By` | `object \| any` |  |
| `Record_Status__s` | `null \| string` |  |
| `Closed_Time` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `more_records` | `boolean` |  |
| `page` | `integer` |  |

</details>

### Tasks Create

Creates a new task record in Zoho CRM

#### Python SDK

```python
await zoho_crm.tasks.create(
    data=[]
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
        "data": []
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data` | `array<object>` | Yes | Array containing the task record to create |
| `data.Subject` | `string` | Yes | Subject or title of the task (required) |
| `data.Due_Date` | `string` | No | Due date for the task (YYYY-MM-DD) |
| `data.Status` | `string` | No | Task status (e.g., Not Started, In Progress, Completed) |
| `data.Priority` | `string` | No | Priority level (e.g., High, Highest, Low, Lowest, Normal) |
| `data.Send_Notification_Email` | `boolean` | No | Whether to send a notification email |
| `data.Description` | `string` | No | Description or notes about the task |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array<object>` |  |
| `data[].code` | `string` |  |
| `data[].details` | `object` |  |
| `data[].details.Modified_Time` | `null \| string` |  |
| `data[].details.Modified_By` | `object \| any` |  |
| `data[].details.Created_Time` | `null \| string` |  |
| `data[].details.id` | `string` |  |
| `data[].details.Created_By` | `object \| any` |  |
| `data[].message` | `string` |  |
| `data[].status` | `string` |  |


</details>

### Tasks Get

Get a single task by ID

#### Python SDK

```python
await zoho_crm.tasks.get(
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
| `id` | `string` | Yes | Task ID |


### Tasks Update

Updates an existing task record in Zoho CRM

#### Python SDK

```python
await zoho_crm.tasks.update(
    data=[],
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
        "data": [],
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data` | `array<object>` | Yes | Array containing the task fields to update |
| `data.Subject` | `string` | No | Subject or title of the task |
| `data.Due_Date` | `string` | No | Due date for the task (YYYY-MM-DD) |
| `data.Status` | `string` | No | Task status (e.g., Not Started, In Progress, Completed) |
| `data.Priority` | `string` | No | Priority level (e.g., High, Highest, Low, Lowest, Normal) |
| `data.Send_Notification_Email` | `boolean` | No | Whether to send a notification email |
| `data.Description` | `string` | No | Description or notes about the task |
| `id` | `string` | Yes | Task ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array<object>` |  |
| `data[].code` | `string` |  |
| `data[].details` | `object` |  |
| `data[].details.Modified_Time` | `null \| string` |  |
| `data[].details.Modified_By` | `object \| any` |  |
| `data[].details.Created_Time` | `null \| string` |  |
| `data[].details.id` | `string` |  |
| `data[].details.Created_By` | `object \| any` |  |
| `data[].message` | `string` |  |
| `data[].status` | `string` |  |


</details>

### Tasks Context Store Search

Search and filter tasks records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zoho_crm.tasks.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
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
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `id` | `string` | Unique record identifier |
| `Subject` | `string` | Subject or title of the task |
| `Due_Date` | `string` | Due date for the task |
| `Status` | `string` | Current status (e.g., Not Started, In Progress, Completed) |
| `Priority` | `string` | Priority level (e.g., High, Highest, Low, Lowest, Normal) |
| `Send_Notification_Email` | `boolean` | Whether to send a notification email |
| `Description` | `string` | Description or notes about the task |
| `Created_Time` | `string` | Time the record was created |
| `Modified_Time` | `string` | Time the record was last modified |
| `Closed_Time` | `string` | Time the task was closed |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique record identifier |
| `data[].Subject` | `string` | Subject or title of the task |
| `data[].Due_Date` | `string` | Due date for the task |
| `data[].Status` | `string` | Current status (e.g., Not Started, In Progress, Completed) |
| `data[].Priority` | `string` | Priority level (e.g., High, Highest, Low, Lowest, Normal) |
| `data[].Send_Notification_Email` | `boolean` | Whether to send a notification email |
| `data[].Description` | `string` | Description or notes about the task |
| `data[].Created_Time` | `string` | Time the record was created |
| `data[].Modified_Time` | `string` | Time the record was last modified |
| `data[].Closed_Time` | `string` | Time the task was closed |

</details>

## Events

### Events List

Returns a paginated list of events (meetings/calendar events)

#### Python SDK

```python
await zoho_crm.events.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "events",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number |
| `per_page` | `integer` | No | Number of records per page |
| `page_token` | `string` | No | Page token for fetching beyond 2000 records |
| `sort_by` | `string` | No | Field to sort by |
| `sort_order` | `"asc" \| "desc"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `Owner` | `object \| any` |  |
| `Event_Title` | `null \| string` |  |
| `Start_DateTime` | `null \| string` |  |
| `End_DateTime` | `null \| string` |  |
| `All_day` | `null \| boolean` |  |
| `Location` | `null \| string` |  |
| `Participants` | `null \| array` |  |
| `Who_Id` | `object \| any` |  |
| `What_Id` | `object \| any` |  |
| `Remind_At` | `null \| object` |  |
| `Recurring_Activity` | `null \| object` |  |
| `Description` | `null \| string` |  |
| `Created_Time` | `null \| string` |  |
| `Modified_Time` | `null \| string` |  |
| `Created_By` | `object \| any` |  |
| `Modified_By` | `object \| any` |  |
| `Record_Status__s` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `more_records` | `boolean` |  |
| `page` | `integer` |  |

</details>

### Events Get

Get a single event by ID

#### Python SDK

```python
await zoho_crm.events.get(
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
| `id` | `string` | Yes | Event ID |


### Events Context Store Search

Search and filter events records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zoho_crm.events.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "events",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `id` | `string` | Unique record identifier |
| `Event_Title` | `string` | Title of the event |
| `Start_DateTime` | `string` | Event start date and time |
| `End_DateTime` | `string` | Event end date and time |
| `All_day` | `boolean` | Whether this is an all-day event |
| `Location` | `string` | Event location |
| `Description` | `string` | Description or notes about the event |
| `Created_Time` | `string` | Time the record was created |
| `Modified_Time` | `string` | Time the record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique record identifier |
| `data[].Event_Title` | `string` | Title of the event |
| `data[].Start_DateTime` | `string` | Event start date and time |
| `data[].End_DateTime` | `string` | Event end date and time |
| `data[].All_day` | `boolean` | Whether this is an all-day event |
| `data[].Location` | `string` | Event location |
| `data[].Description` | `string` | Description or notes about the event |
| `data[].Created_Time` | `string` | Time the record was created |
| `data[].Modified_Time` | `string` | Time the record was last modified |

</details>

## Calls

### Calls List

Returns a paginated list of calls

#### Python SDK

```python
await zoho_crm.calls.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "calls",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number |
| `per_page` | `integer` | No | Number of records per page |
| `page_token` | `string` | No | Page token for fetching beyond 2000 records |
| `sort_by` | `string` | No | Field to sort by |
| `sort_order` | `"asc" \| "desc"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `Owner` | `object \| any` |  |
| `Subject` | `null \| string` |  |
| `Call_Type` | `null \| string` |  |
| `Call_Start_Time` | `null \| string` |  |
| `Call_Duration` | `null \| string` |  |
| `Call_Duration_in_seconds` | `null \| number` |  |
| `Call_Purpose` | `null \| string` |  |
| `Call_Result` | `null \| string` |  |
| `Who_Id` | `object \| any` |  |
| `What_Id` | `object \| any` |  |
| `Description` | `null \| string` |  |
| `Caller_ID` | `null \| string` |  |
| `Outgoing_Call_Status` | `null \| string` |  |
| `Created_Time` | `null \| string` |  |
| `Modified_Time` | `null \| string` |  |
| `Created_By` | `object \| any` |  |
| `Modified_By` | `object \| any` |  |
| `Record_Status__s` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `more_records` | `boolean` |  |
| `page` | `integer` |  |

</details>

### Calls Get

Get a single call by ID

#### Python SDK

```python
await zoho_crm.calls.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "calls",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Call ID |


### Calls Context Store Search

Search and filter calls records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zoho_crm.calls.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "calls",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `id` | `string` | Unique record identifier |
| `Subject` | `string` | Subject of the call |
| `Call_Type` | `string` | Type of call (Inbound or Outbound) |
| `Call_Start_Time` | `string` | Start time of the call |
| `Call_Duration` | `string` | Duration of the call as a formatted string |
| `Call_Duration_in_seconds` | `number` | Duration of the call in seconds |
| `Call_Purpose` | `string` | Purpose of the call |
| `Call_Result` | `string` | Result or outcome of the call |
| `Caller_ID` | `string` | Caller ID number |
| `Outgoing_Call_Status` | `string` | Status of outgoing calls |
| `Description` | `string` | Description or notes about the call |
| `Created_Time` | `string` | Time the record was created |
| `Modified_Time` | `string` | Time the record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique record identifier |
| `data[].Subject` | `string` | Subject of the call |
| `data[].Call_Type` | `string` | Type of call (Inbound or Outbound) |
| `data[].Call_Start_Time` | `string` | Start time of the call |
| `data[].Call_Duration` | `string` | Duration of the call as a formatted string |
| `data[].Call_Duration_in_seconds` | `number` | Duration of the call in seconds |
| `data[].Call_Purpose` | `string` | Purpose of the call |
| `data[].Call_Result` | `string` | Result or outcome of the call |
| `data[].Caller_ID` | `string` | Caller ID number |
| `data[].Outgoing_Call_Status` | `string` | Status of outgoing calls |
| `data[].Description` | `string` | Description or notes about the call |
| `data[].Created_Time` | `string` | Time the record was created |
| `data[].Modified_Time` | `string` | Time the record was last modified |

</details>

## Products

### Products List

Returns a paginated list of products

#### Python SDK

```python
await zoho_crm.products.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "products",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number |
| `per_page` | `integer` | No | Number of records per page |
| `page_token` | `string` | No | Page token for fetching beyond 2000 records |
| `sort_by` | `string` | No | Field to sort by |
| `sort_order` | `"asc" \| "desc"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `Owner` | `object \| any` |  |
| `Product_Name` | `null \| string` |  |
| `Product_Code` | `null \| string` |  |
| `Product_Category` | `null \| string` |  |
| `Product_Active` | `null \| boolean` |  |
| `Unit_Price` | `null \| number` |  |
| `Commission_Rate` | `null \| number` |  |
| `Manufacturer` | `null \| string` |  |
| `Sales_Start_Date` | `null \| string` |  |
| `Sales_End_Date` | `null \| string` |  |
| `Support_Start_Date` | `null \| string` |  |
| `Support_Expiry_Date` | `null \| string` |  |
| `Qty_in_Stock` | `null \| number` |  |
| `Qty_in_Demand` | `null \| number` |  |
| `Qty_Ordered` | `null \| number` |  |
| `Reorder_Level` | `null \| number` |  |
| `Handler` | `object \| any` |  |
| `Tax` | `null \| array` |  |
| `Vendor_Name` | `object \| any` |  |
| `Description` | `null \| string` |  |
| `Created_Time` | `null \| string` |  |
| `Modified_Time` | `null \| string` |  |
| `Created_By` | `object \| any` |  |
| `Modified_By` | `object \| any` |  |
| `Record_Status__s` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `more_records` | `boolean` |  |
| `page` | `integer` |  |

</details>

### Products Get

Get a single product by ID

#### Python SDK

```python
await zoho_crm.products.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "products",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Product ID |


### Products Context Store Search

Search and filter products records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zoho_crm.products.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "products",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `id` | `string` | Unique record identifier |
| `Product_Name` | `string` | Name of the product |
| `Product_Code` | `string` | Product code or SKU |
| `Product_Category` | `string` | Category of the product |
| `Product_Active` | `boolean` | Whether the product is active |
| `Unit_Price` | `number` | Unit price of the product |
| `Commission_Rate` | `number` | Commission rate for the product |
| `Manufacturer` | `string` | Product manufacturer |
| `Sales_Start_Date` | `string` | Date when sales begin |
| `Sales_End_Date` | `string` | Date when sales end |
| `Qty_in_Stock` | `number` | Quantity currently in stock |
| `Qty_in_Demand` | `number` | Quantity in demand |
| `Qty_Ordered` | `number` | Quantity on order |
| `Description` | `string` | Description of the product |
| `Created_Time` | `string` | Time the record was created |
| `Modified_Time` | `string` | Time the record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique record identifier |
| `data[].Product_Name` | `string` | Name of the product |
| `data[].Product_Code` | `string` | Product code or SKU |
| `data[].Product_Category` | `string` | Category of the product |
| `data[].Product_Active` | `boolean` | Whether the product is active |
| `data[].Unit_Price` | `number` | Unit price of the product |
| `data[].Commission_Rate` | `number` | Commission rate for the product |
| `data[].Manufacturer` | `string` | Product manufacturer |
| `data[].Sales_Start_Date` | `string` | Date when sales begin |
| `data[].Sales_End_Date` | `string` | Date when sales end |
| `data[].Qty_in_Stock` | `number` | Quantity currently in stock |
| `data[].Qty_in_Demand` | `number` | Quantity in demand |
| `data[].Qty_Ordered` | `number` | Quantity on order |
| `data[].Description` | `string` | Description of the product |
| `data[].Created_Time` | `string` | Time the record was created |
| `data[].Modified_Time` | `string` | Time the record was last modified |

</details>

## Quotes

### Quotes List

Returns a paginated list of quotes

#### Python SDK

```python
await zoho_crm.quotes.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "quotes",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number |
| `per_page` | `integer` | No | Number of records per page |
| `page_token` | `string` | No | Page token for fetching beyond 2000 records |
| `sort_by` | `string` | No | Field to sort by |
| `sort_order` | `"asc" \| "desc"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `Owner` | `object \| any` |  |
| `Subject` | `null \| string` |  |
| `Quote_Stage` | `null \| string` |  |
| `Valid_Till` | `null \| string` |  |
| `Deal_Name` | `object \| any` |  |
| `Contact_Name` | `object \| any` |  |
| `Account_Name` | `object \| any` |  |
| `Carrier` | `null \| string` |  |
| `Shipping_Street` | `null \| string` |  |
| `Shipping_City` | `null \| string` |  |
| `Shipping_State` | `null \| string` |  |
| `Shipping_Code` | `null \| string` |  |
| `Shipping_Country` | `null \| string` |  |
| `Billing_Street` | `null \| string` |  |
| `Billing_City` | `null \| string` |  |
| `Billing_State` | `null \| string` |  |
| `Billing_Code` | `null \| string` |  |
| `Billing_Country` | `null \| string` |  |
| `Sub_Total` | `null \| number` |  |
| `Tax` | `null \| number` |  |
| `Adjustment` | `null \| number` |  |
| `Grand_Total` | `null \| number` |  |
| `Discount` | `null \| number` |  |
| `Terms_and_Conditions` | `null \| string` |  |
| `Description` | `null \| string` |  |
| `Created_Time` | `null \| string` |  |
| `Modified_Time` | `null \| string` |  |
| `Created_By` | `object \| any` |  |
| `Modified_By` | `object \| any` |  |
| `Record_Status__s` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `more_records` | `boolean` |  |
| `page` | `integer` |  |

</details>

### Quotes Get

Get a single quote by ID

#### Python SDK

```python
await zoho_crm.quotes.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "quotes",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Quote ID |


### Quotes Context Store Search

Search and filter quotes records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zoho_crm.quotes.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "quotes",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `id` | `string` | Unique record identifier |
| `Subject` | `string` | Subject or title of the quote |
| `Quote_Stage` | `string` | Current stage of the quote |
| `Valid_Till` | `string` | Date until which the quote is valid |
| `Carrier` | `string` | Shipping carrier |
| `Sub_Total` | `number` | Subtotal before tax and adjustments |
| `Tax` | `number` | Tax amount |
| `Adjustment` | `number` | Adjustment amount |
| `Grand_Total` | `number` | Total amount including tax and adjustments |
| `Discount` | `number` | Discount amount |
| `Terms_and_Conditions` | `string` | Terms and conditions text |
| `Description` | `string` | Description or notes about the quote |
| `Created_Time` | `string` | Time the record was created |
| `Modified_Time` | `string` | Time the record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique record identifier |
| `data[].Subject` | `string` | Subject or title of the quote |
| `data[].Quote_Stage` | `string` | Current stage of the quote |
| `data[].Valid_Till` | `string` | Date until which the quote is valid |
| `data[].Carrier` | `string` | Shipping carrier |
| `data[].Sub_Total` | `number` | Subtotal before tax and adjustments |
| `data[].Tax` | `number` | Tax amount |
| `data[].Adjustment` | `number` | Adjustment amount |
| `data[].Grand_Total` | `number` | Total amount including tax and adjustments |
| `data[].Discount` | `number` | Discount amount |
| `data[].Terms_and_Conditions` | `string` | Terms and conditions text |
| `data[].Description` | `string` | Description or notes about the quote |
| `data[].Created_Time` | `string` | Time the record was created |
| `data[].Modified_Time` | `string` | Time the record was last modified |

</details>

## Invoices

### Invoices List

Returns a paginated list of invoices

#### Python SDK

```python
await zoho_crm.invoices.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "invoices",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number |
| `per_page` | `integer` | No | Number of records per page |
| `page_token` | `string` | No | Page token for fetching beyond 2000 records |
| `sort_by` | `string` | No | Field to sort by |
| `sort_order` | `"asc" \| "desc"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `Owner` | `object \| any` |  |
| `Subject` | `null \| string` |  |
| `Invoice_Number` | `null \| string` |  |
| `Invoice_Date` | `null \| string` |  |
| `Due_Date` | `null \| string` |  |
| `Status` | `null \| string` |  |
| `Sales_Order` | `object \| any` |  |
| `Contact_Name` | `object \| any` |  |
| `Account_Name` | `object \| any` |  |
| `Deal_Name` | `object \| any` |  |
| `Purchase_Order` | `null \| string` |  |
| `Excise_Duty` | `null \| number` |  |
| `Billing_Street` | `null \| string` |  |
| `Billing_City` | `null \| string` |  |
| `Billing_State` | `null \| string` |  |
| `Billing_Code` | `null \| string` |  |
| `Billing_Country` | `null \| string` |  |
| `Shipping_Street` | `null \| string` |  |
| `Shipping_City` | `null \| string` |  |
| `Shipping_State` | `null \| string` |  |
| `Shipping_Code` | `null \| string` |  |
| `Shipping_Country` | `null \| string` |  |
| `Sub_Total` | `null \| number` |  |
| `Tax` | `null \| number` |  |
| `Adjustment` | `null \| number` |  |
| `Grand_Total` | `null \| number` |  |
| `Discount` | `null \| number` |  |
| `Terms_and_Conditions` | `null \| string` |  |
| `Description` | `null \| string` |  |
| `Created_Time` | `null \| string` |  |
| `Modified_Time` | `null \| string` |  |
| `Created_By` | `object \| any` |  |
| `Modified_By` | `object \| any` |  |
| `Record_Status__s` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `more_records` | `boolean` |  |
| `page` | `integer` |  |

</details>

### Invoices Get

Get a single invoice by ID

#### Python SDK

```python
await zoho_crm.invoices.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "invoices",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Invoice ID |


### Invoices Context Store Search

Search and filter invoices records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zoho_crm.invoices.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "invoices",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `id` | `string` | Unique record identifier |
| `Subject` | `string` | Subject or title of the invoice |
| `Invoice_Number` | `string` | Invoice number |
| `Invoice_Date` | `string` | Date the invoice was issued |
| `Due_Date` | `string` | Payment due date |
| `Status` | `string` | Current status of the invoice |
| `Purchase_Order` | `string` | Associated purchase order number |
| `Sub_Total` | `number` | Subtotal before tax and adjustments |
| `Tax` | `number` | Tax amount |
| `Adjustment` | `number` | Adjustment amount |
| `Grand_Total` | `number` | Total amount including tax and adjustments |
| `Discount` | `number` | Discount amount |
| `Excise_Duty` | `number` | Excise duty amount |
| `Terms_and_Conditions` | `string` | Terms and conditions text |
| `Description` | `string` | Description or notes about the invoice |
| `Created_Time` | `string` | Time the record was created |
| `Modified_Time` | `string` | Time the record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique record identifier |
| `data[].Subject` | `string` | Subject or title of the invoice |
| `data[].Invoice_Number` | `string` | Invoice number |
| `data[].Invoice_Date` | `string` | Date the invoice was issued |
| `data[].Due_Date` | `string` | Payment due date |
| `data[].Status` | `string` | Current status of the invoice |
| `data[].Purchase_Order` | `string` | Associated purchase order number |
| `data[].Sub_Total` | `number` | Subtotal before tax and adjustments |
| `data[].Tax` | `number` | Tax amount |
| `data[].Adjustment` | `number` | Adjustment amount |
| `data[].Grand_Total` | `number` | Total amount including tax and adjustments |
| `data[].Discount` | `number` | Discount amount |
| `data[].Excise_Duty` | `number` | Excise duty amount |
| `data[].Terms_and_Conditions` | `string` | Terms and conditions text |
| `data[].Description` | `string` | Description or notes about the invoice |
| `data[].Created_Time` | `string` | Time the record was created |
| `data[].Modified_Time` | `string` | Time the record was last modified |

</details>

