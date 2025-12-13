# Salesforce

## Supported Entities and Actions

| Entity | Actions |
|--------|---------|
| Accounts | [List](#accounts-list), [Get](#accounts-get), [Search](#accounts-search) |
| Contacts | [List](#contacts-list), [Get](#contacts-get), [Search](#contacts-search) |
| Leads | [List](#leads-list), [Get](#leads-get), [Search](#leads-search) |
| Opportunities | [List](#opportunities-list), [Get](#opportunities-get), [Search](#opportunities-search) |
| Tasks | [List](#tasks-list), [Get](#tasks-get), [Search](#tasks-search) |
| Events | [List](#events-list), [Get](#events-get), [Search](#events-search) |
| Campaigns | [List](#campaigns-list), [Get](#campaigns-get), [Search](#campaigns-search) |
| Cases | [List](#cases-list), [Get](#cases-get), [Search](#cases-search) |
| Notes | [List](#notes-list), [Get](#notes-get), [Search](#notes-search) |
| Content Versions | [List](#content-versions-list), [Get](#content-versions-get), [Download](#content-versions-download) |
| Attachments | [List](#attachments-list), [Get](#attachments-get), [Download](#attachments-download) |
| Query | [List](#query-list) |

### Accounts

#### Accounts List

Returns a list of accounts via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


**Python SDK**

```python
salesforce.accounts.list(
    q="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query for accounts. Default returns up to 200 records.
To change the limit, provide your own query with a LIMIT clause.
Example: "SELECT FIELDS(STANDARD) FROM Account ORDER BY LastModifiedDate DESC LIMIT 50"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `totalSize` | `integer` |  |
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |
| `records` | `array<object>` |  |
| `records[].Id` | `string` |  |
| `records[].Name` | `string` |  |
| `records[].attributes` | `object` |  |


</details>

#### Accounts Get

Get a single account by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


**Python SDK**

```python
salesforce.accounts.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce Account ID (18-character ID starting with '001') |
| `fields` | `string` | No | Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
Example: "Id,Name,Industry,AnnualRevenue,Website"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Name` | `string` |  |
| `attributes` | `object` |  |


</details>

#### Accounts Search

Search for accounts using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields and objects.
Use SOQL (list action) for structured queries with specific field conditions.


**Python SDK**

```python
salesforce.accounts.search(
    q="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "search",
    "params": {
        "q": "<str>"
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOSL search query. Format: FIND {searchTerm} IN scope RETURNING Object(fields) [LIMIT n]
Examples:
- "FIND {Acme} IN ALL FIELDS RETURNING Account(Id,Name)"
- "FIND {tech*} IN NAME FIELDS RETURNING Account(Id,Name,Industry) LIMIT 50"
- "FIND {\"exact phrase\"} RETURNING Account(Id,Name,Website)"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `searchRecords` | `array<object>` |  |


</details>

### Contacts

#### Contacts List

Returns a list of contacts via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


**Python SDK**

```python
salesforce.contacts.list(
    q="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query for contacts. Default returns up to 200 records.
To change the limit, provide your own query with a LIMIT clause.
Example: "SELECT FIELDS(STANDARD) FROM Contact WHERE AccountId = '001xx...' LIMIT 50"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `totalSize` | `integer` |  |
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |
| `records` | `array<object>` |  |
| `records[].Id` | `string` |  |
| `records[].Name` | `string` |  |
| `records[].attributes` | `object` |  |


</details>

#### Contacts Get

Get a single contact by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


**Python SDK**

```python
salesforce.contacts.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce Contact ID (18-character ID starting with '003') |
| `fields` | `string` | No | Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
Example: "Id,FirstName,LastName,Email,Phone,AccountId"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Name` | `string` |  |
| `attributes` | `object` |  |


</details>

#### Contacts Search

Search for contacts using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields.


**Python SDK**

```python
salesforce.contacts.search(
    q="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contacts",
    "action": "search",
    "params": {
        "q": "<str>"
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOSL search query. Format: FIND {searchTerm} RETURNING Contact(fields) [LIMIT n]
Examples:
- "FIND {John} IN NAME FIELDS RETURNING Contact(Id,FirstName,LastName,Email)"
- "FIND {*@example.com} IN EMAIL FIELDS RETURNING Contact(Id,Name,Email) LIMIT 25"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `searchRecords` | `array<object>` |  |


</details>

### Leads

#### Leads List

Returns a list of leads via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


**Python SDK**

```python
salesforce.leads.list(
    q="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query for leads. Default returns up to 200 records.
To change the limit, provide your own query with a LIMIT clause.
Example: "SELECT FIELDS(STANDARD) FROM Lead WHERE Status = 'Open' LIMIT 100"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `totalSize` | `integer` |  |
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |
| `records` | `array<object>` |  |
| `records[].Id` | `string` |  |
| `records[].Name` | `string` |  |
| `records[].attributes` | `object` |  |


</details>

#### Leads Get

Get a single lead by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


**Python SDK**

```python
salesforce.leads.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce Lead ID (18-character ID starting with '00Q') |
| `fields` | `string` | No | Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
Example: "Id,FirstName,LastName,Email,Company,Status,LeadSource"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Name` | `string` |  |
| `attributes` | `object` |  |


</details>

#### Leads Search

Search for leads using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields.


**Python SDK**

```python
salesforce.leads.search(
    q="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "leads",
    "action": "search",
    "params": {
        "q": "<str>"
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOSL search query. Format: FIND {searchTerm} RETURNING Lead(fields) [LIMIT n]
Examples:
- "FIND {Smith} IN NAME FIELDS RETURNING Lead(Id,FirstName,LastName,Company,Status)"
- "FIND {marketing} IN ALL FIELDS RETURNING Lead(Id,Name,LeadSource) LIMIT 50"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `searchRecords` | `array<object>` |  |


</details>

### Opportunities

#### Opportunities List

Returns a list of opportunities via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


**Python SDK**

```python
salesforce.opportunities.list(
    q="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query for opportunities. Default returns up to 200 records.
To change the limit, provide your own query with a LIMIT clause.
Example: "SELECT FIELDS(STANDARD) FROM Opportunity WHERE StageName = 'Closed Won' LIMIT 50"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `totalSize` | `integer` |  |
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |
| `records` | `array<object>` |  |
| `records[].Id` | `string` |  |
| `records[].Name` | `string` |  |
| `records[].attributes` | `object` |  |


</details>

#### Opportunities Get

Get a single opportunity by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


**Python SDK**

```python
salesforce.opportunities.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce Opportunity ID (18-character ID starting with '006') |
| `fields` | `string` | No | Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
Example: "Id,Name,Amount,StageName,CloseDate,AccountId"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Name` | `string` |  |
| `attributes` | `object` |  |


</details>

#### Opportunities Search

Search for opportunities using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields.


**Python SDK**

```python
salesforce.opportunities.search(
    q="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "opportunities",
    "action": "search",
    "params": {
        "q": "<str>"
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOSL search query. Format: FIND {searchTerm} RETURNING Opportunity(fields) [LIMIT n]
Examples:
- "FIND {Enterprise} IN NAME FIELDS RETURNING Opportunity(Id,Name,Amount,StageName)"
- "FIND {renewal} IN ALL FIELDS RETURNING Opportunity(Id,Name,CloseDate) LIMIT 25"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `searchRecords` | `array<object>` |  |


</details>

### Tasks

#### Tasks List

Returns a list of tasks via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


**Python SDK**

```python
salesforce.tasks.list(
    q="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query for tasks. Default returns up to 200 records.
To change the limit, provide your own query with a LIMIT clause.
Example: "SELECT FIELDS(STANDARD) FROM Task WHERE Status = 'Not Started' LIMIT 100"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `totalSize` | `integer` |  |
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |
| `records` | `array<object>` |  |
| `records[].Id` | `string` |  |
| `records[].Subject` | `string` |  |
| `records[].attributes` | `object` |  |


</details>

#### Tasks Get

Get a single task by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


**Python SDK**

```python
salesforce.tasks.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce Task ID (18-character ID starting with '00T') |
| `fields` | `string` | No | Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
Example: "Id,Subject,Status,Priority,ActivityDate,WhoId,WhatId"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Subject` | `string` |  |
| `attributes` | `object` |  |


</details>

#### Tasks Search

Search for tasks using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields.


**Python SDK**

```python
salesforce.tasks.search(
    q="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "search",
    "params": {
        "q": "<str>"
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOSL search query. Format: FIND {searchTerm} RETURNING Task(fields) [LIMIT n]
Examples:
- "FIND {follow up} IN ALL FIELDS RETURNING Task(Id,Subject,Status,Priority)"
- "FIND {call} IN NAME FIELDS RETURNING Task(Id,Subject,ActivityDate) LIMIT 50"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `searchRecords` | `array<object>` |  |


</details>

### Events

#### Events List

Returns a list of events via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


**Python SDK**

```python
salesforce.events.list(
    q="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query for events. Default returns up to 200 records.
To change the limit, provide your own query with a LIMIT clause.
Example: "SELECT FIELDS(STANDARD) FROM Event WHERE StartDateTime > TODAY LIMIT 50"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `totalSize` | `integer` |  |
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |
| `records` | `array<object>` |  |
| `records[].Id` | `string` |  |
| `records[].Subject` | `string` |  |
| `records[].attributes` | `object` |  |


</details>

#### Events Get

Get a single event by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


**Python SDK**

```python
salesforce.events.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce Event ID (18-character ID starting with '00U') |
| `fields` | `string` | No | Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
Example: "Id,Subject,StartDateTime,EndDateTime,Location,WhoId,WhatId"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Subject` | `string` |  |
| `attributes` | `object` |  |


</details>

#### Events Search

Search for events using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields.


**Python SDK**

```python
salesforce.events.search(
    q="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "events",
    "action": "search",
    "params": {
        "q": "<str>"
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOSL search query. Format: FIND {searchTerm} RETURNING Event(fields) [LIMIT n]
Examples:
- "FIND {meeting} IN ALL FIELDS RETURNING Event(Id,Subject,StartDateTime,Location)"
- "FIND {demo} IN NAME FIELDS RETURNING Event(Id,Subject,EndDateTime) LIMIT 25"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `searchRecords` | `array<object>` |  |


</details>

### Campaigns

#### Campaigns List

Returns a list of campaigns via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


**Python SDK**

```python
salesforce.campaigns.list(
    q="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query for campaigns. Default returns up to 200 records.
To change the limit, provide your own query with a LIMIT clause.
Example: "SELECT FIELDS(STANDARD) FROM Campaign WHERE IsActive = true LIMIT 50"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `totalSize` | `integer` |  |
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |
| `records` | `array<object>` |  |
| `records[].Id` | `string` |  |
| `records[].Name` | `string` |  |
| `records[].attributes` | `object` |  |


</details>

#### Campaigns Get

Get a single campaign by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


**Python SDK**

```python
salesforce.campaigns.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce Campaign ID (18-character ID starting with '701') |
| `fields` | `string` | No | Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
Example: "Id,Name,Type,Status,StartDate,EndDate,IsActive"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Name` | `string` |  |
| `attributes` | `object` |  |


</details>

#### Campaigns Search

Search for campaigns using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields.


**Python SDK**

```python
salesforce.campaigns.search(
    q="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
    "action": "search",
    "params": {
        "q": "<str>"
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOSL search query. Format: FIND {searchTerm} RETURNING Campaign(fields) [LIMIT n]
Examples:
- "FIND {webinar} IN ALL FIELDS RETURNING Campaign(Id,Name,Type,Status)"
- "FIND {2024} IN NAME FIELDS RETURNING Campaign(Id,Name,StartDate,IsActive) LIMIT 50"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `searchRecords` | `array<object>` |  |


</details>

### Cases

#### Cases List

Returns a list of cases via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


**Python SDK**

```python
salesforce.cases.list(
    q="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query for cases. Default returns up to 200 records.
To change the limit, provide your own query with a LIMIT clause.
Example: "SELECT FIELDS(STANDARD) FROM Case WHERE Status = 'New' LIMIT 100"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `totalSize` | `integer` |  |
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |
| `records` | `array<object>` |  |
| `records[].Id` | `string` |  |
| `records[].CaseNumber` | `string` |  |
| `records[].Subject` | `string` |  |
| `records[].attributes` | `object` |  |


</details>

#### Cases Get

Get a single case by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


**Python SDK**

```python
salesforce.cases.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce Case ID (18-character ID starting with '500') |
| `fields` | `string` | No | Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
Example: "Id,CaseNumber,Subject,Status,Priority,ContactId,AccountId"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `CaseNumber` | `string` |  |
| `Subject` | `string` |  |
| `attributes` | `object` |  |


</details>

#### Cases Search

Search for cases using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields.


**Python SDK**

```python
salesforce.cases.search(
    q="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "cases",
    "action": "search",
    "params": {
        "q": "<str>"
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOSL search query. Format: FIND {searchTerm} RETURNING Case(fields) [LIMIT n]
Examples:
- "FIND {login issue} IN ALL FIELDS RETURNING Case(Id,CaseNumber,Subject,Status)"
- "FIND {urgent} IN NAME FIELDS RETURNING Case(Id,Subject,Priority) LIMIT 25"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `searchRecords` | `array<object>` |  |


</details>

### Notes

#### Notes List

Returns a list of notes via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


**Python SDK**

```python
salesforce.notes.list(
    q="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query for notes. Default returns up to 200 records.
To change the limit, provide your own query with a LIMIT clause.
Example: "SELECT FIELDS(STANDARD) FROM Note WHERE ParentId = '001xx...' LIMIT 50"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `totalSize` | `integer` |  |
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |
| `records` | `array<object>` |  |
| `records[].Id` | `string` |  |
| `records[].Title` | `string` |  |
| `records[].attributes` | `object` |  |


</details>

#### Notes Get

Get a single note by ID. Returns all accessible fields by default.
Use the `fields` parameter to retrieve only specific fields for better performance.


**Python SDK**

```python
salesforce.notes.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce Note ID (18-character ID starting with '002') |
| `fields` | `string` | No | Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
Example: "Id,Title,Body,ParentId,OwnerId"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Title` | `string` |  |
| `attributes` | `object` |  |


</details>

#### Notes Search

Search for notes using SOSL (Salesforce Object Search Language).
SOSL is optimized for text-based searches across multiple fields.


**Python SDK**

```python
salesforce.notes.search(
    q="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "notes",
    "action": "search",
    "params": {
        "q": "<str>"
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOSL search query. Format: FIND {searchTerm} RETURNING Note(fields) [LIMIT n]
Examples:
- "FIND {important} IN ALL FIELDS RETURNING Note(Id,Title,ParentId)"
- "FIND {action items} IN NAME FIELDS RETURNING Note(Id,Title,Body) LIMIT 50"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `searchRecords` | `array<object>` |  |


</details>

### Content Versions

#### Content Versions List

Returns a list of content versions (file metadata) via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.
Note: ContentVersion does not support FIELDS(STANDARD), so specific fields must be listed.


**Python SDK**

```python
salesforce.content_versions.list(
    q="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query for content versions. Default returns up to 200 records.
To change the limit, provide your own query with a LIMIT clause.
Example: "SELECT Id, Title, FileExtension, ContentSize FROM ContentVersion WHERE IsLatest = true LIMIT 50"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `totalSize` | `integer` |  |
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |
| `records` | `array<object>` |  |
| `records[].Id` | `string` |  |
| `records[].Title` | `string` |  |
| `records[].FileExtension` | `string` |  |
| `records[].ContentSize` | `integer` |  |
| `records[].ContentDocumentId` | `string` |  |
| `records[].VersionNumber` | `string` |  |
| `records[].IsLatest` | `boolean` |  |
| `records[].attributes` | `object` |  |


</details>

#### Content Versions Get

Get a single content version's metadata by ID. Returns file metadata, not the file content.
Use the download action to retrieve the actual file binary.


**Python SDK**

```python
salesforce.content_versions.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce ContentVersion ID (18-character ID starting with '068') |
| `fields` | `string` | No | Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
Example: "Id,Title,FileExtension,ContentSize,ContentDocumentId,IsLatest"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

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

#### Content Versions Download

Downloads the binary file content of a content version.
First use the list or get action to retrieve the ContentVersion ID and file metadata (size, type, etc.),
then use this action to download the actual file content.
The response is the raw binary file data.


**Python SDK**

```python
async for chunk in salesforce.content_versions.download(    id="<str>"):# Process each chunk (e.g., write to file)
    file.write(chunk)
```

> **Note**: Download operations return an async iterator of bytes chunks for memory-efficient streaming. Use `async for` to process chunks as they arrive.

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce ContentVersion ID (18-character ID starting with '068').
Obtain this ID from the list or get action.
 |
| `range_header` | `string` | No | Optional Range header for partial downloads (e.g., 'bytes=0-99') |


### Attachments

#### Attachments List

Returns a list of attachments (legacy) via SOQL query. Default returns up to 200 records.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.
Note: Attachments are a legacy feature; consider using ContentVersion (Salesforce Files) for new implementations.


**Python SDK**

```python
salesforce.attachments.list(
    q="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | SOQL query for attachments. Default returns up to 200 records.
To change the limit, provide your own query with a LIMIT clause.
Example: "SELECT Id, Name, ContentType, BodyLength, ParentId FROM Attachment WHERE ParentId = '001xx...' LIMIT 50"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `totalSize` | `integer` |  |
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |
| `records` | `array<object>` |  |
| `records[].Id` | `string` |  |
| `records[].Name` | `string` |  |
| `records[].ContentType` | `string` |  |
| `records[].BodyLength` | `integer` |  |
| `records[].ParentId` | `string` |  |
| `records[].attributes` | `object` |  |


</details>

#### Attachments Get

Get a single attachment's metadata by ID. Returns file metadata, not the file content.
Use the download action to retrieve the actual file binary.
Note: Attachments are a legacy feature; consider using ContentVersion for new implementations.


**Python SDK**

```python
salesforce.attachments.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce Attachment ID (18-character ID starting with '00P') |
| `fields` | `string` | No | Comma-separated list of fields to retrieve. If omitted, returns all accessible fields.
Example: "Id,Name,ContentType,BodyLength,ParentId"
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `Id` | `string` |  |
| `Name` | `string` |  |
| `ContentType` | `string` |  |
| `BodyLength` | `integer` |  |
| `ParentId` | `string` |  |
| `attributes` | `object` |  |


</details>

#### Attachments Download

Downloads the binary file content of an attachment (legacy).
First use the list or get action to retrieve the Attachment ID and file metadata,
then use this action to download the actual file content.
Note: Attachments are a legacy feature; consider using ContentVersion for new implementations.


**Python SDK**

```python
async for chunk in salesforce.attachments.download(    id="<str>"):# Process each chunk (e.g., write to file)
    file.write(chunk)
```

> **Note**: Download operations return an async iterator of bytes chunks for memory-efficient streaming. Use `async for` to process chunks as they arrive.

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Salesforce Attachment ID (18-character ID starting with '00P').
Obtain this ID from the list or get action.
 |
| `range_header` | `string` | No | Optional Range header for partial downloads (e.g., 'bytes=0-99') |


### Query

#### Query List

Execute a custom SOQL query and return results. Use this for querying any Salesforce object.
For pagination, check the response: if `done` is false, use `nextRecordsUrl` to fetch the next page.


**Python SDK**

```python
salesforce.query.list(
    q="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

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

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `totalSize` | `integer` |  |
| `done` | `boolean` |  |
| `nextRecordsUrl` | `string` |  |
| `records` | `array<object>` |  |


</details>



## Configuration

The connector requires the following configuration variables:

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `instance_url` | `string` | Yes | https://login.salesforce.com | Your Salesforce instance URL (e.g., https://na1.salesforce.com) |

These variables are used to construct the base API URL. Pass them via the `config` parameter when initializing the connector.


## Authentication

The Salesforce connector supports the following authentication methods:


### Salesforce OAuth 2.0

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `refresh_token` | `str` | Yes | OAuth refresh token for automatic token renewal |
| `client_id` | `str` | Yes | Connected App Consumer Key |
| `client_secret` | `str` | Yes | Connected App Consumer Secret |

#### Example

**Python SDK**

```python
SalesforceConnector(
  auth_config=SalesforceAuthConfig(
    refresh_token="<OAuth refresh token for automatic token renewal>",
    client_id="<Connected App Consumer Key>",
    client_secret="<Connected App Consumer Secret>"
  )
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
  "connector_definition_id": "b117307c-14b6-41aa-9422-947e34922962",
  "auth_config": {
    "refresh_token": "<OAuth refresh token for automatic token renewal>",
    "client_id": "<Connected App Consumer Key>",
    "client_secret": "<Connected App Consumer Secret>"
  },
  "name": "My Salesforce Connector"
}'
```

