# Hubspot full reference

This is the full reference documentation for the Hubspot agent connector.

## Supported entities and actions

The Hubspot connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Contacts | [List](#contacts-list), [Get](#contacts-get), [API Search](#contacts-api-search), [Search](#contacts-search) |
| Companies | [List](#companies-list), [Get](#companies-get), [API Search](#companies-api-search), [Search](#companies-search) |
| Deals | [List](#deals-list), [Get](#deals-get), [API Search](#deals-api-search), [Search](#deals-search) |
| Tickets | [List](#tickets-list), [Get](#tickets-get), [API Search](#tickets-api-search) |
| Schemas | [List](#schemas-list), [Get](#schemas-get) |
| Objects | [List](#objects-list), [Get](#objects-get) |

## Contacts

### Contacts List

Returns a paginated list of contacts

#### Python SDK

```python
await hubspot.contacts.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Contacts Get

Get a single contact by ID

#### Python SDK

```python
await hubspot.contacts.get(
    contact_id="<str>"
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

### Contacts API Search

Search for contacts by filtering on properties, searching through associations, and sorting results.

#### Python SDK

```python
await hubspot.contacts.api_search()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Contacts Search

Search and filter contacts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await hubspot.contacts.search(
    query={"filter": {"eq": {"archived": True}}}
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
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `archived` | `boolean` | Boolean flag indicating whether the contact has been archived or deleted. |
| `companies` | `array` | Associated company records linked to this contact. |
| `createdAt` | `string` | Timestamp indicating when the contact was first created in the system. |
| `id` | `string` | Unique identifier for the contact record. |
| `properties` | `object` | Key-value object storing all contact properties and their values. |
| `updatedAt` | `string` | Timestamp indicating when the contact record was last modified. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.archived` | `boolean` | Boolean flag indicating whether the contact has been archived or deleted. |
| `hits[].data.companies` | `array` | Associated company records linked to this contact. |
| `hits[].data.createdAt` | `string` | Timestamp indicating when the contact was first created in the system. |
| `hits[].data.id` | `string` | Unique identifier for the contact record. |
| `hits[].data.properties` | `object` | Key-value object storing all contact properties and their values. |
| `hits[].data.updatedAt` | `string` | Timestamp indicating when the contact record was last modified. |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Companies

### Companies List

Retrieve all companies, using query parameters to control the information that gets returned.

#### Python SDK

```python
await hubspot.companies.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Companies Get

Get a single company by ID

#### Python SDK

```python
await hubspot.companies.get(
    company_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Companies API Search

Search for companies by filtering on properties, searching through associations, and sorting results.

#### Python SDK

```python
await hubspot.companies.api_search()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Companies Search

Search and filter companies records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await hubspot.companies.search(
    query={"filter": {"eq": {"archived": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "companies",
    "action": "search",
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
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `archived` | `boolean` | Indicates whether the company has been deleted and moved to the recycling bin |
| `contacts` | `array` | Associated contact records linked to this company |
| `createdAt` | `string` | Timestamp when the company record was created |
| `id` | `string` | Unique identifier for the company record |
| `properties` | `object` | Object containing all property values for the company |
| `updatedAt` | `string` | Timestamp when the company record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.archived` | `boolean` | Indicates whether the company has been deleted and moved to the recycling bin |
| `hits[].data.contacts` | `array` | Associated contact records linked to this company |
| `hits[].data.createdAt` | `string` | Timestamp when the company record was created |
| `hits[].data.id` | `string` | Unique identifier for the company record |
| `hits[].data.properties` | `object` | Object containing all property values for the company |
| `hits[].data.updatedAt` | `string` | Timestamp when the company record was last modified |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Deals

### Deals List

Returns a paginated list of deals

#### Python SDK

```python
await hubspot.deals.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Deals Get

Get a single deal by ID

#### Python SDK

```python
await hubspot.deals.get(
    deal_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Deals API Search

Search deals with filters and sorting

#### Python SDK

```python
await hubspot.deals.api_search()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Deals Search

Search and filter deals records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await hubspot.deals.search(
    query={"filter": {"eq": {"archived": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "deals",
    "action": "search",
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
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
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
| `updatedAt` | `string` | Timestamp when the deal record was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.archived` | `boolean` | Indicates whether the deal has been deleted and moved to the recycling bin |
| `hits[].data.companies` | `array` | Collection of company records associated with the deal |
| `hits[].data.contacts` | `array` | Collection of contact records associated with the deal |
| `hits[].data.createdAt` | `string` | Timestamp when the deal record was originally created |
| `hits[].data.id` | `string` | Unique identifier for the deal record |
| `hits[].data.line_items` | `array` | Collection of product line items associated with the deal |
| `hits[].data.properties` | `object` | Key-value object containing all deal properties and custom fields |
| `hits[].data.updatedAt` | `string` | Timestamp when the deal record was last modified |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Tickets

### Tickets List

Returns a paginated list of tickets

#### Python SDK

```python
await hubspot.tickets.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Tickets Get

Get a single ticket by ID

#### Python SDK

```python
await hubspot.tickets.get(
    ticket_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Tickets API Search

Search for tickets by filtering on properties, searching through associations, and sorting results.

#### Python SDK

```python
await hubspot.tickets.api_search()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

## Schemas

### Schemas List

Returns all custom object schemas to discover available custom objects

#### Python SDK

```python
await hubspot.schemas.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

#### Python SDK

```python
await hubspot.schemas.get(
    object_type="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

#### Python SDK

```python
await hubspot.objects.list(
    object_type="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

#### Python SDK

```python
await hubspot.objects.get(
    object_type="<str>",
    object_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

