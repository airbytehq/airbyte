# Hubspot

## Supported Entities and Actions

| Entity | Actions |
|--------|---------|
| Contacts | [List](#contacts-list), [Get](#contacts-get), [Search](#contacts-search) |
| Companies | [List](#companies-list), [Get](#companies-get), [Search](#companies-search) |
| Deals | [List](#deals-list), [Get](#deals-get), [Search](#deals-search) |
| Tickets | [List](#tickets-list), [Get](#tickets-get), [Search](#tickets-search) |
| Schemas | [List](#schemas-list), [Get](#schemas-get) |
| Objects | [List](#objects-list), [Get](#objects-get) |

### Contacts

#### Contacts List

Returns a paginated list of contacts

**Python SDK**

```python
hubspot.contacts.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contacts",
    "action": "list"
}'
```


**Params**

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

**Records**

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


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string` |  |
| `next_link` | `string` |  |

</details>

#### Contacts Get

Get a single contact by ID

**Python SDK**

```python
hubspot.contacts.get(
    contact_id="<str>"
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
        "contactId": "<str>"
    }
}'
```


**Params**

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

**Records**

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

#### Contacts Search

Search for contacts by filtering on properties, searching through associations, and sorting results.

**Python SDK**

```python
hubspot.contacts.search()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contacts",
    "action": "search"
}'
```


**Params**

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

**Records**

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


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `total` | `integer` |  |
| `next_cursor` | `string` |  |
| `next_link` | `string` |  |

</details>

### Companies

#### Companies List

Retrieve all companies, using query parameters to control the information that gets returned.

**Python SDK**

```python
hubspot.companies.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "companies",
    "action": "list"
}'
```


**Params**

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

**Records**

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


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string` |  |
| `next_link` | `string` |  |

</details>

#### Companies Get

Get a single company by ID

**Python SDK**

```python
hubspot.companies.get(
    company_id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

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

**Records**

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

#### Companies Search

Search for companies by filtering on properties, searching through associations, and sorting results.

**Python SDK**

```python
hubspot.companies.search()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "companies",
    "action": "search"
}'
```


**Params**

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

**Records**

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


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `total` | `integer` |  |
| `next_cursor` | `string` |  |
| `next_link` | `string` |  |

</details>

### Deals

#### Deals List

Returns a paginated list of deals

**Python SDK**

```python
hubspot.deals.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "deals",
    "action": "list"
}'
```


**Params**

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

**Records**

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


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string` |  |
| `next_link` | `string` |  |

</details>

#### Deals Get

Get a single deal by ID

**Python SDK**

```python
hubspot.deals.get(
    deal_id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

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

**Records**

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

#### Deals Search

Search deals with filters and sorting

**Python SDK**

```python
hubspot.deals.search()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "deals",
    "action": "search"
}'
```


**Params**

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

**Records**

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


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `total` | `integer` |  |
| `next_cursor` | `string` |  |
| `next_link` | `string` |  |

</details>

### Tickets

#### Tickets List

Returns a paginated list of tickets

**Python SDK**

```python
hubspot.tickets.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tickets",
    "action": "list"
}'
```


**Params**

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

**Records**

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


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string` |  |
| `next_link` | `string` |  |

</details>

#### Tickets Get

Get a single ticket by ID

**Python SDK**

```python
hubspot.tickets.get(
    ticket_id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

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

**Records**

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

#### Tickets Search

Search for tickets by filtering on properties, searching through associations, and sorting results.

**Python SDK**

```python
hubspot.tickets.search()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tickets",
    "action": "search"
}'
```


**Params**

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

**Records**

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


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `total` | `integer` |  |
| `next_cursor` | `string` |  |
| `next_link` | `string` |  |

</details>

### Schemas

#### Schemas List

Returns all custom object schemas to discover available custom objects

**Python SDK**

```python
hubspot.schemas.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "schemas",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `archived` | `boolean` | No | Whether to return only results that have been archived. |


<details>
<summary><b>Response Schema</b></summary>

**Records**

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

#### Schemas Get

Get the schema for a specific custom object type

**Python SDK**

```python
hubspot.schemas.get(
    object_type="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `objectType` | `string` | Yes | Fully qualified name or object type ID of your schema. |


<details>
<summary><b>Response Schema</b></summary>

**Records**

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

### Objects

#### Objects List

Read a page of objects. Control what is returned via the properties query param.

**Python SDK**

```python
hubspot.objects.list(
    object_type="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

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

**Records**

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


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string` |  |
| `next_link` | `string` |  |

</details>

#### Objects Get

Read an Object identified by {objectId}. {objectId} refers to the internal object ID by default, or optionally any unique property value as specified by the idProperty query param. Control what is returned via the properties query param.

**Python SDK**

```python
hubspot.objects.get(
    object_type="<str>",
    object_id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

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

**Records**

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



## Authentication

The Hubspot connector supports the following authentication methods:


### OAuth2 Authentication

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `client_id` | `str` | Yes | Your HubSpot OAuth2 Client ID |
| `client_secret` | `str` | Yes | Your HubSpot OAuth2 Client Secret |
| `refresh_token` | `str` | Yes | Your HubSpot OAuth2 Refresh Token |
| `access_token` | `str` | Yes | Your HubSpot OAuth2 Access Token (optional if refresh_token is provided) |

#### Example

**Python SDK**

```python
HubspotConnector(
  auth_config=HubspotAuthConfig(
    client_id="<Your HubSpot OAuth2 Client ID>",
    client_secret="<Your HubSpot OAuth2 Client Secret>",
    refresh_token="<Your HubSpot OAuth2 Refresh Token>",
    access_token="<Your HubSpot OAuth2 Access Token (optional if refresh_token is provided)>"
  )
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
  "connector_definition_id": "36c891d9-4bd9-43ac-bad2-10e12756272c",
  "auth_config": {
    "client_id": "<Your HubSpot OAuth2 Client ID>",
    "client_secret": "<Your HubSpot OAuth2 Client Secret>",
    "refresh_token": "<Your HubSpot OAuth2 Refresh Token>",
    "access_token": "<Your HubSpot OAuth2 Access Token (optional if refresh_token is provided)>"
  },
  "name": "My Hubspot Connector"
}'
```

