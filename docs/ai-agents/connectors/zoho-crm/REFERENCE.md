# Zoho-Crm full reference

This is the full reference documentation for the Zoho-Crm agent connector.

## Supported entities and actions

The Zoho-Crm connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Leads | [List](#leads-list), [Get](#leads-get), [Context Store Search](#leads-context-store-search), [Context Store SQL Query](#leads-context-store-sql-query), [Semantic Search](#leads-semantic-search) |
| Contacts | [List](#contacts-list), [Get](#contacts-get), [Context Store Search](#contacts-context-store-search), [Context Store SQL Query](#contacts-context-store-sql-query), [Semantic Search](#contacts-semantic-search) |
| Accounts | [List](#accounts-list), [Get](#accounts-get), [Context Store Search](#accounts-context-store-search), [Context Store SQL Query](#accounts-context-store-sql-query), [Semantic Search](#accounts-semantic-search) |
| Deals | [List](#deals-list), [Get](#deals-get), [Context Store Search](#deals-context-store-search), [Context Store SQL Query](#deals-context-store-sql-query), [Semantic Search](#deals-semantic-search) |
| Campaigns | [List](#campaigns-list), [Get](#campaigns-get), [Context Store Search](#campaigns-context-store-search), [Context Store SQL Query](#campaigns-context-store-sql-query), [Semantic Search](#campaigns-semantic-search) |
| Tasks | [List](#tasks-list), [Get](#tasks-get), [Context Store Search](#tasks-context-store-search), [Context Store SQL Query](#tasks-context-store-sql-query), [Semantic Search](#tasks-semantic-search) |
| Events | [List](#events-list), [Get](#events-get), [Context Store Search](#events-context-store-search), [Context Store SQL Query](#events-context-store-sql-query), [Semantic Search](#events-semantic-search) |
| Calls | [List](#calls-list), [Get](#calls-get), [Context Store Search](#calls-context-store-search), [Context Store SQL Query](#calls-context-store-sql-query), [Semantic Search](#calls-semantic-search) |
| Products | [List](#products-list), [Get](#products-get), [Context Store Search](#products-context-store-search), [Context Store SQL Query](#products-context-store-sql-query), [Semantic Search](#products-semantic-search) |
| Quotes | [List](#quotes-list), [Get](#quotes-get), [Context Store Search](#quotes-context-store-search), [Context Store SQL Query](#quotes-context-store-sql-query) |
| Invoices | [List](#invoices-list), [Get](#invoices-get), [Context Store Search](#invoices-context-store-search), [Context Store SQL Query](#invoices-context-store-sql-query) |
| Notes | [List](#notes-list), [Get](#notes-get), [Context Store Search](#notes-context-store-search), [Context Store SQL Query](#notes-context-store-sql-query), [Semantic Search](#notes-semantic-search) |

## Leads

### Leads List

Returns a paginated list of leads

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "leads",
  "action": "list"
}'
```

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
| `Designation` | `null \| string` |  |
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
| `$approval` | `null \| object` |  |
| `$approval_state` | `null \| string` |  |
| `$approved` | `null \| boolean` |  |
| `$converted` | `null \| boolean` |  |
| `$currency_symbol` | `null \| string` |  |
| `$editable` | `null \| boolean` |  |
| `$field_states` | `null \| object` |  |
| `$in_merge` | `null \| boolean` |  |
| `$layout_id` | `null \| object` |  |
| `$locked_for_me` | `null \| boolean` |  |
| `$orchestration` | `null \| boolean` |  |
| `$process_flow` | `null \| boolean` |  |
| `$review` | `null \| object` |  |
| `$review_process` | `null \| object` |  |
| `$zia_owner_assignment` | `null \| string` |  |
| `Email_Opt_Out` | `null \| boolean` |  |
| `Last_Activity_Time` | `null \| string` |  |
| `Locked__s` | `null \| boolean` |  |
| `Record_Image` | `null \| string` |  |
| `Salutation` | `null \| string` |  |
| `Secondary_Email` | `null \| string` |  |
| `Skype_ID` | `null \| string` |  |
| `Tag` | `null \| array` |  |
| `Twitter` | `null \| string` |  |
| `Unsubscribed_Mode` | `null \| string` |  |
| `Unsubscribed_Time` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `more_records` | `boolean` |  |
| `page` | `integer` |  |

</details>

### Leads Get

Get a single lead by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "leads",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

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


### Leads Context Store Search

Search and filter leads records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "leads",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "id": "<str>"
        }
      }
    }
  }
}'
```

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
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
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
| `Designation` | `string` | Lead's job title. Zoho names this `Designation` on Leads and `Title` on Contacts; there is no `Title` field on the Leads module.
 |
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
| `data[].Designation` | `string` | Lead's job title. Zoho names this `Designation` on Leads and `Title` on Contacts; there is no `Title` field on the Leads module.
 |
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

### Leads Context Store SQL Query

Run a SQL query against leads records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "leads",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await zoho_crm.leads.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "leads",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

### Leads Semantic Search

Search leads records by meaning rather than by exact or fuzzy field values. Semantic search embeds a natural-language `prompt` and returns the most similar passages, ranked by relevance. Pass `semantic={field, prompt, filter?, context_size?, min_similarity?, dedup?}` to `context_store_search` instead of `query`. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "leads",
  "action": "context_store_search",
  "params": {
    "semantic": {"field": "Full_Name", "prompt": "<your natural-language query>"}
  }
}'
```

#### Python SDK

Semantic search is passed through the generic `execute` method — the typed `leads.context_store_search` helper only accepts `query`.

```python
await zoho_crm.execute(
    "leads",
    "context_store_search",
    {"semantic": {"field": "Full_Name", "prompt": "<your natural-language query>"}},
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
        "semantic": {"field": "Full_Name", "prompt": "<your natural-language query>"}
    }
}'
```

#### Semantic Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `semantic.field` | `string` | Yes | Field to search semantically. Mutually exclusive with `query`. |
| `semantic.prompt` | `string` | Yes | Natural-language query that is embedded and compared against stored passages. |
| `semantic.filter` | `object` | No | Filter conditions (same shape/operators as `query.filter`). `sort` is not supported — results are ranked by similarity. |
| `semantic.context_size` | `integer` | No | Characters of surrounding context to return per hit, up to the field's configured window. Omit to return the full configured window. |
| `semantic.min_similarity` | `number` | No | Minimum similarity score in [-1.0, 1.0]. Omit for 0.25; scores below the threshold are discarded before deduplication and top-k selection. Use -1.0 to disable the cutoff. |
| `semantic.dedup` | `string` | No | `max` (default) returns the single best-scoring passage per record; `none` returns multiple passages per record, still ranked by similarity and capped by `limit`. |
| `fields` | `array` | No | Field paths to include in results (dot notation for nested fields). Applied to each hit's `entity`. |
| `limit` | `integer` | No | Maximum results to return (default 10, maximum 100). |

#### Semantically Searchable Fields

| Field Name | Max Context (chars) | Description |
|------------|---------------------|-------------|
| `Full_Name` | 2048 | Lead's full name |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching passages |
| `data[].entity` | `object` | The matched source record |
| `data[].entity.id` | `string` | Source record field |
| `data[].entity.Modified_Time` | `string` | Source record field |
| `data[].entity.Created_Time` | `string` | Source record field |
| `data[].entity.Full_Name` | `string` | Source record field |
| `data[].entity.Designation` | `string` | Source record field |
| `data[].entity.Company` | `string` | Source record field |
| `data[].entity.Lead_Status` | `string` | Source record field |
| `data[].entity.Lead_Source` | `string` | Source record field |
| `data[].entity.Industry` | `string` | Source record field |
| `data[].entity.State` | `string` | Source record field |
| `data[].entity.Country` | `string` | Source record field |
| `data[].metadata` | `object` | Match metadata |
| `data[].metadata.score` | `number` | Similarity score |
| `data[].metadata.context` | `string` | The matched passage text |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Contacts

### Contacts List

Returns a paginated list of contacts

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "contacts",
  "action": "list"
}'
```

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
| `$approval` | `null \| object` |  |
| `$approval_state` | `null \| string` |  |
| `$approved` | `null \| boolean` |  |
| `$currency_symbol` | `null \| string` |  |
| `$editable` | `null \| boolean` |  |
| `$field_states` | `null \| object` |  |
| `$in_merge` | `null \| boolean` |  |
| `$is_duplicate` | `null \| boolean` |  |
| `$layout_id` | `null \| object` |  |
| `$locked_for_me` | `null \| boolean` |  |
| `$orchestration` | `null \| boolean` |  |
| `$process_flow` | `null \| boolean` |  |
| `$review` | `null \| object` |  |
| `$review_process` | `null \| object` |  |
| `$state` | `null \| string` |  |
| `$zia_owner_assignment` | `null \| string` |  |
| `Assistant` | `null \| string` |  |
| `Asst_Phone` | `null \| string` |  |
| `Contact_Auto_Number` | `null \| string` |  |
| `Email_Opt_Out` | `null \| boolean` |  |
| `Home_Phone` | `null \| string` |  |
| `Last_Activity_Time` | `null \| string` |  |
| `Locked__s` | `null \| boolean` |  |
| `Other_Phone` | `null \| string` |  |
| `Record_Image` | `null \| string` |  |
| `Reporting_To` | `object \| any` |  |
| `Salutation` | `null \| string` |  |
| `Secondary_Email` | `null \| string` |  |
| `Skype_ID` | `null \| string` |  |
| `Tag` | `null \| array` |  |
| `Twitter` | `null \| string` |  |
| `Unsubscribed_Mode` | `null \| string` |  |
| `Unsubscribed_Time` | `null \| string` |  |
| `Vendor_Name` | `object \| any` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `more_records` | `boolean` |  |
| `page` | `integer` |  |

</details>

### Contacts Get

Get a single contact by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "contacts",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

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


### Contacts Context Store Search

Search and filter contacts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "contacts",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "id": "<str>"
        }
      }
    }
  }
}'
```

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
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
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
| `Account_Name` | `object` | Account the contact belongs to, as a lookup object with `name` and `id` |
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
| `data[].Account_Name` | `object` | Account the contact belongs to, as a lookup object with `name` and `id` |
| `data[].Lead_Source` | `string` | Source from which the contact was generated |
| `data[].Date_of_Birth` | `string` | Contact's date of birth |
| `data[].Mailing_City` | `string` | Mailing address city |
| `data[].Mailing_State` | `string` | Mailing address state or province |
| `data[].Mailing_Country` | `string` | Mailing address country |
| `data[].Description` | `string` | Description or notes about the contact |
| `data[].Created_Time` | `string` | Time the record was created |
| `data[].Modified_Time` | `string` | Time the record was last modified |

</details>

### Contacts Context Store SQL Query

Run a SQL query against contacts records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "contacts",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await zoho_crm.contacts.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contacts",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

### Contacts Semantic Search

Search contacts records by meaning rather than by exact or fuzzy field values. Semantic search embeds a natural-language `prompt` and returns the most similar passages, ranked by relevance. Pass `semantic={field, prompt, filter?, context_size?, min_similarity?, dedup?}` to `context_store_search` instead of `query`. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "contacts",
  "action": "context_store_search",
  "params": {
    "semantic": {"field": "Full_Name", "prompt": "<your natural-language query>"}
  }
}'
```

#### Python SDK

Semantic search is passed through the generic `execute` method — the typed `contacts.context_store_search` helper only accepts `query`.

```python
await zoho_crm.execute(
    "contacts",
    "context_store_search",
    {"semantic": {"field": "Full_Name", "prompt": "<your natural-language query>"}},
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
        "semantic": {"field": "Full_Name", "prompt": "<your natural-language query>"}
    }
}'
```

#### Semantic Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `semantic.field` | `string` | Yes | Field to search semantically. Mutually exclusive with `query`. |
| `semantic.prompt` | `string` | Yes | Natural-language query that is embedded and compared against stored passages. |
| `semantic.filter` | `object` | No | Filter conditions (same shape/operators as `query.filter`). `sort` is not supported — results are ranked by similarity. |
| `semantic.context_size` | `integer` | No | Characters of surrounding context to return per hit, up to the field's configured window. Omit to return the full configured window. |
| `semantic.min_similarity` | `number` | No | Minimum similarity score in [-1.0, 1.0]. Omit for 0.25; scores below the threshold are discarded before deduplication and top-k selection. Use -1.0 to disable the cutoff. |
| `semantic.dedup` | `string` | No | `max` (default) returns the single best-scoring passage per record; `none` returns multiple passages per record, still ranked by similarity and capped by `limit`. |
| `fields` | `array` | No | Field paths to include in results (dot notation for nested fields). Applied to each hit's `entity`. |
| `limit` | `integer` | No | Maximum results to return (default 10, maximum 100). |

#### Semantically Searchable Fields

| Field Name | Max Context (chars) | Description |
|------------|---------------------|-------------|
| `Full_Name` | 2048 | Contact's full name |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching passages |
| `data[].entity` | `object` | The matched source record |
| `data[].entity.id` | `string` | Source record field |
| `data[].entity.Modified_Time` | `string` | Source record field |
| `data[].entity.Created_Time` | `string` | Source record field |
| `data[].entity.Full_Name` | `string` | Source record field |
| `data[].entity.Title` | `string` | Source record field |
| `data[].entity.Department` | `string` | Source record field |
| `data[].entity.account_name` | `string` | Source record field |
| `data[].entity.Lead_Source` | `string` | Source record field |
| `data[].entity.Mailing_State` | `string` | Source record field |
| `data[].entity.Mailing_Country` | `string` | Source record field |
| `data[].metadata` | `object` | Match metadata |
| `data[].metadata.score` | `number` | Similarity score |
| `data[].metadata.context` | `string` | The matched passage text |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Accounts

### Accounts List

Returns a paginated list of accounts

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "accounts",
  "action": "list"
}'
```

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
| `$approval` | `null \| object` |  |
| `$approval_state` | `null \| string` |  |
| `$approved` | `null \| boolean` |  |
| `$currency_symbol` | `null \| string` |  |
| `$editable` | `null \| boolean` |  |
| `$field_states` | `null \| object` |  |
| `$in_merge` | `null \| boolean` |  |
| `$is_duplicate` | `null \| boolean` |  |
| `$layout_id` | `null \| object` |  |
| `$locked_for_me` | `null \| boolean` |  |
| `$orchestration` | `null \| boolean` |  |
| `$process_flow` | `null \| boolean` |  |
| `$review` | `null \| object` |  |
| `$review_process` | `null \| object` |  |
| `$state` | `null \| string` |  |
| `$zia_owner_assignment` | `null \| string` |  |
| `Account_Site` | `null \| string` |  |
| `Last_Activity_Time` | `null \| string` |  |
| `Locked__s` | `null \| boolean` |  |
| `Record_Image` | `null \| string` |  |
| `Tag` | `null \| array` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `more_records` | `boolean` |  |
| `page` | `integer` |  |

</details>

### Accounts Get

Get a single account by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "accounts",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

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


### Accounts Context Store Search

Search and filter accounts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "accounts",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "id": "<str>"
        }
      }
    }
  }
}'
```

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
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
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

### Accounts Context Store SQL Query

Run a SQL query against accounts records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "accounts",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await zoho_crm.accounts.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

### Accounts Semantic Search

Search accounts records by meaning rather than by exact or fuzzy field values. Semantic search embeds a natural-language `prompt` and returns the most similar passages, ranked by relevance. Pass `semantic={field, prompt, filter?, context_size?, min_similarity?, dedup?}` to `context_store_search` instead of `query`. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "accounts",
  "action": "context_store_search",
  "params": {
    "semantic": {"field": "Account_Name", "prompt": "<your natural-language query>"}
  }
}'
```

#### Python SDK

Semantic search is passed through the generic `execute` method — the typed `accounts.context_store_search` helper only accepts `query`.

```python
await zoho_crm.execute(
    "accounts",
    "context_store_search",
    {"semantic": {"field": "Account_Name", "prompt": "<your natural-language query>"}},
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
        "semantic": {"field": "Account_Name", "prompt": "<your natural-language query>"}
    }
}'
```

#### Semantic Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `semantic.field` | `string` | Yes | Field to search semantically. Mutually exclusive with `query`. |
| `semantic.prompt` | `string` | Yes | Natural-language query that is embedded and compared against stored passages. |
| `semantic.filter` | `object` | No | Filter conditions (same shape/operators as `query.filter`). `sort` is not supported — results are ranked by similarity. |
| `semantic.context_size` | `integer` | No | Characters of surrounding context to return per hit, up to the field's configured window. Omit to return the full configured window. |
| `semantic.min_similarity` | `number` | No | Minimum similarity score in [-1.0, 1.0]. Omit for 0.25; scores below the threshold are discarded before deduplication and top-k selection. Use -1.0 to disable the cutoff. |
| `semantic.dedup` | `string` | No | `max` (default) returns the single best-scoring passage per record; `none` returns multiple passages per record, still ranked by similarity and capped by `limit`. |
| `fields` | `array` | No | Field paths to include in results (dot notation for nested fields). Applied to each hit's `entity`. |
| `limit` | `integer` | No | Maximum results to return (default 10, maximum 100). |

#### Semantically Searchable Fields

| Field Name | Max Context (chars) | Description |
|------------|---------------------|-------------|
| `Account_Name` | 2048 | Name of the account or company |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching passages |
| `data[].entity` | `object` | The matched source record |
| `data[].entity.id` | `string` | Source record field |
| `data[].entity.Modified_Time` | `string` | Source record field |
| `data[].entity.Created_Time` | `string` | Source record field |
| `data[].entity.Account_Name` | `string` | Source record field |
| `data[].entity.Industry` | `string` | Source record field |
| `data[].entity.Account_Type` | `string` | Source record field |
| `data[].entity.Website` | `string` | Source record field |
| `data[].entity.Billing_State` | `string` | Source record field |
| `data[].entity.Billing_Country` | `string` | Source record field |
| `data[].metadata` | `object` | Match metadata |
| `data[].metadata.score` | `number` | Similarity score |
| `data[].metadata.context` | `string` | The matched passage text |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Deals

### Deals List

Returns a paginated list of deals

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "deals",
  "action": "list"
}'
```

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
| `$approval` | `null \| object` |  |
| `$approval_state` | `null \| string` |  |
| `$approved` | `null \| boolean` |  |
| `$currency_symbol` | `null \| string` |  |
| `$editable` | `null \| boolean` |  |
| `$field_states` | `null \| object` |  |
| `$followed` | `null \| boolean` |  |
| `$followers` | `null \| array` |  |
| `$in_merge` | `null \| boolean` |  |
| `$layout_id` | `null \| object` |  |
| `$locked_for_me` | `null \| boolean` |  |
| `$orchestration` | `null \| boolean` |  |
| `$process_flow` | `null \| boolean` |  |
| `$review` | `null \| object` |  |
| `$review_process` | `null \| object` |  |
| `$state` | `null \| string` |  |
| `$zia_owner_assignment` | `null \| string` |  |
| `Expected_Revenue` | `null \| number` |  |
| `Last_Activity_Time` | `null \| string` |  |
| `Lead_Conversion_Time` | `null \| integer` |  |
| `Locked__s` | `null \| boolean` |  |
| `Overall_Sales_Duration` | `null \| integer` |  |
| `Sales_Cycle_Duration` | `null \| integer` |  |
| `Tag` | `null \| array` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `more_records` | `boolean` |  |
| `page` | `integer` |  |

</details>

### Deals Get

Get a single deal by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "deals",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

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


### Deals Context Store Search

Search and filter deals records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "deals",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "id": "<str>"
        }
      }
    }
  }
}'
```

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
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
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
| `Account_Name` | `object` | Account the deal belongs to, as a lookup object with `name` and `id` |
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
| `data[].Account_Name` | `object` | Account the deal belongs to, as a lookup object with `name` and `id` |
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

### Deals Context Store SQL Query

Run a SQL query against deals records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "deals",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await zoho_crm.deals.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "deals",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

### Deals Semantic Search

Search deals records by meaning rather than by exact or fuzzy field values. Semantic search embeds a natural-language `prompt` and returns the most similar passages, ranked by relevance. Pass `semantic={field, prompt, filter?, context_size?, min_similarity?, dedup?}` to `context_store_search` instead of `query`. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "deals",
  "action": "context_store_search",
  "params": {
    "semantic": {"field": "Deal_Name", "prompt": "<your natural-language query>"}
  }
}'
```

