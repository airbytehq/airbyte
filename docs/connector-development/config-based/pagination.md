# Pagination

Given a page size and a pagination strategy, the `LimitPaginator` will point to pages of results for as long as its strategy returns a `next_page_token`.

Iterating over pages of result is different from iterating over stream slices.
Stream slices have semantic value, for instance, a Datetime stream slice defines data for a specific date range. Two stream slices will have data for different date ranges.
Conversely, pages don't have semantic value. More pages simply means that more records are to be read, without specifying any meaningful difference between the records of the first and later pages.

The paginator is defined by

- `page_size`: The number of records to fetch in a single request
- `limit_option`: How to specify the page size in the outgoing HTTP request
- `pagination_strategy`: How to compute the next page to fetch
- `page_token_option`: How to specify the next page to fetch in the outgoing HTTP request

3 pagination strategies are supported

1. Page increment
2. Offset increment
3. Cursor-based

## Pagination Strategies

### Page increment

When using the `PageIncrement` strategy, the page number will be set as part of the `page_token_option`.

The following paginator example will fetch 5 records per page, and specify the page number as a request_parameter:

```yaml
paginator:
  type: "LimitPaginator"
  page_size: 5
  limit_option:
    option_type: request_parameter
    field_name: page_size
  pagination_strategy:
    type: "PageIncrement"
  page_token:
    option_type: "request_parameter"
    field_name: "page"
```

If the page contains less than 5 records, then the paginator knows there are no more pages to fetch.
If the API returns more records than requested, all records will be processed.

Assuming the endpoint to fetch data from is `https://cloud.airbyte.com/api/get_data`,
the first request will be sent as `https://cloud.airbyte.com/api/get_data?page_size=5&page=0`
and the second request as `https://cloud.airbyte.com/api/get_data?page_size=5&page=1`,

### Offset increment

When using the `OffsetIncrement` strategy, the number of records read will be set as part of the `page_token_option`.

The following paginator example will fetch 5 records per page, and specify the offset as a request_parameter:

```yaml
paginator:
  type: "LimitPaginator"
  page_size: 5
  limit_option:
    option_type: request_parameter
    field_name: page_size
  pagination_strategy:
    type: "OffsetIncrement"
  page_token:
    field_name: "offset"
    inject_into: "request_parameter"

```

Assuming the endpoint to fetch data from is `https://cloud.airbyte.com/api/get_data`,
the first request will be sent as `https://cloud.airbyte.com/api/get_data?page_size=5&offset=0`
and the second request as `https://cloud.airbyte.com/api/get_data?page_size=5&offset=5`,

### Cursor

The `CursorPaginationStrategy` outputs a token by evaluating its `cursor_value` string with the following parameters:

- `response`: The decoded response
- `headers`: HTTP headers on the response
- `last_records`: List of records selected from the last response

This cursor value can be used to request the next page of record.

#### Cursor paginator in request parameters

In this example, the next page of record is defined by setting the `from` request parameter to the id of the last record read:

```yaml
paginator:
  type: "LimitPaginator"
  <...>
  pagination_strategy:
    type: "CursorPaginationStrategy"
    cursor_value: "{{ last_records[-1]['id'] }}"
  page_token:
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
  type: "LimitPaginator"
  <...>
  pagination_strategy:
    type: "CursorPaginationStrategy"
    cursor_value: "{{ headers['urls']['next'] }}"
  page_token:
    inject_into: "path"
```

Assuming the endpoint to fetch data from is `https://cloud.airbyte.com/api/get_data`,
the first request will be sent as `https://cloud.airbyte.com/api/get_data`

Assuming the response's next url is `https://cloud.airbyte.com/api/get_data?page=1&page_size=100`,
the next request will be sent as `https://cloud.airbyte.com/api/get_data?page=1&page_size=100`