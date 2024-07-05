# Pagination

Given a page size and a pagination strategy, the `DefaultPaginator` will point to pages of results for as long as its strategy returns a `next_page_token`.

Iterating over pages of result is different from iterating over stream slices.
Stream slices have semantic value, for instance, a Datetime stream slice defines data for a specific date range. Two stream slices will have data for different date ranges.
Conversely, pages don't have semantic value. More pages simply means that more records are to be read, without specifying any meaningful difference between the records of the first and later pages.

Schema:

```yaml
Paginator:
  type: object
  anyOf:
    - "$ref": "#/definitions/DefaultPaginator"
    - "$ref": "#/definitions/NoPagination"
NoPagination:
  type: object
  additionalProperties: true
```

## Default paginator

The default paginator is defined by

- `page_size_option`: How to specify the page size in the outgoing HTTP request
- `pagination_strategy`: How to compute the next page to fetch
- `page_token_option`: How to specify the next page to fetch in the outgoing HTTP request

Schema:

```yaml
DefaultPaginator:
  type: object
  additionalProperties: true
  required:
    - page_token_option
    - pagination_strategy
  properties:
    "$parameters":
      "$ref": "#/definitions/$parameters"
    page_size:
      type: integer
    page_size_option:
      "$ref": "#/definitions/RequestOption"
    page_token_option:
      anyOf:
        - "$ref": "#/definitions/RequestOption"
        - "$ref": "#/definitions/RequestPath"
    pagination_strategy:
      "$ref": "#/definitions/PaginationStrategy"
```

3 pagination strategies are supported

1. Page increment
2. Offset increment
3. Cursor-based

## Pagination Strategies

Schema:

```yaml
PaginationStrategy:
  type: object
  anyOf:
    - "$ref": "#/definitions/CursorPagination"
    - "$ref": "#/definitions/OffsetIncrement"
    - "$ref": "#/definitions/PageIncrement"
```

### Page increment

When using the `PageIncrement` strategy, the page number will be set as part of the `page_token_option`.

Schema:

```yaml
PageIncrement:
  type: object
  additionalProperties: true
  required:
    - page_size
  properties:
    "$parameters":
      "$ref": "#/definitions/$parameters"
    page_size:
      type: integer
```

The following paginator example will fetch 5 records per page, and specify the page number as a request_parameter:

Example:

```yaml
paginator:
  type: "DefaultPaginator"
  page_size_option:
    type: "RequestOption"
    inject_into: "request_parameter"
    field_name: "page_size"
  pagination_strategy:
    type: "PageIncrement"
    page_size: 5
  page_token_option:
    type: "RequestOption"
    inject_into: "request_parameter"
    field_name: "page"
```

If the page contains less than 5 records, then the paginator knows there are no more pages to fetch.
If the API returns more records than requested, all records will be processed.

Assuming the endpoint to fetch data from is `https://cloud.airbyte.com/api/get_data`,
the first request will be sent as `https://cloud.airbyte.com/api/get_data?page_size=5&page=0`
and the second request as `https://cloud.airbyte.com/api/get_data?page_size=5&page=1`,

### Offset increment

When using the `OffsetIncrement` strategy, the number of records read will be set as part of the `page_token_option`.

Schema:

```yaml
OffsetIncrement:
  type: object
  additionalProperties: true
  required:
    - page_size
  properties:
    "$parameters":
      "$ref": "#/definitions/$parameters"
    page_size:
      type: integer
```

The following paginator example will fetch 5 records per page, and specify the offset as a request_parameter:

Example:

```yaml
paginator:
  type: "DefaultPaginator"
  page_size_option:
    type: "RequestOption"
    inject_into: "request_parameter"
    field_name: "page_size"
  pagination_strategy:
    type: "OffsetIncrement"
    page_size: 5
  page_token_option:
    type: "RequestOption"
    field_name: "offset"
    inject_into: "request_parameter"
```

Assuming the endpoint to fetch data from is `https://cloud.airbyte.com/api/get_data`,
the first request will be sent as `https://cloud.airbyte.com/api/get_data?page_size=5&offset=0`
and the second request as `https://cloud.airbyte.com/api/get_data?page_size=5&offset=5`,

### Cursor

The `CursorPagination` outputs a token by evaluating its `cursor_value` string with the following parameters:

- `response`: The decoded response
- `headers`: HTTP headers on the response
- `last_records`: List of records selected from the last response

This cursor value can be used to request the next page of record.

Schema:

```yaml
CursorPagination:
  type: object
  additionalProperties: true
  required:
    - cursor_value
  properties:
    "$parameters":
      "$ref": "#/definitions/$parameters"
    cursor_value:
      type: string
    stop_condition:
      type: string
    page_size:
      type: integer
```

#### Cursor paginator in request parameters

In this example, the next page of record is defined by setting the `from` request parameter to the id of the last record read:

```yaml
paginator:
  type: "DefaultPaginator"
  <...>
  pagination_strategy:
    type: "CursorPagination"
    cursor_value: "{{ last_records[-1]['id'] }}"
  page_token_option:
    type: "RequestPath"
    field_name: "from"
    inject_into: "request_parameter"
```

Assuming the endpoint to fetch data from is `https://cloud.airbyte.com/api/get_data`,
the first request will be sent as `https://cloud.airbyte.com/api/get_data`.
Assuming the id of the last record fetched is 1000,
the next request will be sent as `https://cloud.airbyte.com/api/get_data?from=1000`.

#### Cursor paginator in path

Some APIs directly point to the URL of the next page to fetch. In this example, the URL of the next page is extracted from the response headers:

```yaml
paginator:
  type: "DefaultPaginator"
  <...>
  pagination_strategy:
    type: "CursorPagination"
    cursor_value: "{{ headers['link']['next']['url'] }}"
  page_token_option:
    type: "RequestPath"
```

Assuming the endpoint to fetch data from is `https://cloud.airbyte.com/api/get_data`,
the first request will be sent as `https://cloud.airbyte.com/api/get_data`
Assuming the response's next url is `https://cloud.airbyte.com/api/get_data?page=1&page_size=100`,
the next request will be sent as `https://cloud.airbyte.com/api/get_data?page=1&page_size=100`