#### Python SDK

Semantic search is passed through the generic `execute` method — the typed `deals.context_store_search` helper only accepts `query`.

```python
await zoho_crm.execute(
    "deals",
    "context_store_search",
    {"semantic": {"field": "Deal_Name", "prompt": "<your natural-language query>"}},
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
        "semantic": {"field": "Deal_Name", "prompt": "<your natural-language query>"}
    }
}'
```

#### Semantic Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `semantic.field` | `string` | Yes | Field to search semantically. Mutually exclusive with `query`. |
| `semantic.prompt` | `string` | Yes | Natural-language query that is embedded and compared against stored passages. |
| `semantic.filter` | `object` | No | Filter conditions (same shape/operators as `query.filter`). `sort` is not supported — results are ranked by similarity. |
| `semantic.context_size` | `integer` | No | Characters of surrounding context to return per hit, up to the field's configured window. Omit to return the full configured window. |
| `semantic.min_similarity` | `number` | No | Minimum similarity score in [-1.0, 1.0]. Omit for 0.25; scores below the threshold are discarded before deduplication and top-k selection. Use -1.0 to disable the cutoff. |
| `semantic.dedup` | `string` | No | `max` (default) returns the single best-scoring passage per record; `none` returns multiple passages per record, still ranked by similarity and capped by `limit`. |
| `fields` | `array` | No | Field paths to include in results (dot notation for nested fields). Applied to each hit's `entity`. |
| `limit` | `integer` | No | Maximum results to return (default 10, maximum 100). |

