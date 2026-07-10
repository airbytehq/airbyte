# Hubspot full reference

This is the full reference documentation for the Hubspot agent connector.

## Supported entities and actions

The Hubspot connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Contacts | [List](#contacts-list), [Create](#contacts-create), [Get](#contacts-get), [Update](#contacts-update), [API Search](#contacts-api-search), [Context Store Search](#contacts-context-store-search) |
| Companies | [List](#companies-list), [Create](#companies-create), [Get](#companies-get), [Update](#companies-update), [API Search](#companies-api-search), [Context Store Search](#companies-context-store-search) |
| Deals | [List](#deals-list), [Create](#deals-create), [Get](#deals-get), [Update](#deals-update), [API Search](#deals-api-search), [Context Store Search](#deals-context-store-search) |
| Tickets | [List](#tickets-list), [Create](#tickets-create), [Get](#tickets-get), [Update](#tickets-update), [API Search](#tickets-api-search), [Context Store Search](#tickets-context-store-search) |
| Notes | [List](#notes-list), [Create](#notes-create), [Get](#notes-get), [Update](#notes-update), [Delete](#notes-delete), [Context Store Search](#notes-context-store-search) |
| Calls | [List](#calls-list), [Create](#calls-create), [Get](#calls-get), [Update](#calls-update), [Delete](#calls-delete), [Context Store Search](#calls-context-store-search) |
| Emails | [List](#emails-list), [Create](#emails-create), [Get](#emails-get), [Update](#emails-update), [Delete](#emails-delete), [Context Store Search](#emails-context-store-search) |
| Meetings | [List](#meetings-list), [Create](#meetings-create), [Get](#meetings-get), [Update](#meetings-update), [Delete](#meetings-delete), [Context Store Search](#meetings-context-store-search) |
| Tasks | [List](#tasks-list), [Create](#tasks-create), [Get](#tasks-get), [Update](#tasks-update), [Delete](#tasks-delete), [Context Store Search](#tasks-context-store-search) |
| Schemas | [List](#schemas-list), [Get](#schemas-get) |
| Objects | [List](#objects-list), [Get](#objects-get) |

## Contacts

### Contacts List

Returns a paginated list of contacts

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "contacts",
  "action": "list"
}'
```

#### Python SDK

```python
await hubspot.contacts.list()
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
| `limit` | `integer` | No | The maximum number of results to display per page. |
| `after` | `string` | No | The paging cursor token of the last successfully read resource will be returned as the paging.next.after JSON property of a paged response containing more results. |
| `associations` | `string` | No | A comma separated list of associated object types to include in the response. Valid values are contacts, deals, tickets, and custom object type IDs or fully qualified names (e.g., "p12345_cars"). |
| `properties` | `string` | No | A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `propertiesWithHistory` | `string` | No | A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored. Usage of this parameter will reduce the maximum number of companies that can be read by a single request. |
| `archived` | `boolean` | No | Whether to return only results that have been archived. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `propertiesWithHistory` | `object \| null` |  |
| `associations` | `object \| null` |  |
| `objectWriteTraceId` | `string \| null` |  |
| `url` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string` |  |
| `next_link` | `string` |  |

</details>

### Contacts Create

Create a new contact in HubSpot CRM with the provided properties.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "contacts",
  "action": "create",
  "params": {
    "properties": {
      "email": "<str>"
    }
  }
}'
```

#### Python SDK

```python
await hubspot.contacts.create(
    properties={
        "email": "<str>"
    }
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
        "properties": {
            "email": "<str>"
        }
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `properties` | `object` | Yes | Contact properties to set |
| `properties.email` | `string` | Yes | Contact email address (required, used as unique identifier) |
| `properties.firstname` | `string` | No | Contact first name |
| `properties.lastname` | `string` | No | Contact last name |
| `properties.phone` | `string` | No | Contact phone number |
| `properties.company` | `string` | No | Company name associated with the contact |
| `properties.website` | `string` | No | Contact website URL |
| `properties.lifecyclestage` | `string` | No | Lifecycle stage (e.g., subscriber, lead, marketingqualifiedlead, salesqualifiedlead, opportunity, customer, evangelist, other) |
| `properties.jobtitle` | `string` | No | Contact job title |
| `properties.hubspot_owner_id` | `string` | No | ID of the HubSpot owner to assign to this contact |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `propertiesWithHistory` | `object \| null` |  |
| `associations` | `object \| null` |  |
| `objectWriteTraceId` | `string \| null` |  |
| `url` | `string \| null` |  |


</details>

### Contacts Get

Get a single contact by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "contacts",
  "action": "get",
  "params": {
    "contactId": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.contacts.get(
    contact_id="<str>"
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
        "contactId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `contactId` | `string` | Yes | Contact ID |
| `properties` | `string` | No | A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `propertiesWithHistory` | `string` | No | A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `associations` | `string` | No | A comma separated list of object types to retrieve associated IDs for. If any of the specified associations do not exist, they will be ignored. |
| `idProperty` | `string` | No | The name of a property whose values are unique for this object. |
| `archived` | `boolean` | No | Whether to return only results that have been archived. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `propertiesWithHistory` | `object \| null` |  |
| `associations` | `object \| null` |  |
| `objectWriteTraceId` | `string \| null` |  |
| `url` | `string \| null` |  |


</details>

### Contacts Update

Update an existing contact's properties by ID. Only the specified properties will be updated.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "contacts",
  "action": "update",
  "params": {
    "properties": {},
    "contactId": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.contacts.update(
    properties={},
    contact_id="<str>"
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
        "properties": {},
        "contactId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `properties` | `object` | Yes | Contact properties to update |
| `properties.email` | `string` | No | Contact email address |
| `properties.firstname` | `string` | No | Contact first name |
| `properties.lastname` | `string` | No | Contact last name |
| `properties.phone` | `string` | No | Contact phone number |
| `properties.company` | `string` | No | Company name associated with the contact |
| `properties.website` | `string` | No | Contact website URL |
| `properties.lifecyclestage` | `string` | No | Lifecycle stage (e.g., subscriber, lead, marketingqualifiedlead, salesqualifiedlead, opportunity, customer, evangelist, other) |
| `properties.jobtitle` | `string` | No | Contact job title |
| `properties.hubspot_owner_id` | `string` | No | ID of the HubSpot owner to assign to this contact |
| `contactId` | `string` | Yes | Contact ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `propertiesWithHistory` | `object \| null` |  |
| `associations` | `object \| null` |  |
| `objectWriteTraceId` | `string \| null` |  |
| `url` | `string \| null` |  |


</details>

### Contacts API Search

Search for contacts by filtering on properties, searching through associations, and sorting results.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "contacts",
  "action": "api_search"
}'
```

#### Python SDK

```python
await hubspot.contacts.api_search()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contacts",
    "action": "api_search"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `filterGroups` | `array<object>` | No | Up to 6 groups of filters defining additional query criteria. |
| `filterGroups.filters` | `array<object>` | No |  |
| `filterGroups.filters.operator` | `"BETWEEN" \| "CONTAINS_TOKEN" \| "EQ" \| "GT" \| "GTE" \| "HAS_PROPERTY" \| "IN" \| "LT" \| "LTE" \| "NEQ" \| "NOT_CONTAINS_TOKEN" \| "NOT_HAS_PROPERTY" \| "NOT_IN"` | No |  |
| `filterGroups.filters.propertyName` | `string` | No | The name of the property to apply the filter on. |
| `filterGroups.filters.value` | `string` | No | The value to match against the property. |
| `filterGroups.filters.values` | `array<string>` | No | The values to match against the property. |
| `properties` | `array<string>` | No | A list of property names to include in the response. |
| `limit` | `integer` | No | Maximum number of results to return |
| `after` | `string` | No | A paging cursor token for retrieving subsequent pages. |
| `sorts` | `array<object>` | No | Sort criteria |
| `sorts.propertyName` | `string` | No |  |
| `sorts.direction` | `"ASCENDING" \| "DESCENDING"` | No |  |
| `query` | `string` | No | The search query string, up to 3000 characters. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `propertiesWithHistory` | `object \| null` |  |
| `associations` | `object \| null` |  |
| `objectWriteTraceId` | `string \| null` |  |
| `url` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `total` | `integer` |  |
| `next_cursor` | `string` |  |
| `next_link` | `string` |  |

</details>

### Contacts Context Store Search

Search and filter contacts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "contacts",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "archived": true
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await hubspot.contacts.context_store_search(
    query={"filter": {"eq": {"archived": True}}}
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
        "query": {"filter": {"eq": {"archived": True}}}
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
| `archived` | `boolean` | Boolean flag indicating whether the contact has been archived or deleted |
| `companies` | `array` | Associated company records linked to this contact |
| `createdAt` | `string` | Timestamp indicating when the contact was first created in the system |
| `id` | `string` | Unique identifier for the contact record |
| `properties` | `object` | Key-value object storing all contact properties and their values. |
| `properties.associatedcompanyid` | `string` | ID of the associated company |
| `properties.createdate` | `string` | Date the contact was created |
| `properties.email` | `string` | Contact email address |
| `properties.firstname` | `string` | Contact first name |
| `properties.hs_object_id` | `string` | HubSpot object ID |
| `properties.hubspot_owner_id` | `string` | ID of the HubSpot owner assigned to this contact |
| `properties.lastmodifieddate` | `string` | Last modified date of the contact |
| `properties.lastname` | `string` | Contact last name |
| `updatedAt` | `string` | Timestamp indicating when the contact record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].archived` | `boolean` | Boolean flag indicating whether the contact has been archived or deleted |
| `data[].companies` | `array` | Associated company records linked to this contact |
| `data[].createdAt` | `string` | Timestamp indicating when the contact was first created in the system |
| `data[].id` | `string` | Unique identifier for the contact record |
| `data[].properties` | `object` | Key-value object storing all contact properties and their values. |
| `data[].properties.associatedcompanyid` | `string` | ID of the associated company |
| `data[].properties.createdate` | `string` | Date the contact was created |
| `data[].properties.email` | `string` | Contact email address |
| `data[].properties.firstname` | `string` | Contact first name |
| `data[].properties.hs_object_id` | `string` | HubSpot object ID |
| `data[].properties.hubspot_owner_id` | `string` | ID of the HubSpot owner assigned to this contact |
| `data[].properties.lastmodifieddate` | `string` | Last modified date of the contact |
| `data[].properties.lastname` | `string` | Contact last name |
| `data[].updatedAt` | `string` | Timestamp indicating when the contact record was last modified |

</details>

## Companies

### Companies List

Retrieve all companies, using query parameters to control the information that gets returned.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "companies",
  "action": "list"
}'
```

#### Python SDK

```python
await hubspot.companies.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "companies",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | The maximum number of results to display per page. |
| `after` | `string` | No | The paging cursor token of the last successfully read resource will be returned as the paging.next.after JSON property of a paged response containing more results. |
| `associations` | `string` | No | A comma separated list of associated object types to include in the response. Valid values are contacts, deals, tickets, and custom object type IDs or fully qualified names (e.g., "p12345_cars"). |
| `properties` | `string` | No | A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `propertiesWithHistory` | `string` | No | A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored. Usage of this parameter will reduce the maximum number of companies that can be read by a single request. |
| `archived` | `boolean` | No | Whether to return only results that have been archived. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `propertiesWithHistory` | `object \| null` |  |
| `associations` | `object \| null` |  |
| `objectWriteTraceId` | `string \| null` |  |
| `url` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string` |  |
| `next_link` | `string` |  |

</details>

### Companies Create

Create a new company in HubSpot CRM with the provided properties.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "companies",
  "action": "create",
  "params": {
    "properties": {
      "name": "<str>"
    }
  }
}'
```

#### Python SDK

```python
await hubspot.companies.create(
    properties={
        "name": "<str>"
    }
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "companies",
    "action": "create",
    "params": {
        "properties": {
            "name": "<str>"
        }
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `properties` | `object` | Yes | Company properties to set |
| `properties.name` | `string` | Yes | Company name (required) |
| `properties.domain` | `string` | No | Company domain name (e.g., example.com) |
| `properties.description` | `string` | No | Company description |
| `properties.phone` | `string` | No | Company phone number |
| `properties.industry` | `string` | No | Company industry (e.g., COMPUTER_SOFTWARE, INFORMATION_TECHNOLOGY_AND_SERVICES, INTERNET, FINANCIAL_SERVICES, MARKETING_AND_ADVERTISING, EDUCATION_MANAGEMENT) |
| `properties.city` | `string` | No | Company city |
| `properties.state` | `string` | No | Company state/region |
| `properties.country` | `string` | No | Company country |
| `properties.zip` | `string` | No | Company postal/zip code |
| `properties.numberofemployees` | `string` | No | Number of employees |
| `properties.annualrevenue` | `string` | No | Annual revenue |
| `properties.lifecyclestage` | `string` | No | Lifecycle stage (e.g., subscriber, lead, marketingqualifiedlead, salesqualifiedlead, opportunity, customer, evangelist, other) |
| `properties.hubspot_owner_id` | `string` | No | ID of the HubSpot owner to assign to this company |
| `properties.website` | `string` | No | Company website URL |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `propertiesWithHistory` | `object \| null` |  |
| `associations` | `object \| null` |  |
| `objectWriteTraceId` | `string \| null` |  |
| `url` | `string \| null` |  |


</details>

### Companies Get

Get a single company by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "companies",
  "action": "get",
  "params": {
    "companyId": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.companies.get(
    company_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "companies",
    "action": "get",
    "params": {
        "companyId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `companyId` | `string` | Yes | Company ID |
| `properties` | `string` | No | A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `propertiesWithHistory` | `string` | No | A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `associations` | `string` | No | A comma separated list of object types to retrieve associated IDs for. If any of the specified associations do not exist, they will be ignored. |
| `idProperty` | `string` | No | The name of a property whose values are unique for this object. |
| `archived` | `boolean` | No | Whether to return only results that have been archived. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `propertiesWithHistory` | `object \| null` |  |
| `associations` | `object \| null` |  |
| `objectWriteTraceId` | `string \| null` |  |
| `url` | `string \| null` |  |


</details>

### Companies Update

Update an existing company's properties by ID. Only the specified properties will be updated.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "companies",
  "action": "update",
  "params": {
    "properties": {},
    "companyId": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.companies.update(
    properties={},
    company_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "companies",
    "action": "update",
    "params": {
        "properties": {},
        "companyId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `properties` | `object` | Yes | Company properties to update |
| `properties.name` | `string` | No | Company name |
| `properties.domain` | `string` | No | Company domain name (e.g., example.com) |
| `properties.description` | `string` | No | Company description |
| `properties.phone` | `string` | No | Company phone number |
| `properties.industry` | `string` | No | Company industry (e.g., COMPUTER_SOFTWARE, INFORMATION_TECHNOLOGY_AND_SERVICES, INTERNET, FINANCIAL_SERVICES, MARKETING_AND_ADVERTISING, EDUCATION_MANAGEMENT) |
| `properties.city` | `string` | No | Company city |
| `properties.state` | `string` | No | Company state/region |
| `properties.country` | `string` | No | Company country |
| `properties.zip` | `string` | No | Company postal/zip code |
| `properties.numberofemployees` | `string` | No | Number of employees |
| `properties.annualrevenue` | `string` | No | Annual revenue |
| `properties.lifecyclestage` | `string` | No | Lifecycle stage (e.g., subscriber, lead, marketingqualifiedlead, salesqualifiedlead, opportunity, customer, evangelist, other) |
| `properties.hubspot_owner_id` | `string` | No | ID of the HubSpot owner to assign to this company |
| `properties.website` | `string` | No | Company website URL |
| `companyId` | `string` | Yes | Company ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `propertiesWithHistory` | `object \| null` |  |
| `associations` | `object \| null` |  |
| `objectWriteTraceId` | `string \| null` |  |
| `url` | `string \| null` |  |


</details>

### Companies API Search

Search for companies by filtering on properties, searching through associations, and sorting results.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "companies",
  "action": "api_search"
}'
```

#### Python SDK

```python
await hubspot.companies.api_search()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "companies",
    "action": "api_search"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `filterGroups` | `array<object>` | No | Up to 6 groups of filters defining additional query criteria. |
| `filterGroups.filters` | `array<object>` | No |  |
| `filterGroups.filters.operator` | `"BETWEEN" \| "CONTAINS_TOKEN" \| "EQ" \| "GT" \| "GTE" \| "HAS_PROPERTY" \| "IN" \| "LT" \| "LTE" \| "NEQ" \| "NOT_CONTAINS_TOKEN" \| "NOT_HAS_PROPERTY" \| "NOT_IN"` | No |  |
| `filterGroups.filters.propertyName` | `string` | No | The name of the property to apply the filter on. |
| `filterGroups.filters.value` | `string` | No | The value to match against the property. |
| `filterGroups.filters.values` | `array<string>` | No | The values to match against the property. |
| `properties` | `array<string>` | No | A list of property names to include in the response. |
| `limit` | `integer` | No | Maximum number of results to return |
| `after` | `string` | No | A paging cursor token for retrieving subsequent pages. |
| `sorts` | `array<object>` | No | Sort criteria |
| `sorts.propertyName` | `string` | No |  |
| `sorts.direction` | `"ASCENDING" \| "DESCENDING"` | No |  |
| `query` | `string` | No | The search query string, up to 3000 characters. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `propertiesWithHistory` | `object \| null` |  |
| `associations` | `object \| null` |  |
| `objectWriteTraceId` | `string \| null` |  |
| `url` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `total` | `integer` |  |
| `next_cursor` | `string` |  |
| `next_link` | `string` |  |

</details>

### Companies Context Store Search

Search and filter companies records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "companies",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "archived": true
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await hubspot.companies.context_store_search(
    query={"filter": {"eq": {"archived": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "companies",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"archived": True}}}
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
| `archived` | `boolean` | Indicates whether the company has been deleted and moved to the recycling bin |
| `contacts` | `array` | Associated contact records linked to this company |
| `createdAt` | `string` | Timestamp when the company record was created |
| `id` | `string` | Unique identifier for the company record |
| `properties` | `object` | Object containing all property values for the company |
| `properties.createdate` | `string` | Date the company was created |
| `properties.domain` | `string` | Company domain name |
| `properties.hs_lastmodifieddate` | `string` | Last modified date of the company |
| `properties.hs_object_id` | `string` | HubSpot object ID |
| `properties.hubspot_owner_id` | `string` | ID of the HubSpot owner assigned to this company |
| `properties.name` | `string` | Company name |
| `updatedAt` | `string` | Timestamp when the company record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].archived` | `boolean` | Indicates whether the company has been deleted and moved to the recycling bin |
| `data[].contacts` | `array` | Associated contact records linked to this company |
| `data[].createdAt` | `string` | Timestamp when the company record was created |
| `data[].id` | `string` | Unique identifier for the company record |
| `data[].properties` | `object` | Object containing all property values for the company |
| `data[].properties.createdate` | `string` | Date the company was created |
| `data[].properties.domain` | `string` | Company domain name |
| `data[].properties.hs_lastmodifieddate` | `string` | Last modified date of the company |
| `data[].properties.hs_object_id` | `string` | HubSpot object ID |
| `data[].properties.hubspot_owner_id` | `string` | ID of the HubSpot owner assigned to this company |
| `data[].properties.name` | `string` | Company name |
| `data[].updatedAt` | `string` | Timestamp when the company record was last modified |

</details>

## Deals

### Deals List

Returns a paginated list of deals

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "deals",
  "action": "list"
}'
```

#### Python SDK

```python
await hubspot.deals.list()
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
| `limit` | `integer` | No | The maximum number of results to display per page. |
| `after` | `string` | No | The paging cursor token of the last successfully read resource will be returned as the paging.next.after JSON property of a paged response containing more results. |
| `associations` | `string` | No | A comma separated list of associated object types to include in the response. Valid values are contacts, deals, tickets, and custom object type IDs or fully qualified names (e.g., "p12345_cars"). |
| `properties` | `string` | No | A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `propertiesWithHistory` | `string` | No | A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored. Usage of this parameter will reduce the maximum number of companies that can be read by a single request. |
| `archived` | `boolean` | No | Whether to return only results that have been archived. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `propertiesWithHistory` | `object \| null` |  |
| `associations` | `object \| null` |  |
| `objectWriteTraceId` | `string \| null` |  |
| `url` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string` |  |
| `next_link` | `string` |  |

</details>

### Deals Create

Create a new deal in HubSpot CRM with the provided properties.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "deals",
  "action": "create",
  "params": {
    "properties": {
      "dealname": "<str>"
    }
  }
}'
```

#### Python SDK

```python
await hubspot.deals.create(
    properties={
        "dealname": "<str>"
    }
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
        "properties": {
            "dealname": "<str>"
        }
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `properties` | `object` | Yes | Deal properties to set |
| `properties.dealname` | `string` | Yes | Deal name (required) |
| `properties.amount` | `string` | No | Deal amount |
| `properties.dealstage` | `string` | No | Deal stage ID (e.g., appointmentscheduled, qualifiedtobuy, presentationscheduled, decisionmakerboughtin, contractsent, closedwon, closedlost) |
| `properties.pipeline` | `string` | No | Deal pipeline ID (defaults to the default pipeline) |
| `properties.closedate` | `string` | No | Expected close date (ISO 8601 format, e.g., 2024-12-31T00:00:00.000Z) |
| `properties.dealtype` | `string` | No | Deal type (e.g., newbusiness, existingbusiness) |
| `properties.description` | `string` | No | Deal description |
| `properties.hubspot_owner_id` | `string` | No | ID of the HubSpot owner to assign to this deal |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `propertiesWithHistory` | `object \| null` |  |
| `associations` | `object \| null` |  |
| `objectWriteTraceId` | `string \| null` |  |
| `url` | `string \| null` |  |


</details>

### Deals Get

Get a single deal by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "deals",
  "action": "get",
  "params": {
    "dealId": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.deals.get(
    deal_id="<str>"
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
        "dealId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `dealId` | `string` | Yes | Deal ID |
| `properties` | `string` | No | A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `propertiesWithHistory` | `string` | No | A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `associations` | `string` | No | A comma separated list of object types to retrieve associated IDs for. If any of the specified associations do not exist, they will be ignored. |
| `idProperty` | `string` | No | The name of a property whose values are unique for this object. |
| `archived` | `boolean` | No | Whether to return only results that have been archived. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `propertiesWithHistory` | `object \| null` |  |
| `associations` | `object \| null` |  |
| `objectWriteTraceId` | `string \| null` |  |
| `url` | `string \| null` |  |


</details>

### Deals Update

Update an existing deal's properties by ID. Only the specified properties will be updated.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "deals",
  "action": "update",
  "params": {
    "properties": {},
    "dealId": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.deals.update(
    properties={},
    deal_id="<str>"
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
        "properties": {},
        "dealId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `properties` | `object` | Yes | Deal properties to update |
| `properties.dealname` | `string` | No | Deal name |
| `properties.amount` | `string` | No | Deal amount |
| `properties.dealstage` | `string` | No | Deal stage ID (e.g., appointmentscheduled, qualifiedtobuy, presentationscheduled, decisionmakerboughtin, contractsent, closedwon, closedlost) |
| `properties.pipeline` | `string` | No | Deal pipeline ID |
| `properties.closedate` | `string` | No | Expected close date (ISO 8601 format, e.g., 2024-12-31T00:00:00.000Z) |
| `properties.dealtype` | `string` | No | Deal type (e.g., newbusiness, existingbusiness) |
| `properties.description` | `string` | No | Deal description |
| `properties.hubspot_owner_id` | `string` | No | ID of the HubSpot owner to assign to this deal |
| `dealId` | `string` | Yes | Deal ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `propertiesWithHistory` | `object \| null` |  |
| `associations` | `object \| null` |  |
| `objectWriteTraceId` | `string \| null` |  |
| `url` | `string \| null` |  |


</details>

### Deals API Search

Search deals with filters and sorting

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "deals",
  "action": "api_search"
}'
```

#### Python SDK

```python
await hubspot.deals.api_search()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "deals",
    "action": "api_search"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `filterGroups` | `array<object>` | No | Up to 6 groups of filters defining additional query criteria. |
| `filterGroups.filters` | `array<object>` | No |  |
| `filterGroups.filters.operator` | `"BETWEEN" \| "CONTAINS_TOKEN" \| "EQ" \| "GT" \| "GTE" \| "HAS_PROPERTY" \| "IN" \| "LT" \| "LTE" \| "NEQ" \| "NOT_CONTAINS_TOKEN" \| "NOT_HAS_PROPERTY" \| "NOT_IN"` | No |  |
| `filterGroups.filters.propertyName` | `string` | No | The name of the property to apply the filter on. |
| `filterGroups.filters.value` | `string` | No | The value to match against the property. |
| `filterGroups.filters.values` | `array<string>` | No | The values to match against the property. |
| `properties` | `array<string>` | No | A list of property names to include in the response. |
| `limit` | `integer` | No | Maximum number of results to return |
| `after` | `string` | No | A paging cursor token for retrieving subsequent pages. |
| `sorts` | `array<object>` | No | Sort criteria |
| `sorts.propertyName` | `string` | No |  |
| `sorts.direction` | `"ASCENDING" \| "DESCENDING"` | No |  |
| `query` | `string` | No | The search query string, up to 3000 characters. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `propertiesWithHistory` | `object \| null` |  |
| `associations` | `object \| null` |  |
| `objectWriteTraceId` | `string \| null` |  |
| `url` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `total` | `integer` |  |
| `next_cursor` | `string` |  |
| `next_link` | `string` |  |

</details>

### Deals Context Store Search

Search and filter deals records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "deals",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "archived": true
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await hubspot.deals.context_store_search(
    query={"filter": {"eq": {"archived": True}}}
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
        "query": {"filter": {"eq": {"archived": True}}}
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
| `archived` | `boolean` | Indicates whether the deal has been deleted and moved to the recycling bin |
| `companies` | `array` | Collection of company records associated with the deal |
| `contacts` | `array` | Collection of contact records associated with the deal |
| `createdAt` | `string` | Timestamp when the deal record was originally created |
| `id` | `string` | Unique identifier for the deal record |
| `line_items` | `array` | Collection of product line items associated with the deal |
| `properties` | `object` | Key-value object containing all deal properties and custom fields |
| `properties.amount` | `string` | Deal amount |
| `properties.closedate` | `string` | Expected close date of the deal |
| `properties.createdate` | `string` | Date the deal was created |
| `properties.dealname` | `string` | Deal name |
| `properties.dealstage` | `string` | Current deal stage |
| `properties.hs_lastmodifieddate` | `string` | Last modified date of the deal |
| `properties.hs_object_id` | `string` | HubSpot object ID |
| `properties.hubspot_owner_id` | `string` | ID of the HubSpot owner assigned to this deal |
| `properties.pipeline` | `string` | Deal pipeline |
| `updatedAt` | `string` | Timestamp when the deal record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].archived` | `boolean` | Indicates whether the deal has been deleted and moved to the recycling bin |
| `data[].companies` | `array` | Collection of company records associated with the deal |
| `data[].contacts` | `array` | Collection of contact records associated with the deal |
| `data[].createdAt` | `string` | Timestamp when the deal record was originally created |
| `data[].id` | `string` | Unique identifier for the deal record |
| `data[].line_items` | `array` | Collection of product line items associated with the deal |
| `data[].properties` | `object` | Key-value object containing all deal properties and custom fields |
| `data[].properties.amount` | `string` | Deal amount |
| `data[].properties.closedate` | `string` | Expected close date of the deal |
| `data[].properties.createdate` | `string` | Date the deal was created |
| `data[].properties.dealname` | `string` | Deal name |
| `data[].properties.dealstage` | `string` | Current deal stage |
| `data[].properties.hs_lastmodifieddate` | `string` | Last modified date of the deal |
| `data[].properties.hs_object_id` | `string` | HubSpot object ID |
| `data[].properties.hubspot_owner_id` | `string` | ID of the HubSpot owner assigned to this deal |
| `data[].properties.pipeline` | `string` | Deal pipeline |
| `data[].updatedAt` | `string` | Timestamp when the deal record was last modified |

</details>

## Tickets

### Tickets List

Returns a paginated list of tickets

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "tickets",
  "action": "list"
}'
```

#### Python SDK

```python
await hubspot.tickets.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tickets",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | The maximum number of results to display per page. |
| `after` | `string` | No | The paging cursor token of the last successfully read resource will be returned as the paging.next.after JSON property of a paged response containing more results. |
| `associations` | `string` | No | A comma separated list of associated object types to include in the response. Valid values are contacts, deals, tickets, and custom object type IDs or fully qualified names (e.g., "p12345_cars"). |
| `properties` | `string` | No | A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `propertiesWithHistory` | `string` | No | A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored. Usage of this parameter will reduce the maximum number of companies that can be read by a single request. |
| `archived` | `boolean` | No | Whether to return only results that have been archived. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `propertiesWithHistory` | `object \| null` |  |
| `associations` | `object \| null` |  |
| `objectWriteTraceId` | `string \| null` |  |
| `url` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string` |  |
| `next_link` | `string` |  |

</details>

### Tickets Create

Create a new support ticket in HubSpot CRM with the provided properties.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "tickets",
  "action": "create",
  "params": {
    "properties": {
      "subject": "<str>",
      "hs_pipeline": "<str>",
      "hs_pipeline_stage": "<str>"
    }
  }
}'
```

#### Python SDK

```python
await hubspot.tickets.create(
    properties={
        "subject": "<str>",
        "hs_pipeline": "<str>",
        "hs_pipeline_stage": "<str>"
    }
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tickets",
    "action": "create",
    "params": {
        "properties": {
            "subject": "<str>",
            "hs_pipeline": "<str>",
            "hs_pipeline_stage": "<str>"
        }
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `properties` | `object` | Yes | Ticket properties to set |
| `properties.subject` | `string` | Yes | Ticket subject line (required) |
| `properties.content` | `string` | No | Ticket description/content |
| `properties.hs_pipeline` | `string` | Yes | Ticket pipeline ID (required, use '0' for default pipeline) |
| `properties.hs_pipeline_stage` | `string` | Yes | Pipeline stage ID (required, e.g., '1' for New in the default pipeline) |
| `properties.hs_ticket_priority` | `string` | No | Ticket priority (e.g., LOW, MEDIUM, HIGH) |
| `properties.hs_ticket_category` | `string` | No | Ticket category |
| `properties.hubspot_owner_id` | `string` | No | ID of the HubSpot owner to assign to this ticket |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `propertiesWithHistory` | `object \| null` |  |
| `associations` | `object \| null` |  |
| `objectWriteTraceId` | `string \| null` |  |
| `url` | `string \| null` |  |


</details>

### Tickets Get

Get a single ticket by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "tickets",
  "action": "get",
  "params": {
    "ticketId": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.tickets.get(
    ticket_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tickets",
    "action": "get",
    "params": {
        "ticketId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ticketId` | `string` | Yes | Ticket ID |
| `properties` | `string` | No | A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `propertiesWithHistory` | `string` | No | A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `associations` | `string` | No | A comma separated list of object types to retrieve associated IDs for. If any of the specified associations do not exist, they will be ignored. |
| `idProperty` | `string` | No | The name of a property whose values are unique for this object. |
| `archived` | `boolean` | No | Whether to return only results that have been archived. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `propertiesWithHistory` | `object \| null` |  |
| `associations` | `object \| null` |  |
| `objectWriteTraceId` | `string \| null` |  |
| `url` | `string \| null` |  |


</details>

### Tickets Update

Update an existing ticket's properties by ID. Only the specified properties will be updated.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "tickets",
  "action": "update",
  "params": {
    "properties": {},
    "ticketId": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.tickets.update(
    properties={},
    ticket_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tickets",
    "action": "update",
    "params": {
        "properties": {},
        "ticketId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `properties` | `object` | Yes | Ticket properties to update |
| `properties.subject` | `string` | No | Ticket subject line |
| `properties.content` | `string` | No | Ticket description/content |
| `properties.hs_pipeline` | `string` | No | Ticket pipeline ID |
| `properties.hs_pipeline_stage` | `string` | No | Pipeline stage ID |
| `properties.hs_ticket_priority` | `string` | No | Ticket priority (e.g., LOW, MEDIUM, HIGH) |
| `properties.hs_ticket_category` | `string` | No | Ticket category |
| `properties.hubspot_owner_id` | `string` | No | ID of the HubSpot owner to assign to this ticket |
| `ticketId` | `string` | Yes | Ticket ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `propertiesWithHistory` | `object \| null` |  |
| `associations` | `object \| null` |  |
| `objectWriteTraceId` | `string \| null` |  |
| `url` | `string \| null` |  |


</details>

### Tickets API Search

Search for tickets by filtering on properties, searching through associations, and sorting results.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "tickets",
  "action": "api_search"
}'
```

#### Python SDK

```python
await hubspot.tickets.api_search()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tickets",
    "action": "api_search"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `filterGroups` | `array<object>` | No | Up to 6 groups of filters defining additional query criteria. |
| `filterGroups.filters` | `array<object>` | No |  |
| `filterGroups.filters.operator` | `"BETWEEN" \| "CONTAINS_TOKEN" \| "EQ" \| "GT" \| "GTE" \| "HAS_PROPERTY" \| "IN" \| "LT" \| "LTE" \| "NEQ" \| "NOT_CONTAINS_TOKEN" \| "NOT_HAS_PROPERTY" \| "NOT_IN"` | No |  |
| `filterGroups.filters.propertyName` | `string` | No | The name of the property to apply the filter on. |
| `filterGroups.filters.value` | `string` | No | The value to match against the property. |
| `filterGroups.filters.values` | `array<string>` | No | The values to match against the property. |
| `properties` | `array<string>` | No | A list of property names to include in the response. |
| `limit` | `integer` | No | Maximum number of results to return |
| `after` | `string` | No | A paging cursor token for retrieving subsequent pages. |
| `sorts` | `array<object>` | No | Sort criteria |
| `sorts.propertyName` | `string` | No |  |
| `sorts.direction` | `"ASCENDING" \| "DESCENDING"` | No |  |
| `query` | `string` | No | The search query string, up to 3000 characters. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `propertiesWithHistory` | `object \| null` |  |
| `associations` | `object \| null` |  |
| `objectWriteTraceId` | `string \| null` |  |
| `url` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `total` | `integer` |  |
| `next_cursor` | `string` |  |
| `next_link` | `string` |  |

</details>

### Tickets Context Store Search

Search and filter tickets records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "tickets",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "archived": true
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await hubspot.tickets.context_store_search(
    query={"filter": {"eq": {"archived": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tickets",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"archived": True}}}
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
| `archived` | `boolean` | Indicates whether the ticket has been deleted and moved to the recycling bin |
| `companies` | `array` | Collection of company records associated with the ticket |
| `contacts` | `array` | Collection of contact records associated with the ticket |
| `createdAt` | `string` | Timestamp when the ticket record was originally created |
| `id` | `string` | Unique identifier for the ticket record |
| `properties` | `object` | Object containing all property values for the ticket |
| `properties.content` | `string` | Ticket content/description |
| `properties.createdate` | `string` | Date the ticket was created |
| `properties.hs_lastmodifieddate` | `string` | Last modified date of the ticket |
| `properties.hs_object_id` | `string` | HubSpot object ID |
| `properties.hs_pipeline` | `string` | Ticket pipeline |
| `properties.hs_pipeline_stage` | `string` | Current pipeline stage of the ticket |
| `properties.hs_ticket_category` | `string` | Ticket category |
| `properties.hs_ticket_priority` | `string` | Ticket priority level |
| `properties.subject` | `string` | Ticket subject line |
| `updatedAt` | `string` | Timestamp when the ticket record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].archived` | `boolean` | Indicates whether the ticket has been deleted and moved to the recycling bin |
| `data[].companies` | `array` | Collection of company records associated with the ticket |
| `data[].contacts` | `array` | Collection of contact records associated with the ticket |
| `data[].createdAt` | `string` | Timestamp when the ticket record was originally created |
| `data[].id` | `string` | Unique identifier for the ticket record |
| `data[].properties` | `object` | Object containing all property values for the ticket |
| `data[].properties.content` | `string` | Ticket content/description |
| `data[].properties.createdate` | `string` | Date the ticket was created |
| `data[].properties.hs_lastmodifieddate` | `string` | Last modified date of the ticket |
| `data[].properties.hs_object_id` | `string` | HubSpot object ID |
| `data[].properties.hs_pipeline` | `string` | Ticket pipeline |
| `data[].properties.hs_pipeline_stage` | `string` | Current pipeline stage of the ticket |
| `data[].properties.hs_ticket_category` | `string` | Ticket category |
| `data[].properties.hs_ticket_priority` | `string` | Ticket priority level |
| `data[].properties.subject` | `string` | Ticket subject line |
| `data[].updatedAt` | `string` | Timestamp when the ticket record was last modified |

</details>

## Notes

### Notes List

Returns a paginated list of notes

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "notes",
  "action": "list"
}'
```

#### Python SDK

```python
await hubspot.notes.list()
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
| `limit` | `integer` | No | The maximum number of results to display per page. |
| `after` | `string` | No | The paging cursor token of the last successfully read resource will be returned as the paging.next.after JSON property of a paged response containing more results. |
| `associations` | `string` | No | A comma separated list of associated object types to include in the response. Valid values are contacts, companies, deals, tickets, and custom object type IDs or fully qualified names. |
| `properties` | `string` | No | A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `propertiesWithHistory` | `string` | No | A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `archived` | `boolean` | No | Whether to return only results that have been archived. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `associations` | `object \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string` |  |
| `next_link` | `string` |  |

</details>

### Notes Create

Create a new note in HubSpot CRM. Notes can be associated with contacts,
companies, deals, or tickets by using the associations parameter.
The hs_timestamp property sets when the note activity occurred.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "notes",
  "action": "create",
  "params": {
    "properties": {
      "hs_note_body": "<str>",
      "hs_timestamp": "<str>"
    },
    "associations": []
  }
}'
```

#### Python SDK

```python
await hubspot.notes.create(
    properties={
        "hs_note_body": "<str>",
        "hs_timestamp": "<str>"
    },
    associations=[]
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
        "properties": {
            "hs_note_body": "<str>",
            "hs_timestamp": "<str>"
        },
        "associations": []
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `properties` | `object` | Yes | Note properties to set |
| `properties.hs_note_body` | `string` | Yes | The body content of the note (supports HTML) |
| `properties.hs_timestamp` | `string` | Yes | Required. Timestamp when the note activity occurred (ISO 8601 format, e.g. 2025-01-15T10:30:00.000Z). Use the current time if the user does not specify one. |
| `properties.hubspot_owner_id` | `string` | No | ID of the HubSpot owner to assign to this note |
| `associations` | `array<object>` | No | Associate the note with other CRM records (contacts, companies, deals, tickets) |
| `associations.to` | `object` | No |  |
| `associations.to.id` | `string` | No | ID of the record to associate with |
| `associations.types` | `array<object>` | No |  |
| `associations.types.associationCategory` | `string` | No | Association category (e.g., HUBSPOT_DEFINED) |
| `associations.types.associationTypeId` | `integer` | No | Association type ID (e.g., 202 for note-to-contact, 190 for note-to-company, 214 for note-to-deal, 18 for note-to-ticket) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `associations` | `object \| null` |  |


</details>

### Notes Get

Get a single note by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "notes",
  "action": "get",
  "params": {
    "noteId": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.notes.get(
    note_id="<str>"
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
        "noteId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `noteId` | `string` | Yes | Note ID |
| `properties` | `string` | No | A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `propertiesWithHistory` | `string` | No | A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `associations` | `string` | No | A comma separated list of object types to retrieve associated IDs for. If any of the specified associations do not exist, they will be ignored. |
| `idProperty` | `string` | No | The name of a property whose values are unique for this object. |
| `archived` | `boolean` | No | Whether to return only results that have been archived. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `associations` | `object \| null` |  |


</details>

### Notes Update

Update an existing note's properties by ID.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "notes",
  "action": "update",
  "params": {
    "properties": {},
    "noteId": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.notes.update(
    properties={},
    note_id="<str>"
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
        "properties": {},
        "noteId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `properties` | `object` | Yes | Note properties to update |
| `properties.hs_note_body` | `string` | No | The body content of the note (supports HTML) |
| `properties.hs_timestamp` | `string` | No | Timestamp when the note activity occurred |
| `properties.hubspot_owner_id` | `string` | No | ID of the HubSpot owner to assign to this note |
| `noteId` | `string` | Yes | Note ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `associations` | `object \| null` |  |


</details>

### Notes Delete

Archive a note by ID. This is a soft delete — the note is moved to the
recycle bin and can be restored for approximately 90 days. No public
hard-delete endpoint exists.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "notes",
  "action": "delete",
  "params": {
    "noteId": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.notes.delete(
    note_id="<str>"
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
        "noteId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `noteId` | `string` | Yes | Note ID |


### Notes Context Store Search

Search and filter notes records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "notes",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "archived": true
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await hubspot.notes.context_store_search(
    query={"filter": {"eq": {"archived": True}}}
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
        "query": {"filter": {"eq": {"archived": True}}}
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
| `archived` | `boolean` | Indicates whether the note has been archived |
| `createdAt` | `string` | Timestamp when the note was created |
| `id` | `string` | Unique identifier for the note record |
| `properties` | `object` | Object containing all property values for the note |
| `properties.hs_createdate` | `string` | Date the note was created |
| `properties.hs_lastmodifieddate` | `string` | Last modified date of the note |
| `properties.hs_note_body` | `string` | The body content of the note (supports HTML) |
| `properties.hs_object_id` | `string` | HubSpot object ID |
| `properties.hs_timestamp` | `string` | Timestamp when the note activity occurred |
| `properties.hubspot_owner_id` | `string` | ID of the note owner |
| `updatedAt` | `string` | Timestamp when the note record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].archived` | `boolean` | Indicates whether the note has been archived |
| `data[].createdAt` | `string` | Timestamp when the note was created |
| `data[].id` | `string` | Unique identifier for the note record |
| `data[].properties` | `object` | Object containing all property values for the note |
| `data[].properties.hs_createdate` | `string` | Date the note was created |
| `data[].properties.hs_lastmodifieddate` | `string` | Last modified date of the note |
| `data[].properties.hs_note_body` | `string` | The body content of the note (supports HTML) |
| `data[].properties.hs_object_id` | `string` | HubSpot object ID |
| `data[].properties.hs_timestamp` | `string` | Timestamp when the note activity occurred |
| `data[].properties.hubspot_owner_id` | `string` | ID of the note owner |
| `data[].updatedAt` | `string` | Timestamp when the note record was last modified |

</details>

## Calls

### Calls List

Returns a paginated list of calls

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "calls",
  "action": "list"
}'
```

#### Python SDK

```python
await hubspot.calls.list()
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
| `limit` | `integer` | No | The maximum number of results to display per page. |
| `after` | `string` | No | The paging cursor token of the last successfully read resource will be returned as the paging.next.after JSON property of a paged response containing more results. |
| `associations` | `string` | No | A comma separated list of associated object types to include in the response. Valid values are contacts, companies, deals, tickets, and custom object type IDs or fully qualified names. |
| `properties` | `string` | No | A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `propertiesWithHistory` | `string` | No | A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `archived` | `boolean` | No | Whether to return only results that have been archived. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `associations` | `object \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string` |  |
| `next_link` | `string` |  |

</details>

### Calls Create

Create a new call engagement in HubSpot CRM. Calls can be associated with contacts,
companies, deals, or tickets by using the associations parameter.
The hs_timestamp property sets when the call activity occurred.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "calls",
  "action": "create",
  "params": {
    "properties": {
      "hs_timestamp": "<str>"
    },
    "associations": []
  }
}'
```

#### Python SDK

```python
await hubspot.calls.create(
    properties={
        "hs_timestamp": "<str>"
    },
    associations=[]
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "calls",
    "action": "create",
    "params": {
        "properties": {
            "hs_timestamp": "<str>"
        },
        "associations": []
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `properties` | `object` | Yes | Call properties to set |
| `properties.hs_call_body` | `string` | No | Description or notes about the call |
| `properties.hs_call_direction` | `string` | No | Direction of the call (INBOUND or OUTBOUND) |
| `properties.hs_call_disposition` | `string` | No | The outcome of the call (e.g., connected, no answer, busy, left voicemail) |
| `properties.hs_call_duration` | `string` | No | Duration of the call in milliseconds |
| `properties.hs_call_from_number` | `string` | No | Phone number the call was made from |
| `properties.hs_call_to_number` | `string` | No | Phone number the call was made to |
| `properties.hs_call_status` | `string` | No | Status of the call (e.g., COMPLETED, BUSY, NO_ANSWER, FAILED, CANCELED) |
| `properties.hs_call_title` | `string` | No | Title or subject of the call |
| `properties.hs_timestamp` | `string` | Yes | Required. Timestamp when the call activity occurred (ISO 8601 format, e.g. 2025-01-15T10:30:00.000Z). Use the current time if the user does not specify one. |
| `properties.hubspot_owner_id` | `string` | No | ID of the HubSpot owner to assign to this call |
| `associations` | `array<object>` | No | Associate the call with other CRM records (contacts, companies, deals, tickets) |
| `associations.to` | `object` | No |  |
| `associations.to.id` | `string` | No | ID of the record to associate with |
| `associations.types` | `array<object>` | No |  |
| `associations.types.associationCategory` | `string` | No | Association category (e.g., HUBSPOT_DEFINED) |
| `associations.types.associationTypeId` | `integer` | No | Association type ID (e.g., 194 for call-to-contact, 182 for call-to-company, 206 for call-to-deal, 220 for call-to-ticket) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `associations` | `object \| null` |  |


</details>

### Calls Get

Get a single call by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "calls",
  "action": "get",
  "params": {
    "callId": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.calls.get(
    call_id="<str>"
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
        "callId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `callId` | `string` | Yes | Call ID |
| `properties` | `string` | No | A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `propertiesWithHistory` | `string` | No | A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `associations` | `string` | No | A comma separated list of object types to retrieve associated IDs for. If any of the specified associations do not exist, they will be ignored. |
| `idProperty` | `string` | No | The name of a property whose values are unique for this object. |
| `archived` | `boolean` | No | Whether to return only results that have been archived. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `associations` | `object \| null` |  |


</details>

### Calls Update

Update an existing call's properties by ID.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "calls",
  "action": "update",
  "params": {
    "properties": {},
    "callId": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.calls.update(
    properties={},
    call_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "calls",
    "action": "update",
    "params": {
        "properties": {},
        "callId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `properties` | `object` | Yes | Call properties to update |
| `properties.hs_call_body` | `string` | No | Description or notes about the call |
| `properties.hs_call_direction` | `string` | No | Direction of the call (INBOUND or OUTBOUND) |
| `properties.hs_call_disposition` | `string` | No | The outcome of the call |
| `properties.hs_call_duration` | `string` | No | Duration of the call in milliseconds |
| `properties.hs_call_from_number` | `string` | No | Phone number the call was made from |
| `properties.hs_call_to_number` | `string` | No | Phone number the call was made to |
| `properties.hs_call_status` | `string` | No | Status of the call (e.g., COMPLETED, BUSY, NO_ANSWER) |
| `properties.hs_call_title` | `string` | No | Title or subject of the call |
| `properties.hs_timestamp` | `string` | No | Timestamp when the call activity occurred |
| `properties.hubspot_owner_id` | `string` | No | ID of the HubSpot owner to assign to this call |
| `callId` | `string` | Yes | Call ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `associations` | `object \| null` |  |


</details>

### Calls Delete

Archive a call by ID. This is a soft delete — the call is moved to the
recycle bin and can be restored for approximately 90 days. No public
hard-delete endpoint exists.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "calls",
  "action": "delete",
  "params": {
    "callId": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.calls.delete(
    call_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "calls",
    "action": "delete",
    "params": {
        "callId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `callId` | `string` | Yes | Call ID |


### Calls Context Store Search

Search and filter calls records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "calls",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "archived": true
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await hubspot.calls.context_store_search(
    query={"filter": {"eq": {"archived": True}}}
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
        "query": {"filter": {"eq": {"archived": True}}}
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
| `archived` | `boolean` | Indicates whether the call has been archived |
| `createdAt` | `string` | Timestamp when the call was created |
| `id` | `string` | Unique identifier for the call record |
| `properties` | `object` | Object containing all property values for the call |
| `properties.hs_call_body` | `string` | Description or notes about the call |
| `properties.hs_call_direction` | `string` | Direction of the call (INBOUND or OUTBOUND) |
| `properties.hs_call_duration` | `string` | Duration of the call in milliseconds |
| `properties.hs_call_status` | `string` | Status of the call (e.g., COMPLETED, BUSY, NO_ANSWER) |
| `properties.hs_call_title` | `string` | Title or subject of the call |
| `properties.hs_createdate` | `string` | Date the call was created |
| `properties.hs_lastmodifieddate` | `string` | Last modified date of the call |
| `properties.hs_object_id` | `string` | HubSpot object ID |
| `properties.hs_timestamp` | `string` | Timestamp when the call activity occurred |
| `properties.hubspot_owner_id` | `string` | ID of the call owner |
| `updatedAt` | `string` | Timestamp when the call record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].archived` | `boolean` | Indicates whether the call has been archived |
| `data[].createdAt` | `string` | Timestamp when the call was created |
| `data[].id` | `string` | Unique identifier for the call record |
| `data[].properties` | `object` | Object containing all property values for the call |
| `data[].properties.hs_call_body` | `string` | Description or notes about the call |
| `data[].properties.hs_call_direction` | `string` | Direction of the call (INBOUND or OUTBOUND) |
| `data[].properties.hs_call_duration` | `string` | Duration of the call in milliseconds |
| `data[].properties.hs_call_status` | `string` | Status of the call (e.g., COMPLETED, BUSY, NO_ANSWER) |
| `data[].properties.hs_call_title` | `string` | Title or subject of the call |
| `data[].properties.hs_createdate` | `string` | Date the call was created |
| `data[].properties.hs_lastmodifieddate` | `string` | Last modified date of the call |
| `data[].properties.hs_object_id` | `string` | HubSpot object ID |
| `data[].properties.hs_timestamp` | `string` | Timestamp when the call activity occurred |
| `data[].properties.hubspot_owner_id` | `string` | ID of the call owner |
| `data[].updatedAt` | `string` | Timestamp when the call record was last modified |

</details>

## Emails

### Emails List

Returns a paginated list of emails

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "emails",
  "action": "list"
}'
```

#### Python SDK

```python
await hubspot.emails.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "emails",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | The maximum number of results to display per page. |
| `after` | `string` | No | The paging cursor token of the last successfully read resource will be returned as the paging.next.after JSON property of a paged response containing more results. |
| `associations` | `string` | No | A comma separated list of associated object types to include in the response. Valid values are contacts, companies, deals, tickets, and custom object type IDs or fully qualified names. |
| `properties` | `string` | No | A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `propertiesWithHistory` | `string` | No | A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `archived` | `boolean` | No | Whether to return only results that have been archived. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `associations` | `object \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string` |  |
| `next_link` | `string` |  |

</details>

### Emails Create

Create a new email engagement in HubSpot CRM. Emails can be associated with contacts,
companies, deals, or tickets by using the associations parameter.
The hs_timestamp property sets when the email activity occurred.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "emails",
  "action": "create",
  "params": {
    "properties": {
      "hs_timestamp": "<str>",
      "hs_email_direction": "<str>"
    },
    "associations": []
  }
}'
```

#### Python SDK

```python
await hubspot.emails.create(
    properties={
        "hs_timestamp": "<str>",
        "hs_email_direction": "<str>"
    },
    associations=[]
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "emails",
    "action": "create",
    "params": {
        "properties": {
            "hs_timestamp": "<str>",
            "hs_email_direction": "<str>"
        },
        "associations": []
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `properties` | `object` | Yes | Email properties to set |
| `properties.hs_email_subject` | `string` | No | Subject line of the email |
| `properties.hs_email_text` | `string` | No | Plain text body of the email |
| `properties.hs_email_html` | `string` | No | HTML body of the email |
| `properties.hs_email_direction` | `string` | Yes | Required. Direction of the email (EMAIL for sent, INCOMING_EMAIL for received, FORWARDED_EMAIL for forwarded) |
| `properties.hs_email_status` | `string` | No | Status of the email (BOUNCED, FAILED, SCHEDULED, SENDING, SENT, DRAFT) |
| `properties.hs_email_sender_email` | `string` | No | Sender email address |
| `properties.hs_email_to_email` | `string` | No | Recipient email address(es) |
| `properties.hs_timestamp` | `string` | Yes | Required. Timestamp when the email activity occurred (ISO 8601 format, e.g. 2025-01-15T10:30:00.000Z). Use the current time if the user does not specify one. |
| `properties.hubspot_owner_id` | `string` | No | ID of the HubSpot owner to assign to this email |
| `associations` | `array<object>` | No | Associate the email with other CRM records (contacts, companies, deals, tickets) |
| `associations.to` | `object` | No |  |
| `associations.to.id` | `string` | No | ID of the record to associate with |
| `associations.types` | `array<object>` | No |  |
| `associations.types.associationCategory` | `string` | No | Association category (e.g., HUBSPOT_DEFINED) |
| `associations.types.associationTypeId` | `integer` | No | Association type ID (e.g., 198 for email-to-contact, 186 for email-to-company, 210 for email-to-deal, 224 for email-to-ticket) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `associations` | `object \| null` |  |


</details>

### Emails Get

Get a single email by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "emails",
  "action": "get",
  "params": {
    "emailId": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.emails.get(
    email_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "emails",
    "action": "get",
    "params": {
        "emailId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `emailId` | `string` | Yes | Email ID |
| `properties` | `string` | No | A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `propertiesWithHistory` | `string` | No | A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `associations` | `string` | No | A comma separated list of object types to retrieve associated IDs for. If any of the specified associations do not exist, they will be ignored. |
| `idProperty` | `string` | No | The name of a property whose values are unique for this object. |
| `archived` | `boolean` | No | Whether to return only results that have been archived. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `associations` | `object \| null` |  |


</details>

### Emails Update

Update an existing email's properties by ID.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "emails",
  "action": "update",
  "params": {
    "properties": {},
    "emailId": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.emails.update(
    properties={},
    email_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "emails",
    "action": "update",
    "params": {
        "properties": {},
        "emailId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `properties` | `object` | Yes | Email properties to update |
| `properties.hs_email_subject` | `string` | No | Subject line of the email |
| `properties.hs_email_text` | `string` | No | Plain text body of the email |
| `properties.hs_email_html` | `string` | No | HTML body of the email |
| `properties.hs_email_direction` | `string` | No | Direction of the email (EMAIL, INCOMING_EMAIL, FORWARDED_EMAIL) |
| `properties.hs_email_status` | `string` | No | Status of the email (BOUNCED, FAILED, SCHEDULED, SENDING, SENT, DRAFT) |
| `properties.hs_timestamp` | `string` | No | Timestamp when the email activity occurred |
| `properties.hubspot_owner_id` | `string` | No | ID of the HubSpot owner to assign to this email |
| `emailId` | `string` | Yes | Email ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `associations` | `object \| null` |  |


</details>

### Emails Delete

Archive an email by ID. This is a soft delete — the email is moved to the
recycle bin and can be restored for approximately 90 days. No public
hard-delete endpoint exists.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "emails",
  "action": "delete",
  "params": {
    "emailId": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.emails.delete(
    email_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "emails",
    "action": "delete",
    "params": {
        "emailId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `emailId` | `string` | Yes | Email ID |


### Emails Context Store Search

Search and filter emails records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "emails",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "archived": true
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await hubspot.emails.context_store_search(
    query={"filter": {"eq": {"archived": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "emails",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"archived": True}}}
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
| `archived` | `boolean` | Indicates whether the email has been archived |
| `createdAt` | `string` | Timestamp when the email was created |
| `id` | `string` | Unique identifier for the email record |
| `properties` | `object` | Object containing all property values for the email |
| `properties.hs_createdate` | `string` | Date the email was created |
| `properties.hs_email_direction` | `string` | Direction of the email (EMAIL, INCOMING_EMAIL, FORWARDED_EMAIL) |
| `properties.hs_email_status` | `string` | Status of the email (BOUNCED, FAILED, SCHEDULED, SENDING, SENT, DRAFT) |
| `properties.hs_email_subject` | `string` | Subject line of the email |
| `properties.hs_email_text` | `string` | Plain text body of the email |
| `properties.hs_lastmodifieddate` | `string` | Last modified date of the email |
| `properties.hs_object_id` | `string` | HubSpot object ID |
| `properties.hs_timestamp` | `string` | Timestamp when the email activity occurred |
| `properties.hubspot_owner_id` | `string` | ID of the email owner |
| `updatedAt` | `string` | Timestamp when the email record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].archived` | `boolean` | Indicates whether the email has been archived |
| `data[].createdAt` | `string` | Timestamp when the email was created |
| `data[].id` | `string` | Unique identifier for the email record |
| `data[].properties` | `object` | Object containing all property values for the email |
| `data[].properties.hs_createdate` | `string` | Date the email was created |
| `data[].properties.hs_email_direction` | `string` | Direction of the email (EMAIL, INCOMING_EMAIL, FORWARDED_EMAIL) |
| `data[].properties.hs_email_status` | `string` | Status of the email (BOUNCED, FAILED, SCHEDULED, SENDING, SENT, DRAFT) |
| `data[].properties.hs_email_subject` | `string` | Subject line of the email |
| `data[].properties.hs_email_text` | `string` | Plain text body of the email |
| `data[].properties.hs_lastmodifieddate` | `string` | Last modified date of the email |
| `data[].properties.hs_object_id` | `string` | HubSpot object ID |
| `data[].properties.hs_timestamp` | `string` | Timestamp when the email activity occurred |
| `data[].properties.hubspot_owner_id` | `string` | ID of the email owner |
| `data[].updatedAt` | `string` | Timestamp when the email record was last modified |

</details>

## Meetings

### Meetings List

Returns a paginated list of meetings

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "meetings",
  "action": "list"
}'
```

#### Python SDK

```python
await hubspot.meetings.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "meetings",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | The maximum number of results to display per page. |
| `after` | `string` | No | The paging cursor token of the last successfully read resource will be returned as the paging.next.after JSON property of a paged response containing more results. |
| `associations` | `string` | No | A comma separated list of associated object types to include in the response. Valid values are contacts, companies, deals, tickets, and custom object type IDs or fully qualified names. |
| `properties` | `string` | No | A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `propertiesWithHistory` | `string` | No | A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `archived` | `boolean` | No | Whether to return only results that have been archived. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `associations` | `object \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string` |  |
| `next_link` | `string` |  |

</details>

### Meetings Create

Create a new meeting engagement in HubSpot CRM. Meetings can be associated with contacts,
companies, deals, or tickets by using the associations parameter.
The hs_timestamp property sets when the meeting activity occurred.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "meetings",
  "action": "create",
  "params": {
    "properties": {
      "hs_timestamp": "<str>",
      "hs_meeting_title": "<str>"
    },
    "associations": []
  }
}'
```

#### Python SDK

```python
await hubspot.meetings.create(
    properties={
        "hs_timestamp": "<str>",
        "hs_meeting_title": "<str>"
    },
    associations=[]
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "meetings",
    "action": "create",
    "params": {
        "properties": {
            "hs_timestamp": "<str>",
            "hs_meeting_title": "<str>"
        },
        "associations": []
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `properties` | `object` | Yes | Meeting properties to set |
| `properties.hs_meeting_title` | `string` | Yes | Required. Title of the meeting |
| `properties.hs_meeting_body` | `string` | No | Description or notes about the meeting (supports HTML) |
| `properties.hs_meeting_start_time` | `string` | No | Start time of the meeting (ISO 8601 format, e.g. 2025-01-15T10:30:00.000Z) |
| `properties.hs_meeting_end_time` | `string` | No | End time of the meeting (ISO 8601 format, e.g. 2025-01-15T11:30:00.000Z) |
| `properties.hs_meeting_location` | `string` | No | Location of the meeting |
| `properties.hs_meeting_outcome` | `string` | No | Outcome of the meeting (e.g., SCHEDULED, COMPLETED, RESCHEDULED, NO_SHOW, CANCELED) |
| `properties.hs_internal_meeting_notes` | `string` | No | Internal notes about the meeting |
| `properties.hs_timestamp` | `string` | Yes | Required. Timestamp when the meeting activity occurred (ISO 8601 format, e.g. 2025-01-15T10:30:00.000Z). Use the current time if the user does not specify one. |
| `properties.hubspot_owner_id` | `string` | No | ID of the HubSpot owner to assign to this meeting |
| `associations` | `array<object>` | No | Associate the meeting with other CRM records (contacts, companies, deals, tickets) |
| `associations.to` | `object` | No |  |
| `associations.to.id` | `string` | No | ID of the record to associate with |
| `associations.types` | `array<object>` | No |  |
| `associations.types.associationCategory` | `string` | No | Association category (e.g., HUBSPOT_DEFINED) |
| `associations.types.associationTypeId` | `integer` | No | Association type ID (e.g., 200 for meeting-to-contact, 188 for meeting-to-company, 212 for meeting-to-deal, 226 for meeting-to-ticket) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `associations` | `object \| null` |  |


</details>

### Meetings Get

Get a single meeting by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "meetings",
  "action": "get",
  "params": {
    "meetingId": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.meetings.get(
    meeting_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "meetings",
    "action": "get",
    "params": {
        "meetingId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `meetingId` | `string` | Yes | Meeting ID |
| `properties` | `string` | No | A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `propertiesWithHistory` | `string` | No | A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `associations` | `string` | No | A comma separated list of object types to retrieve associated IDs for. If any of the specified associations do not exist, they will be ignored. |
| `idProperty` | `string` | No | The name of a property whose values are unique for this object. |
| `archived` | `boolean` | No | Whether to return only results that have been archived. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `associations` | `object \| null` |  |


</details>

### Meetings Update

Update an existing meeting's properties by ID.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "meetings",
  "action": "update",
  "params": {
    "properties": {},
    "meetingId": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.meetings.update(
    properties={},
    meeting_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "meetings",
    "action": "update",
    "params": {
        "properties": {},
        "meetingId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `properties` | `object` | Yes | Meeting properties to update |
| `properties.hs_meeting_title` | `string` | No | Title of the meeting |
| `properties.hs_meeting_body` | `string` | No | Description or notes about the meeting (supports HTML) |
| `properties.hs_meeting_start_time` | `string` | No | Start time of the meeting (ISO 8601 format) |
| `properties.hs_meeting_end_time` | `string` | No | End time of the meeting (ISO 8601 format) |
| `properties.hs_meeting_location` | `string` | No | Location of the meeting |
| `properties.hs_meeting_outcome` | `string` | No | Outcome of the meeting (e.g., SCHEDULED, COMPLETED, RESCHEDULED, NO_SHOW, CANCELED) |
| `properties.hs_internal_meeting_notes` | `string` | No | Internal notes about the meeting |
| `properties.hs_timestamp` | `string` | No | Timestamp when the meeting activity occurred |
| `properties.hubspot_owner_id` | `string` | No | ID of the HubSpot owner to assign to this meeting |
| `meetingId` | `string` | Yes | Meeting ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `associations` | `object \| null` |  |


</details>

### Meetings Delete

Archive a meeting by ID. This is a soft delete — the meeting is moved to the
recycle bin and can be restored for approximately 90 days. No public
hard-delete endpoint exists.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "meetings",
  "action": "delete",
  "params": {
    "meetingId": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.meetings.delete(
    meeting_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "meetings",
    "action": "delete",
    "params": {
        "meetingId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `meetingId` | `string` | Yes | Meeting ID |


### Meetings Context Store Search

Search and filter meetings records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "meetings",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "archived": true
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await hubspot.meetings.context_store_search(
    query={"filter": {"eq": {"archived": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "meetings",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"archived": True}}}
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
| `archived` | `boolean` | Indicates whether the meeting has been archived |
| `createdAt` | `string` | Timestamp when the meeting was created |
| `id` | `string` | Unique identifier for the meeting record |
| `properties` | `object` | Object containing all property values for the meeting |
| `properties.hs_createdate` | `string` | Date the meeting was created |
| `properties.hs_lastmodifieddate` | `string` | Last modified date of the meeting |
| `properties.hs_meeting_body` | `string` | Description or notes about the meeting |
| `properties.hs_meeting_end_time` | `string` | End time of the meeting |
| `properties.hs_meeting_location` | `string` | Location of the meeting |
| `properties.hs_meeting_outcome` | `string` | Outcome of the meeting (e.g., SCHEDULED, COMPLETED, NO_SHOW, CANCELED) |
| `properties.hs_meeting_start_time` | `string` | Start time of the meeting |
| `properties.hs_meeting_title` | `string` | Title of the meeting |
| `properties.hs_object_id` | `string` | HubSpot object ID |
| `properties.hs_timestamp` | `string` | Timestamp when the meeting activity occurred |
| `properties.hubspot_owner_id` | `string` | ID of the meeting owner |
| `updatedAt` | `string` | Timestamp when the meeting record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].archived` | `boolean` | Indicates whether the meeting has been archived |
| `data[].createdAt` | `string` | Timestamp when the meeting was created |
| `data[].id` | `string` | Unique identifier for the meeting record |
| `data[].properties` | `object` | Object containing all property values for the meeting |
| `data[].properties.hs_createdate` | `string` | Date the meeting was created |
| `data[].properties.hs_lastmodifieddate` | `string` | Last modified date of the meeting |
| `data[].properties.hs_meeting_body` | `string` | Description or notes about the meeting |
| `data[].properties.hs_meeting_end_time` | `string` | End time of the meeting |
| `data[].properties.hs_meeting_location` | `string` | Location of the meeting |
| `data[].properties.hs_meeting_outcome` | `string` | Outcome of the meeting (e.g., SCHEDULED, COMPLETED, NO_SHOW, CANCELED) |
| `data[].properties.hs_meeting_start_time` | `string` | Start time of the meeting |
| `data[].properties.hs_meeting_title` | `string` | Title of the meeting |
| `data[].properties.hs_object_id` | `string` | HubSpot object ID |
| `data[].properties.hs_timestamp` | `string` | Timestamp when the meeting activity occurred |
| `data[].properties.hubspot_owner_id` | `string` | ID of the meeting owner |
| `data[].updatedAt` | `string` | Timestamp when the meeting record was last modified |

</details>

## Tasks

### Tasks List

Returns a paginated list of tasks

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "tasks",
  "action": "list"
}'
```

#### Python SDK

```python
await hubspot.tasks.list()
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
| `limit` | `integer` | No | The maximum number of results to display per page. |
| `after` | `string` | No | The paging cursor token of the last successfully read resource will be returned as the paging.next.after JSON property of a paged response containing more results. |
| `associations` | `string` | No | A comma separated list of associated object types to include in the response. Valid values are contacts, companies, deals, tickets, and custom object type IDs or fully qualified names. |
| `properties` | `string` | No | A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `propertiesWithHistory` | `string` | No | A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `archived` | `boolean` | No | Whether to return only results that have been archived. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `associations` | `object \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string` |  |
| `next_link` | `string` |  |

</details>

### Tasks Create

Create a new task in HubSpot CRM. Tasks can be associated with contacts,
companies, deals, or tickets by using the associations parameter.
The hs_timestamp property sets when the task activity occurred.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "tasks",
  "action": "create",
  "params": {
    "properties": {
      "hs_timestamp": "<str>",
      "hs_task_subject": "<str>"
    },
    "associations": []
  }
}'
```

#### Python SDK

```python
await hubspot.tasks.create(
    properties={
        "hs_timestamp": "<str>",
        "hs_task_subject": "<str>"
    },
    associations=[]
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
        "properties": {
            "hs_timestamp": "<str>",
            "hs_task_subject": "<str>"
        },
        "associations": []
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `properties` | `object` | Yes | Task properties to set |
| `properties.hs_task_body` | `string` | No | Description or notes for the task (supports HTML) |
| `properties.hs_task_subject` | `string` | Yes | Required. Subject or title of the task |
| `properties.hs_task_status` | `string` | No | Status of the task (NOT_STARTED, IN_PROGRESS, WAITING, COMPLETED, DEFERRED). Defaults to NOT_STARTED. |
| `properties.hs_task_priority` | `string` | No | Priority of the task (LOW, MEDIUM, HIGH) |
| `properties.hs_task_type` | `string` | No | Type of the task (TODO, CALL, EMAIL). Defaults to TODO. |
| `properties.hs_task_reminders` | `string` | No | Reminder timestamp for the task (epoch milliseconds) |
| `properties.hs_timestamp` | `string` | Yes | Required. Due date / timestamp for the task (ISO 8601 format, e.g. 2025-01-15T10:30:00.000Z). Use the current time if the user does not specify one. |
| `properties.hubspot_owner_id` | `string` | No | ID of the HubSpot owner to assign to this task |
| `associations` | `array<object>` | No | Associate the task with other CRM records (contacts, companies, deals, tickets) |
| `associations.to` | `object` | No |  |
| `associations.to.id` | `string` | No | ID of the record to associate with |
| `associations.types` | `array<object>` | No |  |
| `associations.types.associationCategory` | `string` | No | Association category (e.g., HUBSPOT_DEFINED) |
| `associations.types.associationTypeId` | `integer` | No | Association type ID (e.g., 204 for task-to-contact, 192 for task-to-company, 216 for task-to-deal, 228 for task-to-ticket) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `associations` | `object \| null` |  |


</details>

### Tasks Get

Get a single task by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "tasks",
  "action": "get",
  "params": {
    "taskId": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.tasks.get(
    task_id="<str>"
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
        "taskId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `taskId` | `string` | Yes | Task ID |
| `properties` | `string` | No | A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `propertiesWithHistory` | `string` | No | A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `associations` | `string` | No | A comma separated list of object types to retrieve associated IDs for. If any of the specified associations do not exist, they will be ignored. |
| `idProperty` | `string` | No | The name of a property whose values are unique for this object. |
| `archived` | `boolean` | No | Whether to return only results that have been archived. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `associations` | `object \| null` |  |


</details>

### Tasks Update

Update an existing task's properties by ID.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "tasks",
  "action": "update",
  "params": {
    "properties": {},
    "taskId": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.tasks.update(
    properties={},
    task_id="<str>"
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
        "properties": {},
        "taskId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `properties` | `object` | Yes | Task properties to update |
| `properties.hs_task_body` | `string` | No | Description or notes for the task (supports HTML) |
| `properties.hs_task_subject` | `string` | No | Subject or title of the task |
| `properties.hs_task_status` | `string` | No | Status of the task (NOT_STARTED, IN_PROGRESS, WAITING, COMPLETED, DEFERRED) |
| `properties.hs_task_priority` | `string` | No | Priority of the task (LOW, MEDIUM, HIGH) |
| `properties.hs_task_type` | `string` | No | Type of the task (TODO, CALL, EMAIL) |
| `properties.hs_task_reminders` | `string` | No | Reminder timestamp for the task (epoch milliseconds) |
| `properties.hs_timestamp` | `string` | No | Due date / timestamp for the task |
| `properties.hubspot_owner_id` | `string` | No | ID of the HubSpot owner to assign to this task |
| `taskId` | `string` | Yes | Task ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `associations` | `object \| null` |  |


</details>

### Tasks Delete

Archive a task by ID. This is a soft delete — the task is moved to the
recycle bin and can be restored for approximately 90 days. No public
hard-delete endpoint exists.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "tasks",
  "action": "delete",
  "params": {
    "taskId": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.tasks.delete(
    task_id="<str>"
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
        "taskId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `taskId` | `string` | Yes | Task ID |


### Tasks Context Store Search

Search and filter tasks records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "tasks",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "archived": true
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await hubspot.tasks.context_store_search(
    query={"filter": {"eq": {"archived": True}}}
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
        "query": {"filter": {"eq": {"archived": True}}}
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
| `archived` | `boolean` | Indicates whether the task has been archived |
| `createdAt` | `string` | Timestamp when the task was created |
| `id` | `string` | Unique identifier for the task record |
| `properties` | `object` | Object containing all property values for the task |
| `properties.hs_createdate` | `string` | Date the task was created |
| `properties.hs_lastmodifieddate` | `string` | Last modified date of the task |
| `properties.hs_object_id` | `string` | HubSpot object ID |
| `properties.hs_task_body` | `string` | Description or notes for the task |
| `properties.hs_task_priority` | `string` | Priority of the task (LOW, MEDIUM, HIGH) |
| `properties.hs_task_status` | `string` | Status of the task (NOT_STARTED, IN_PROGRESS, WAITING, COMPLETED, DEFERRED) |
| `properties.hs_task_subject` | `string` | Subject or title of the task |
| `properties.hs_task_type` | `string` | Type of the task (TODO, CALL, EMAIL) |
| `properties.hs_timestamp` | `string` | Due date / timestamp for the task |
| `properties.hubspot_owner_id` | `string` | ID of the task owner |
| `updatedAt` | `string` | Timestamp when the task record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].archived` | `boolean` | Indicates whether the task has been archived |
| `data[].createdAt` | `string` | Timestamp when the task was created |
| `data[].id` | `string` | Unique identifier for the task record |
| `data[].properties` | `object` | Object containing all property values for the task |
| `data[].properties.hs_createdate` | `string` | Date the task was created |
| `data[].properties.hs_lastmodifieddate` | `string` | Last modified date of the task |
| `data[].properties.hs_object_id` | `string` | HubSpot object ID |
| `data[].properties.hs_task_body` | `string` | Description or notes for the task |
| `data[].properties.hs_task_priority` | `string` | Priority of the task (LOW, MEDIUM, HIGH) |
| `data[].properties.hs_task_status` | `string` | Status of the task (NOT_STARTED, IN_PROGRESS, WAITING, COMPLETED, DEFERRED) |
| `data[].properties.hs_task_subject` | `string` | Subject or title of the task |
| `data[].properties.hs_task_type` | `string` | Type of the task (TODO, CALL, EMAIL) |
| `data[].properties.hs_timestamp` | `string` | Due date / timestamp for the task |
| `data[].properties.hubspot_owner_id` | `string` | ID of the task owner |
| `data[].updatedAt` | `string` | Timestamp when the task record was last modified |

</details>

## Schemas

### Schemas List

Returns all custom object schemas to discover available custom objects

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "schemas",
  "action": "list"
}'
```

#### Python SDK

```python
await hubspot.schemas.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "schemas",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `archived` | `boolean` | No | Whether to return only results that have been archived. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `labels` | `object` |  |
| `objectTypeId` | `string` |  |
| `fullyQualifiedName` | `string` |  |
| `requiredProperties` | `array<string>` |  |
| `searchableProperties` | `array<string>` |  |
| `primaryDisplayProperty` | `string` |  |
| `secondaryDisplayProperties` | `array<string>` |  |
| `description` | `string \| null` |  |
| `allowsSensitiveProperties` | `boolean` |  |
| `archived` | `boolean` |  |
| `restorable` | `boolean` |  |
| `metaType` | `string` |  |
| `createdByUserId` | `integer` |  |
| `updatedByUserId` | `integer` |  |
| `properties` | `array<object>` |  |
| `associations` | `array<object>` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |


</details>

### Schemas Get

Get the schema for a specific custom object type

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "schemas",
  "action": "get",
  "params": {
    "objectType": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.schemas.get(
    object_type="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "schemas",
    "action": "get",
    "params": {
        "objectType": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `objectType` | `string` | Yes | Fully qualified name or object type ID of your schema. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `labels` | `object` |  |
| `objectTypeId` | `string` |  |
| `fullyQualifiedName` | `string` |  |
| `requiredProperties` | `array<string>` |  |
| `searchableProperties` | `array<string>` |  |
| `primaryDisplayProperty` | `string` |  |
| `secondaryDisplayProperties` | `array<string>` |  |
| `description` | `string \| null` |  |
| `allowsSensitiveProperties` | `boolean` |  |
| `archived` | `boolean` |  |
| `restorable` | `boolean` |  |
| `metaType` | `string` |  |
| `createdByUserId` | `integer` |  |
| `updatedByUserId` | `integer` |  |
| `properties` | `array<object>` |  |
| `associations` | `array<object>` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |


</details>

## Objects

### Objects List

Read a page of objects. Control what is returned via the properties query param.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "objects",
  "action": "list",
  "params": {
    "objectType": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.objects.list(
    object_type="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "objects",
    "action": "list",
    "params": {
        "objectType": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `objectType` | `string` | Yes | Object type ID or fully qualified name (e.g., "cars" or "p12345_cars") |
| `limit` | `integer` | No | The maximum number of results to display per page. |
| `after` | `string` | No | The paging cursor token of the last successfully read resource will be returned as the `paging.next.after` JSON property of a paged response containing more results. |
| `properties` | `string` | No | A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `archived` | `boolean` | No | Whether to return only results that have been archived. |
| `associations` | `string` | No | A comma separated list of object types to retrieve associated IDs for. If any of the specified associations do not exist, they will be ignored. |
| `propertiesWithHistory` | `string` | No | A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `propertiesWithHistory` | `object \| null` |  |
| `associations` | `object \| null` |  |
| `objectWriteTraceId` | `string \| null` |  |
| `url` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string` |  |
| `next_link` | `string` |  |

</details>

### Objects Get

Read an Object identified by \{objectId\}. \{objectId\} refers to the internal object ID by default, or optionally any unique property value as specified by the idProperty query param. Control what is returned via the properties query param.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
  "entity": "objects",
  "action": "get",
  "params": {
    "objectType": "<str>",
    "objectId": "<str>"
  }
}'
```

#### Python SDK

```python
await hubspot.objects.get(
    object_type="<str>",
    object_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "objects",
    "action": "get",
    "params": {
        "objectType": "<str>",
        "objectId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `objectType` | `string` | Yes | Object type ID or fully qualified name |
| `objectId` | `string` | Yes | Object record ID |
| `properties` | `string` | No | A comma separated list of the properties to be returned in the response. If any of the specified properties are not present on the requested object(s), they will be ignored. |
| `archived` | `boolean` | No | Whether to return only results that have been archived. |
| `associations` | `string` | No | A comma separated list of object types to retrieve associated IDs for. If any of the specified associations do not exist, they will be ignored. |
| `idProperty` | `string` | No | The name of a property whose values are unique for this object. |
| `propertiesWithHistory` | `string` | No | A comma separated list of the properties to be returned along with their history of previous values. If any of the specified properties are not present on the requested object(s), they will be ignored. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `properties` | `object` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |
| `archived` | `boolean` |  |
| `archivedAt` | `string \| null` |  |
| `propertiesWithHistory` | `object \| null` |  |
| `associations` | `object \| null` |  |
| `objectWriteTraceId` | `string \| null` |  |
| `url` | `string \| null` |  |


</details>