#### Semantically Searchable Fields

| Field Name | Max Context (chars) | Description |
|------------|---------------------|-------------|
| `Deal_Name` | 2048 | Name of the deal |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching passages |
| `data[].entity` | `object` | The matched source record |
| `data[].entity.id` | `string` | Source record field |
| `data[].entity.Modified_Time` | `string` | Source record field |
| `data[].entity.Created_Time` | `string` | Source record field |
| `data[].entity.Deal_Name` | `string` | Source record field |
| `data[].entity.Stage` | `string` | Source record field |
| `data[].entity.Type` | `string` | Source record field |
| `data[].entity.Closing_Date` | `string` | Source record field |
| `data[].entity.Lead_Source` | `string` | Source record field |
| `data[].entity.account_name` | `string` | Source record field |
| `data[].metadata` | `object` | Match metadata |
| `data[].metadata.score` | `number` | Similarity score |
| `data[].metadata.context` | `string` | The matched passage text |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Campaigns

### Campaigns List

Returns a paginated list of campaigns

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "campaigns",
  "action": "list"
}'
```

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
| `$approval` | `null \| object` |  |
| `$approval_state` | `null \| string` |  |
| `$approved` | `null \| boolean` |  |
| `$currency_symbol` | `null \| string` |  |
| `$editable` | `null \| boolean` |  |
| `$field_states` | `null \| object` |  |
| `$in_merge` | `null \| boolean` |  |
| `$layout_id` | `null \| object` |  |
| `$orchestration` | `null \| boolean` |  |
| `$process_flow` | `null \| boolean` |  |
| `$review` | `null \| object` |  |
| `$review_process` | `null \| object` |  |
| `$state` | `null \| string` |  |
| `Last_Activity_Time` | `null \| string` |  |
| `Parent_Campaign` | `object \| any` |  |
| `Tag` | `null \| array` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `more_records` | `boolean` |  |
| `page` | `integer` |  |

</details>

### Campaigns Get

Get a single campaign by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "campaigns",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

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

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "campaigns",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "id": "<str>"
        }
      }
    }
  }
}'
```

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
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
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

### Campaigns Context Store SQL Query

Run a SQL query against campaigns records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "campaigns",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await zoho_crm.campaigns.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

### Campaigns Semantic Search

Search campaigns records by meaning rather than by exact or fuzzy field values. Semantic search embeds a natural-language `prompt` and returns the most similar passages, ranked by relevance. Pass `semantic={field, prompt, filter?, context_size?, min_similarity?, dedup?}` to `context_store_search` instead of `query`. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "campaigns",
  "action": "context_store_search",
  "params": {
    "semantic": {"field": "Campaign_Name", "prompt": "<your natural-language query>"}
  }
}'
```

#### Python SDK

Semantic search is passed through the generic `execute` method — the typed `campaigns.context_store_search` helper only accepts `query`.

```python
await zoho_crm.execute(
    "campaigns",
    "context_store_search",
    {"semantic": {"field": "Campaign_Name", "prompt": "<your natural-language query>"}},
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
        "semantic": {"field": "Campaign_Name", "prompt": "<your natural-language query>"}
    }
}'
```

#### Semantic Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `semantic.field` | `string` | Yes | Field to search semantically. Mutually exclusive with `query`. |
| `semantic.prompt` | `string` | Yes | Natural-language query that is embedded and compared against stored passages. |
| `semantic.filter` | `object` | No | Filter conditions (same shape/operators as `query.filter`). `sort` is not supported — results are ranked by similarity. |
| `semantic.context_size` | `integer` | No | Characters of surrounding context to return per hit, up to the field's configured window. Omit to return the full configured window. |
| `semantic.min_similarity` | `number` | No | Minimum similarity score in [-1.0, 1.0]. Omit for 0.25; scores below the threshold are discarded before deduplication and top-k selection. Use -1.0 to disable the cutoff. |
| `semantic.dedup` | `string` | No | `max` (default) returns the single best-scoring passage per record; `none` returns multiple passages per record, still ranked by similarity and capped by `limit`. |
| `fields` | `array` | No | Field paths to include in results (dot notation for nested fields). Applied to each hit's `entity`. |
| `limit` | `integer` | No | Maximum results to return (default 10, maximum 100). |

#### Semantically Searchable Fields

| Field Name | Max Context (chars) | Description |
|------------|---------------------|-------------|
| `Campaign_Name` | 2048 | Name of the campaign |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching passages |
| `data[].entity` | `object` | The matched source record |
| `data[].entity.id` | `string` | Source record field |
| `data[].entity.Modified_Time` | `string` | Source record field |
| `data[].entity.Created_Time` | `string` | Source record field |
| `data[].entity.Campaign_Name` | `string` | Source record field |
| `data[].entity.Type` | `string` | Source record field |
| `data[].entity.Status` | `string` | Source record field |
| `data[].entity.Start_Date` | `string` | Source record field |
| `data[].entity.End_Date` | `string` | Source record field |
| `data[].metadata` | `object` | Match metadata |
| `data[].metadata.score` | `number` | Similarity score |
| `data[].metadata.context` | `string` | The matched passage text |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Tasks

### Tasks List

Returns a paginated list of tasks

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "tasks",
  "action": "list"
}'
```

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
| `$approval` | `null \| object` |  |
| `$approval_state` | `null \| string` |  |
| `$approved` | `null \| boolean` |  |
| `$currency_symbol` | `null \| string` |  |
| `$editable` | `null \| boolean` |  |
| `$field_states` | `null \| object` |  |
| `$in_merge` | `null \| boolean` |  |
| `$locked_for_me` | `null \| boolean` |  |
| `$orchestration` | `null \| boolean` |  |
| `$process_flow` | `null \| boolean` |  |
| `$review` | `null \| object` |  |
| `$review_process` | `null \| object` |  |
| `$se_module` | `null \| string` |  |
| `$state` | `null \| string` |  |
| `$u_id` | `null \| string` |  |
| `$zia_owner_assignment` | `null \| string` |  |
| `BEST_TIME` | `null \| array` |  |
| `Last_Activity_Time` | `null \| string` |  |
| `Locked__s` | `null \| boolean` |  |
| `Tag` | `null \| array` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `more_records` | `boolean` |  |
| `page` | `integer` |  |

</details>

### Tasks Get

Get a single task by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "tasks",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

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


### Tasks Context Store Search

Search and filter tasks records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "tasks",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "id": "<str>"
        }
      }
    }
  }
}'
```

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
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
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
| `Who_Id` | `object` | Contact or lead the task is with, as a lookup object with `name` and `id` |
| `What_Id` | `object` | Account, deal, or other record the task is linked to, as a lookup object with `name` and `id` |
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
| `data[].Who_Id` | `object` | Contact or lead the task is with, as a lookup object with `name` and `id` |
| `data[].What_Id` | `object` | Account, deal, or other record the task is linked to, as a lookup object with `name` and `id` |
| `data[].Due_Date` | `string` | Due date for the task |
| `data[].Status` | `string` | Current status (e.g., Not Started, In Progress, Completed) |
| `data[].Priority` | `string` | Priority level (e.g., High, Highest, Low, Lowest, Normal) |
| `data[].Send_Notification_Email` | `boolean` | Whether to send a notification email |
| `data[].Description` | `string` | Description or notes about the task |
| `data[].Created_Time` | `string` | Time the record was created |
| `data[].Modified_Time` | `string` | Time the record was last modified |
| `data[].Closed_Time` | `string` | Time the task was closed |

</details>

### Tasks Context Store SQL Query

Run a SQL query against tasks records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "tasks",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await zoho_crm.tasks.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

### Tasks Semantic Search

Search tasks records by meaning rather than by exact or fuzzy field values. Semantic search embeds a natural-language `prompt` and returns the most similar passages, ranked by relevance. Pass `semantic={field, prompt, filter?, context_size?, min_similarity?, dedup?}` to `context_store_search` instead of `query`. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "tasks",
  "action": "context_store_search",
  "params": {
    "semantic": {"field": "Subject", "prompt": "<your natural-language query>"}
  }
}'
```

#### Python SDK

Semantic search is passed through the generic `execute` method — the typed `tasks.context_store_search` helper only accepts `query`.

```python
await zoho_crm.execute(
    "tasks",
    "context_store_search",
    {"semantic": {"field": "Subject", "prompt": "<your natural-language query>"}},
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
        "semantic": {"field": "Subject", "prompt": "<your natural-language query>"}
    }
}'
```

#### Semantic Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `semantic.field` | `string` | Yes | Field to search semantically. Mutually exclusive with `query`. |
| `semantic.prompt` | `string` | Yes | Natural-language query that is embedded and compared against stored passages. |
| `semantic.filter` | `object` | No | Filter conditions (same shape/operators as `query.filter`). `sort` is not supported — results are ranked by similarity. |
| `semantic.context_size` | `integer` | No | Characters of surrounding context to return per hit, up to the field's configured window. Omit to return the full configured window. |
| `semantic.min_similarity` | `number` | No | Minimum similarity score in [-1.0, 1.0]. Omit for 0.25; scores below the threshold are discarded before deduplication and top-k selection. Use -1.0 to disable the cutoff. |
| `semantic.dedup` | `string` | No | `max` (default) returns the single best-scoring passage per record; `none` returns multiple passages per record, still ranked by similarity and capped by `limit`. |
| `fields` | `array` | No | Field paths to include in results (dot notation for nested fields). Applied to each hit's `entity`. |
| `limit` | `integer` | No | Maximum results to return (default 10, maximum 100). |

#### Semantically Searchable Fields

| Field Name | Max Context (chars) | Description |
|------------|---------------------|-------------|
| `Subject` | 2048 | Subject or title of the task |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching passages |
| `data[].entity` | `object` | The matched source record |
| `data[].entity.id` | `string` | Source record field |
| `data[].entity.Modified_Time` | `string` | Source record field |
| `data[].entity.Created_Time` | `string` | Source record field |
| `data[].entity.Subject` | `string` | Source record field |
| `data[].entity.Status` | `string` | Source record field |
| `data[].entity.Priority` | `string` | Source record field |
| `data[].entity.Due_Date` | `string` | Source record field |
| `data[].entity.Closed_Time` | `string` | Source record field |
| `data[].entity.related_to` | `string` | Source record field |
| `data[].entity.contact_name` | `string` | Source record field |
| `data[].metadata` | `object` | Match metadata |
| `data[].metadata.score` | `number` | Similarity score |
| `data[].metadata.context` | `string` | The matched passage text |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Events

### Events List

Returns a paginated list of events (meetings/calendar events)

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "events",
  "action": "list"
}'
```

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
| `Venue` | `null \| string` |  |
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
| `$approval` | `null \| object` |  |
| `$approval_state` | `null \| string` |  |
| `$approved` | `null \| boolean` |  |
| `$calendar_booking_event` | `null \| boolean` |  |
| `$currency_symbol` | `null \| string` |  |
| `$editable` | `null \| boolean` |  |
| `$field_states` | `null \| object` |  |
| `$in_merge` | `null \| boolean` |  |
| `$meeting_details` | `null \| object` |  |
| `$orchestration` | `null \| boolean` |  |
| `$process_flow` | `null \| boolean` |  |
| `$recurrence_id` | `null \| string` |  |
| `$review` | `null \| object` |  |
| `$review_process` | `null \| object` |  |
| `$se_module` | `null \| string` |  |
| `$send_notification` | `null \| boolean` |  |
| `$state` | `null \| string` |  |
| `$u_id` | `null \| string` |  |
| `Check_In_Address` | `null \| string` |  |
| `Check_In_By` | `null \| object` |  |
| `Check_In_City` | `null \| string` |  |
| `Check_In_Comment` | `null \| string` |  |
| `Check_In_Country` | `null \| string` |  |
| `Check_In_State` | `null \| string` |  |
| `Check_In_Status` | `null \| string` |  |
| `Check_In_Sub_Locality` | `null \| string` |  |
| `Check_In_Time` | `null \| string` |  |
| `Last_Activity_Time` | `null \| string` |  |
| `Latitude` | `null \| number` |  |
| `Longitude` | `null \| number` |  |
| `Tag` | `null \| array` |  |
| `ZIP_Code` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `more_records` | `boolean` |  |
| `page` | `integer` |  |

</details>

### Events Get

Get a single event by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "events",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

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

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "events",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "id": "<str>"
        }
      }
    }
  }
}'
```

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
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
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
| `Who_Id` | `object` | Contact or lead invited to the event, as a lookup object with `name` and `id` |
| `What_Id` | `object` | Account, deal, or other record the event is linked to, as a lookup object with `name` and `id` |
| `Start_DateTime` | `string` | Event start date and time |
| `End_DateTime` | `string` | Event end date and time |
| `All_day` | `boolean` | Whether this is an all-day event |
| `Venue` | `string` | Event location. Zoho names this field `Venue`; there is no `Location` field on the Events module.
 |
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
| `data[].Who_Id` | `object` | Contact or lead invited to the event, as a lookup object with `name` and `id` |
| `data[].What_Id` | `object` | Account, deal, or other record the event is linked to, as a lookup object with `name` and `id` |
| `data[].Start_DateTime` | `string` | Event start date and time |
| `data[].End_DateTime` | `string` | Event end date and time |
| `data[].All_day` | `boolean` | Whether this is an all-day event |
| `data[].Venue` | `string` | Event location. Zoho names this field `Venue`; there is no `Location` field on the Events module.
 |
| `data[].Description` | `string` | Description or notes about the event |
| `data[].Created_Time` | `string` | Time the record was created |
| `data[].Modified_Time` | `string` | Time the record was last modified |

</details>

### Events Context Store SQL Query

Run a SQL query against events records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "events",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await zoho_crm.events.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "events",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

### Events Semantic Search

Search events records by meaning rather than by exact or fuzzy field values. Semantic search embeds a natural-language `prompt` and returns the most similar passages, ranked by relevance. Pass `semantic={field, prompt, filter?, context_size?, min_similarity?, dedup?}` to `context_store_search` instead of `query`. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "events",
  "action": "context_store_search",
  "params": {
    "semantic": {"field": "Event_Title", "prompt": "<your natural-language query>"}
  }
}'
```

#### Python SDK

Semantic search is passed through the generic `execute` method — the typed `events.context_store_search` helper only accepts `query`.

```python
await zoho_crm.execute(
    "events",
    "context_store_search",
    {"semantic": {"field": "Event_Title", "prompt": "<your natural-language query>"}},
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
        "semantic": {"field": "Event_Title", "prompt": "<your natural-language query>"}
    }
}'
```

#### Semantic Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `semantic.field` | `string` | Yes | Field to search semantically. Mutually exclusive with `query`. |
| `semantic.prompt` | `string` | Yes | Natural-language query that is embedded and compared against stored passages. |
| `semantic.filter` | `object` | No | Filter conditions (same shape/operators as `query.filter`). `sort` is not supported — results are ranked by similarity. |
| `semantic.context_size` | `integer` | No | Characters of surrounding context to return per hit, up to the field's configured window. Omit to return the full configured window. |
| `semantic.min_similarity` | `number` | No | Minimum similarity score in [-1.0, 1.0]. Omit for 0.25; scores below the threshold are discarded before deduplication and top-k selection. Use -1.0 to disable the cutoff. |
| `semantic.dedup` | `string` | No | `max` (default) returns the single best-scoring passage per record; `none` returns multiple passages per record, still ranked by similarity and capped by `limit`. |
| `fields` | `array` | No | Field paths to include in results (dot notation for nested fields). Applied to each hit's `entity`. |
| `limit` | `integer` | No | Maximum results to return (default 10, maximum 100). |

#### Semantically Searchable Fields

| Field Name | Max Context (chars) | Description |
|------------|---------------------|-------------|
| `Event_Title` | 2048 | Title of the event |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching passages |
| `data[].entity` | `object` | The matched source record |
| `data[].entity.id` | `string` | Source record field |
| `data[].entity.Modified_Time` | `string` | Source record field |
| `data[].entity.Created_Time` | `string` | Source record field |
| `data[].entity.Event_Title` | `string` | Source record field |
| `data[].entity.Start_DateTime` | `string` | Source record field |
| `data[].entity.End_DateTime` | `string` | Source record field |
| `data[].entity.All_day` | `string` | Source record field |
| `data[].entity.Venue` | `string` | Source record field |
| `data[].entity.related_to` | `string` | Source record field |
| `data[].entity.contact_name` | `string` | Source record field |
| `data[].metadata` | `object` | Match metadata |
| `data[].metadata.score` | `number` | Similarity score |
| `data[].metadata.context` | `string` | The matched passage text |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Calls

### Calls List

Returns a paginated list of calls

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "calls",
  "action": "list"
}'
```

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
| `Call_Status` | `null \| string` |  |
| `Call_Agenda` | `null \| string` |  |
| `Created_Time` | `null \| string` |  |
| `Modified_Time` | `null \| string` |  |
| `Created_By` | `object \| any` |  |
| `Modified_By` | `object \| any` |  |
| `Record_Status__s` | `null \| string` |  |
| `$approval` | `null \| object` |  |
| `$approval_state` | `null \| string` |  |
| `$approved` | `null \| boolean` |  |
| `$calendar_booking_call` | `null \| boolean` |  |
| `$currency_symbol` | `null \| string` |  |
| `$editable` | `null \| boolean` |  |
| `$field_states` | `null \| object` |  |
| `$in_merge` | `null \| boolean` |  |
| `$orchestration` | `null \| boolean` |  |
| `$process_flow` | `null \| boolean` |  |
| `$review` | `null \| object` |  |
| `$review_process` | `null \| object` |  |
| `$se_module` | `null \| string` |  |
| `$state` | `null \| string` |  |
| `Dialled_Number` | `null \| string` |  |
| `Last_Activity_Time` | `null \| string` |  |
| `Reminder` | `null \| string` |  |
| `Tag` | `null \| array` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `more_records` | `boolean` |  |
| `page` | `integer` |  |

</details>

### Calls Get

Get a single call by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "calls",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

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

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "calls",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "id": "<str>"
        }
      }
    }
  }
}'
```

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
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
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
| `Who_Id` | `object` | Contact or lead on the call, as a lookup object with `name` and `id` |
| `What_Id` | `object` | Account, deal, or other record the call is linked to, as a lookup object with `name` and `id` |
| `Call_Type` | `string` | Type of call (Inbound or Outbound) |
| `Call_Start_Time` | `string` | Start time of the call |
| `Call_Duration` | `string` | Duration of the call as a formatted string |
| `Call_Duration_in_seconds` | `number` | Duration of the call in seconds |
| `Call_Purpose` | `string` | Purpose of the call |
| `Call_Result` | `string` | Result or outcome of the call |
| `Caller_ID` | `string` | Caller ID number |
| `Call_Status` | `string` | Disposition of the call (Missed, Received, Overdue, Scheduled). Zoho names this field `Call_Status`; there is no `Outgoing_Call_Status` field on the Calls module.
 |
| `Call_Agenda` | `string` | Free-text agenda written before the call |
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
| `data[].Who_Id` | `object` | Contact or lead on the call, as a lookup object with `name` and `id` |
| `data[].What_Id` | `object` | Account, deal, or other record the call is linked to, as a lookup object with `name` and `id` |
| `data[].Call_Type` | `string` | Type of call (Inbound or Outbound) |
| `data[].Call_Start_Time` | `string` | Start time of the call |
| `data[].Call_Duration` | `string` | Duration of the call as a formatted string |
| `data[].Call_Duration_in_seconds` | `number` | Duration of the call in seconds |
| `data[].Call_Purpose` | `string` | Purpose of the call |
| `data[].Call_Result` | `string` | Result or outcome of the call |
| `data[].Caller_ID` | `string` | Caller ID number |
| `data[].Call_Status` | `string` | Disposition of the call (Missed, Received, Overdue, Scheduled). Zoho names this field `Call_Status`; there is no `Outgoing_Call_Status` field on the Calls module.
 |
| `data[].Call_Agenda` | `string` | Free-text agenda written before the call |
| `data[].Description` | `string` | Description or notes about the call |
| `data[].Created_Time` | `string` | Time the record was created |
| `data[].Modified_Time` | `string` | Time the record was last modified |

</details>

### Calls Context Store SQL Query

Run a SQL query against calls records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "calls",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await zoho_crm.calls.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "calls",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

### Calls Semantic Search

Search calls records by meaning rather than by exact or fuzzy field values. Semantic search embeds a natural-language `prompt` and returns the most similar passages, ranked by relevance. Pass `semantic={field, prompt, filter?, context_size?, min_similarity?, dedup?}` to `context_store_search` instead of `query`. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "calls",
  "action": "context_store_search",
  "params": {
    "semantic": {"field": "Subject", "prompt": "<your natural-language query>"}
  }
}'
```

#### Python SDK

Semantic search is passed through the generic `execute` method — the typed `calls.context_store_search` helper only accepts `query`.

```python
await zoho_crm.execute(
    "calls",
    "context_store_search",
    {"semantic": {"field": "Subject", "prompt": "<your natural-language query>"}},
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
        "semantic": {"field": "Subject", "prompt": "<your natural-language query>"}
    }
}'
```

#### Semantic Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `semantic.field` | `string` | Yes | Field to search semantically. Mutually exclusive with `query`. |
| `semantic.prompt` | `string` | Yes | Natural-language query that is embedded and compared against stored passages. |
| `semantic.filter` | `object` | No | Filter conditions (same shape/operators as `query.filter`). `sort` is not supported — results are ranked by similarity. |
| `semantic.context_size` | `integer` | No | Characters of surrounding context to return per hit, up to the field's configured window. Omit to return the full configured window. |
| `semantic.min_similarity` | `number` | No | Minimum similarity score in [-1.0, 1.0]. Omit for 0.25; scores below the threshold are discarded before deduplication and top-k selection. Use -1.0 to disable the cutoff. |
| `semantic.dedup` | `string` | No | `max` (default) returns the single best-scoring passage per record; `none` returns multiple passages per record, still ranked by similarity and capped by `limit`. |
| `fields` | `array` | No | Field paths to include in results (dot notation for nested fields). Applied to each hit's `entity`. |
| `limit` | `integer` | No | Maximum results to return (default 10, maximum 100). |

#### Semantically Searchable Fields

| Field Name | Max Context (chars) | Description |
|------------|---------------------|-------------|
| `Subject` | 2048 | Subject of the call |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching passages |
| `data[].entity` | `object` | The matched source record |
| `data[].entity.id` | `string` | Source record field |
| `data[].entity.Modified_Time` | `string` | Source record field |
| `data[].entity.Created_Time` | `string` | Source record field |
| `data[].entity.Subject` | `string` | Source record field |
| `data[].entity.Call_Type` | `string` | Source record field |
| `data[].entity.Call_Status` | `string` | Source record field |
| `data[].entity.Call_Purpose` | `string` | Source record field |
| `data[].entity.Call_Start_Time` | `string` | Source record field |
| `data[].entity.related_to` | `string` | Source record field |
| `data[].entity.contact_name` | `string` | Source record field |
| `data[].metadata` | `object` | Match metadata |
| `data[].metadata.score` | `number` | Similarity score |
| `data[].metadata.context` | `string` | The matched passage text |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Products

### Products List

Returns a paginated list of products

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "products",
  "action": "list"
}'
```

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
| `$approval` | `null \| object` |  |
| `$approval_state` | `null \| string` |  |
| `$approved` | `null \| boolean` |  |
| `$currency_symbol` | `null \| string` |  |
| `$editable` | `null \| boolean` |  |
| `$field_states` | `null \| object` |  |
| `$in_merge` | `null \| boolean` |  |
| `$layout_id` | `null \| object` |  |
| `$locked_for_me` | `null \| boolean` |  |
| `$orchestration` | `null \| boolean` |  |
| `$process_flow` | `null \| boolean` |  |
| `$review` | `null \| object` |  |
| `$review_process` | `null \| object` |  |
| `$state` | `null \| string` |  |
| `Last_Activity_Time` | `null \| string` |  |
| `Locked__s` | `null \| boolean` |  |
| `Record_Image` | `null \| string` |  |
| `Tag` | `null \| array` |  |
| `Taxable` | `null \| boolean` |  |
| `Usage_Unit` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `more_records` | `boolean` |  |
| `page` | `integer` |  |

</details>

### Products Get

Get a single product by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "products",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

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

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "products",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "id": "<str>"
        }
      }
    }
  }
}'
```

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
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
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

### Products Context Store SQL Query

Run a SQL query against products records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "products",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await zoho_crm.products.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "products",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

### Products Semantic Search

Search products records by meaning rather than by exact or fuzzy field values. Semantic search embeds a natural-language `prompt` and returns the most similar passages, ranked by relevance. Pass `semantic={field, prompt, filter?, context_size?, min_similarity?, dedup?}` to `context_store_search` instead of `query`. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "products",
  "action": "context_store_search",
  "params": {
    "semantic": {"field": "Product_Name", "prompt": "<your natural-language query>"}
  }
}'
```

#### Python SDK

Semantic search is passed through the generic `execute` method — the typed `products.context_store_search` helper only accepts `query`.

```python
await zoho_crm.execute(
    "products",
    "context_store_search",
    {"semantic": {"field": "Product_Name", "prompt": "<your natural-language query>"}},
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
        "semantic": {"field": "Product_Name", "prompt": "<your natural-language query>"}
    }
}'
```

#### Semantic Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `semantic.field` | `string` | Yes | Field to search semantically. Mutually exclusive with `query`. |
| `semantic.prompt` | `string` | Yes | Natural-language query that is embedded and compared against stored passages. |
| `semantic.filter` | `object` | No | Filter conditions (same shape/operators as `query.filter`). `sort` is not supported — results are ranked by similarity. |
| `semantic.context_size` | `integer` | No | Characters of surrounding context to return per hit, up to the field's configured window. Omit to return the full configured window. |
| `semantic.min_similarity` | `number` | No | Minimum similarity score in [-1.0, 1.0]. Omit for 0.25; scores below the threshold are discarded before deduplication and top-k selection. Use -1.0 to disable the cutoff. |
| `semantic.dedup` | `string` | No | `max` (default) returns the single best-scoring passage per record; `none` returns multiple passages per record, still ranked by similarity and capped by `limit`. |
| `fields` | `array` | No | Field paths to include in results (dot notation for nested fields). Applied to each hit's `entity`. |
| `limit` | `integer` | No | Maximum results to return (default 10, maximum 100). |

#### Semantically Searchable Fields

| Field Name | Max Context (chars) | Description |
|------------|---------------------|-------------|
| `Product_Name` | 2048 | Name of the product |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching passages |
| `data[].entity` | `object` | The matched source record |
| `data[].entity.id` | `string` | Source record field |
| `data[].entity.Modified_Time` | `string` | Source record field |
| `data[].entity.Created_Time` | `string` | Source record field |
| `data[].entity.Product_Name` | `string` | Source record field |
| `data[].entity.Product_Code` | `string` | Source record field |
| `data[].entity.Product_Category` | `string` | Source record field |
| `data[].entity.Manufacturer` | `string` | Source record field |
| `data[].entity.Product_Active` | `string` | Source record field |
| `data[].metadata` | `object` | Match metadata |
| `data[].metadata.score` | `number` | Similarity score |
| `data[].metadata.context` | `string` | The matched passage text |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Quotes

### Quotes List

Returns a paginated list of quotes

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "quotes",
  "action": "list"
}'
```

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
| `$approval` | `null \| object` |  |
| `$approval_state` | `null \| string` |  |
| `$approved` | `null \| boolean` |  |
| `$converted` | `null \| boolean` |  |
| `$currency_symbol` | `null \| string` |  |
| `$editable` | `null \| boolean` |  |
| `$field_states` | `null \| object` |  |
| `$in_merge` | `null \| boolean` |  |
| `$layout_id` | `null \| object` |  |
| `$line_tax` | `null \| array` |  |
| `$locked_for_me` | `null \| boolean` |  |
| `$orchestration` | `null \| boolean` |  |
| `$process_flow` | `null \| boolean` |  |
| `$review` | `null \| object` |  |
| `$review_process` | `null \| object` |  |
| `$state` | `null \| string` |  |
| `Last_Activity_Time` | `null \| string` |  |
| `Locked__s` | `null \| boolean` |  |
| `Product_Details` | `null \| array` |  |
| `Quote_Number` | `null \| string` |  |
| `Tag` | `null \| array` |  |
| `Team` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `more_records` | `boolean` |  |
| `page` | `integer` |  |

</details>

### Quotes Get

Get a single quote by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "quotes",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

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

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "quotes",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "id": "<str>"
        }
      }
    }
  }
}'
```

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
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
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

### Quotes Context Store SQL Query

Run a SQL query against quotes records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "quotes",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await zoho_crm.quotes.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "quotes",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Invoices

### Invoices List

Returns a paginated list of invoices

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "invoices",
  "action": "list"
}'
```

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
| `$approval` | `null \| object` |  |
| `$approval_state` | `null \| string` |  |
| `$approved` | `null \| boolean` |  |
| `$currency_symbol` | `null \| string` |  |
| `$editable` | `null \| boolean` |  |
| `$field_states` | `null \| object` |  |
| `$in_merge` | `null \| boolean` |  |
| `$layout_id` | `null \| object` |  |
| `$line_tax` | `null \| array` |  |
| `$locked_for_me` | `null \| boolean` |  |
| `$orchestration` | `null \| boolean` |  |
| `$process_flow` | `null \| boolean` |  |
| `$review` | `null \| object` |  |
| `$review_process` | `null \| object` |  |
| `$state` | `null \| string` |  |
| `Last_Activity_Time` | `null \| string` |  |
| `Locked__s` | `null \| boolean` |  |
| `Product_Details` | `null \| array` |  |
| `Sales_Commission` | `null \| number` |  |
| `Tag` | `null \| array` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `more_records` | `boolean` |  |
| `page` | `integer` |  |

</details>

### Invoices Get

Get a single invoice by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "invoices",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

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

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "invoices",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "id": "<str>"
        }
      }
    }
  }
}'
```

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
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
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

### Invoices Context Store SQL Query

Run a SQL query against invoices records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "invoices",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await zoho_crm.invoices.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "invoices",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Notes

### Notes List

Returns a paginated list of notes

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "notes",
  "action": "list"
}'
```

#### Python SDK

```python
await zoho_crm.notes.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "notes",
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
| `Note_Title` | `null \| string` |  |
| `Note_Content` | `null \| string` |  |
| `Parent_Id` | `object \| any` |  |
| `Created_Time` | `null \| string` |  |
| `Modified_Time` | `null \| string` |  |
| `$attachments` | `null \| array` |  |
| `$editable` | `null \| boolean` |  |
| `$field_states` | `null \| object` |  |
| `$is_shared_to_client` | `null \| boolean` |  |
| `$se_module` | `null \| string` |  |
| `$size` | `null \| integer` |  |
| `$state` | `null \| string` |  |
| `$voice_note` | `null \| boolean` |  |
| `Created_By` | `object \| any` |  |
| `Modified_By` | `object \| any` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `more_records` | `boolean` |  |
| `page` | `integer` |  |

</details>

### Notes Get

Get a single note by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "notes",
  "action": "get",
  "params": {
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await zoho_crm.notes.get(
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
| `id` | `string` | Yes | Note ID |


### Notes Context Store Search

Search and filter notes records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "notes",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "id": "<str>"
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await zoho_crm.notes.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "notes",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Unique record identifier |
| `Note_Content` | `string` | Body of the note. This is where rep-authored free text actually accumulates in Zoho CRM -- notes attach to any module record and, unlike the per-record `Description` textarea, are mandatory content by construction.
 |
| `Note_Title` | `string` | Optional short title for the note |
| `Parent_Id` | `object` | Record the note is attached to, as a lookup object with `name` and `id` |
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
| `data[].Note_Content` | `string` | Body of the note. This is where rep-authored free text actually accumulates in Zoho CRM -- notes attach to any module record and, unlike the per-record `Description` textarea, are mandatory content by construction.
 |
| `data[].Note_Title` | `string` | Optional short title for the note |
| `data[].Parent_Id` | `object` | Record the note is attached to, as a lookup object with `name` and `id` |
| `data[].Created_Time` | `string` | Time the record was created |
| `data[].Modified_Time` | `string` | Time the record was last modified |

</details>

### Notes Context Store SQL Query

Run a SQL query against notes records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "notes",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await zoho_crm.notes.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "notes",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

### Notes Semantic Search

Search notes records by meaning rather than by exact or fuzzy field values. Semantic search embeds a natural-language `prompt` and returns the most similar passages, ranked by relevance. Pass `semantic={field, prompt, filter?, context_size?, min_similarity?, dedup?}` to `context_store_search` instead of `query`. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "notes",
  "action": "context_store_search",
  "params": {
    "semantic": {"field": "Note_Content", "prompt": "<your natural-language query>"}
  }
}'
```

#### Python SDK

Semantic search is passed through the generic `execute` method — the typed `notes.context_store_search` helper only accepts `query`.

```python
await zoho_crm.execute(
    "notes",
    "context_store_search",
    {"semantic": {"field": "Note_Content", "prompt": "<your natural-language query>"}},
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "notes",
    "action": "context_store_search",
    "params": {
        "semantic": {"field": "Note_Content", "prompt": "<your natural-language query>"}
    }
}'
```

#### Semantic Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `semantic.field` | `string` | Yes | Field to search semantically. Mutually exclusive with `query`. |
| `semantic.prompt` | `string` | Yes | Natural-language query that is embedded and compared against stored passages. |
| `semantic.filter` | `object` | No | Filter conditions (same shape/operators as `query.filter`). `sort` is not supported — results are ranked by similarity. |
| `semantic.context_size` | `integer` | No | Characters of surrounding context to return per hit, up to the field's configured window. Omit to return the full configured window. |
| `semantic.min_similarity` | `number` | No | Minimum similarity score in [-1.0, 1.0]. Omit for 0.25; scores below the threshold are discarded before deduplication and top-k selection. Use -1.0 to disable the cutoff. |
| `semantic.dedup` | `string` | No | `max` (default) returns the single best-scoring passage per record; `none` returns multiple passages per record, still ranked by similarity and capped by `limit`. |
| `fields` | `array` | No | Field paths to include in results (dot notation for nested fields). Applied to each hit's `entity`. |
| `limit` | `integer` | No | Maximum results to return (default 10, maximum 100). |

#### Semantically Searchable Fields

| Field Name | Max Context (chars) | Description |
|------------|---------------------|-------------|
| `Note_Content` | 2048 | Body of the note. This is where rep-authored free text actually accumulates in Zoho CRM -- notes attach to any module record and, unlike the per-record `Description` textarea, are mandatory content by construction.
 |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching passages |
| `data[].entity` | `object` | The matched source record |
| `data[].entity.id` | `string` | Source record field |
| `data[].entity.Modified_Time` | `string` | Source record field |
| `data[].entity.Created_Time` | `string` | Source record field |
| `data[].entity.Note_Title` | `string` | Source record field |
| `data[].entity.parent_id` | `string` | Source record field |
| `data[].entity.parent_name` | `string` | Source record field |
| `data[].metadata` | `object` | Match metadata |
| `data[].metadata.score` | `number` | Similarity score |
| `data[].metadata.context` | `string` | The matched passage text |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

